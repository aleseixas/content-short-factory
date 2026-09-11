from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
import json
import math
from pathlib import Path
import re
import unicodedata


@dataclass(frozen=True)
class ContentRequest:
    """Editorial input for one short, independent from the rendering engine."""

    topic: str | None = None
    content_profile: str | None = None
    category: str | None = None
    angle: str | None = None
    target_duration: float | None = None
    language: str | None = None
    additional_instructions: str | None = None
    entities: tuple[str, ...] = ()
    events: tuple[str, ...] = ()
    locations: tuple[str, ...] = ()
    time_period: str | None = None
    visual_keywords: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for field_name in (
            "topic",
            "content_profile",
            "category",
            "angle",
            "language",
            "additional_instructions",
            "time_period",
        ):
            object.__setattr__(
                self, field_name, _optional_text(getattr(self, field_name))
            )

        for field_name in ("entities", "events", "locations", "visual_keywords"):
            object.__setattr__(
                self,
                field_name,
                _text_tuple(getattr(self, field_name), field_name),
            )

        if self.topic is None and self.content_profile is None:
            raise ValueError("Informe ao menos 'topic' ou 'content_profile'.")

        if self.target_duration is not None:
            if isinstance(self.target_duration, bool):
                raise ValueError(
                    "target_duration precisa ser um numero positivo e finito."
                )
            try:
                target_duration = float(self.target_duration)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    "target_duration precisa ser um numero positivo e finito."
                ) from exc
            if not math.isfinite(target_duration) or target_duration <= 0:
                raise ValueError(
                    "target_duration precisa ser um numero positivo e finito."
                )
            object.__setattr__(self, "target_duration", target_duration)

    @classmethod
    def from_mapping(cls, data: Mapping[str, object]) -> ContentRequest:
        """Build a request from the public JSON-shaped editorial contract."""

        if not isinstance(data, Mapping):
            raise ValueError("A solicitacao de conteudo precisa ser um objeto.")
        supported = {
            "topic",
            "content_profile",
            "category",
            "angle",
            "target_duration",
            "language",
            "additional_instructions",
            "entities",
            "events",
            "locations",
            "time_period",
            "visual_keywords",
        }
        unknown = set(data).difference(supported)
        if unknown:
            raise ValueError(
                "Campos editoriais desconhecidos: " + ", ".join(sorted(unknown))
            )
        return cls(**dict(data))  # type: ignore[arg-type]


TopicSelector = Callable[[ContentRequest, tuple[str, ...]], str]


def load_content_request(path: Path) -> ContentRequest:
    """Load the public editorial input contract from a JSON object."""

    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"Arquivo editorial ausente: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"JSON editorial invalido em {path} "
            f"(linha {exc.lineno}, coluna {exc.colno}): {exc.msg}"
        ) from exc
    except OSError as exc:
        raise RuntimeError(f"Nao foi possivel ler {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("A solicitacao de conteudo precisa ser um objeto JSON.")
    return ContentRequest.from_mapping(data)


def resolve_content_request(
    request: ContentRequest,
    topic_history: Iterable[str] = (),
    selector: TopicSelector | None = None,
) -> ContentRequest:
    """Resolve profile-only input through an injected, side-effect-free boundary."""

    if request.topic is not None:
        return request
    if selector is None:
        raise RuntimeError(
            "content_profile sem topic exige um seletor externo; "
            "resolva o topico antes de criar o episodio."
        )

    history = _text_tuple(topic_history, "topic_history")
    selected = selector(request, history)
    if not isinstance(selected, str) or not selected.strip():
        raise RuntimeError("O seletor externo nao retornou um topic valido.")
    return replace(request, topic=selected.strip())


def load_topic_history(
    project_root: Path,
    episodes_dir: str = "episodes",
    *,
    exclude_slug: str | None = None,
) -> tuple[str, ...]:
    """Read canonical topics, with title fallback for schema-v1 stories."""

    root = project_root.resolve()
    episodes_root = (root / episodes_dir).resolve()
    try:
        episodes_root.relative_to(root)
    except ValueError as exc:
        raise RuntimeError(
            f"Pasta de episodios fora do projeto: {episodes_root}"
        ) from exc
    if not episodes_root.is_dir():
        return ()

    excluded = str(exclude_slug or "").strip().casefold()
    topics: list[str] = []
    seen: set[str] = set()
    for episode_dir in sorted(
        path for path in episodes_root.iterdir() if path.is_dir()
    ):
        if excluded and episode_dir.name.casefold() == excluded:
            continue
        story_path = episode_dir / "story.json"
        try:
            data = json.loads(story_path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            continue
        if not isinstance(data, dict):
            continue
        raw_topic = data.get("topic")
        raw_title = data.get("title")
        topic = raw_topic.strip() if isinstance(raw_topic, str) else ""
        if not topic:
            topic = raw_title.strip() if isinstance(raw_title, str) else ""
        if not topic:
            continue
        key = normalize_topic(topic)
        if key and key not in seen:
            topics.append(topic)
            seen.add(key)
    return tuple(topics)


def normalize_topic(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", str(value or ""))
    ascii_like = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return " ".join(re.findall(r"[a-z0-9]+", ascii_like.casefold()))


def slugify_topic(topic: str, *, max_length: int = 96) -> str:
    """Create a stable ASCII slug while preserving Portuguese word boundaries."""

    if max_length < 1:
        raise ValueError("max_length precisa ser positivo.")
    slug = normalize_topic(topic).replace(" ", "_")
    slug = slug[:max_length].rstrip("_")
    if not slug:
        raise ValueError("Nao foi possivel derivar um slug do topic informado.")
    return slug


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("Campos editoriais de texto precisam ser strings.")
    normalized = value.strip()
    return normalized or None


def _text_tuple(values: object, label: str) -> tuple[str, ...]:
    if values is None:
        return ()
    if isinstance(values, (str, bytes, Mapping)) or not isinstance(
        values, (Sequence, Iterable)
    ):
        raise ValueError(f"{label} precisa ser uma sequencia de strings.")
    result: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label} precisa conter somente strings nao vazias.")
        normalized = value.strip()
        if normalized not in result:
            result.append(normalized)
    return tuple(result)
