from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
import json
from pathlib import Path
import re
import unicodedata


DUPLICATE_CODE = "DUPLICATE_CANDIDATE"

_TOPIC_FILLER_WORDS = frozenset(
    {
        "a",
        "ao",
        "aos",
        "as",
        "como",
        "da",
        "das",
        "de",
        "do",
        "dos",
        "dia",
        "e",
        "em",
        "entre",
        "foi",
        "historia",
        "na",
        "nao",
        "nas",
        "no",
        "nos",
        "o",
        "os",
        "para",
        "pela",
        "pelas",
        "pelo",
        "pelos",
        "por",
        "porque",
        "que",
        "quando",
        "um",
        "uma",
        "the",
        "a",
        "an",
        "and",
        "of",
        "to",
        "in",
        "on",
        "for",
        "why",
        "how",
        "when",
    }
)
_TOPIC_EQUIVALENTS = {
    "adquirir": "comprar",
    "adquiriu": "comprar",
    "aquisicao": "comprar",
    "compra": "comprar",
    "comprado": "comprar",
    "comprou": "comprar",
    "negou": "recusar",
    "recusa": "recusar",
    "recusada": "recusar",
    "recusado": "recusar",
    "recusou": "recusar",
    "rejeicao": "recusar",
    "rejeitada": "recusar",
    "rejeitado": "recusar",
    "rejeitou": "recusar",
}


@dataclass(frozen=True)
class DuplicateMatch:
    kind: str
    path: str
    slug: str
    reason: str


def normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", str(value or ""))
    ascii_like = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return " ".join(re.findall(r"[a-z0-9]+", ascii_like.casefold()))


def _story_payload(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _story_corpus(path: Path, slug: str) -> str:
    data = _story_payload(path)
    title = str(data.get("title") or "")
    segments = data.get("segments")
    first_text = ""
    if isinstance(segments, list) and segments and isinstance(segments[0], dict):
        first_text = str(segments[0].get("text") or "")
    return normalize_text(f"{slug} {title} {first_text}")


def infer_identity_from_story(path: Path) -> tuple[str, str]:
    data = _story_payload(path)
    # Topic-driven stories may legitimately use a dash in a generic title. Only
    # apply the old Artist — Song heuristic to legacy stories with no topic.
    topic = data.get("topic")
    if isinstance(topic, str) and topic.strip():
        return "", ""
    title = str(data.get("title") or "").strip()
    if title:
        parts = re.split(r"\s+[—–-]\s+", title, maxsplit=1)
        if len(parts) == 2:
            left, right = parts
            right = re.split(r"[:|]", right, maxsplit=1)[0]
            if left.strip() and right.strip():
                # Most current episodes use "Artist — Song: framing".
                return right.strip(), left.strip()

    segments = data.get("segments")
    if isinstance(segments, list) and segments and isinstance(segments[0], dict):
        text = str(segments[0].get("text") or "").strip()
        match = re.match(
            r"^(.+?),\s+(?:de|da|do)\s+(.+?)(?:,|\.|:|;|\s+nao\b|\s+não\b)",
            text,
            flags=re.IGNORECASE,
        )
        if match:
            return match.group(1).strip(), match.group(2).strip()
    return "", ""


def infer_topic_from_story(path: Path) -> str:
    """Return the canonical topic, with title fallback for legacy stories."""

    data = _story_payload(path)
    topic = data.get("topic")
    if isinstance(topic, str) and topic.strip():
        return topic.strip()
    title = data.get("title")
    return title.strip() if isinstance(title, str) else ""


def _slug_from_retry_name(stem: str) -> str:
    return re.sub(r"-retry-\d+$", "", stem)


def _canonical_topic_tokens(value: str) -> tuple[str, ...]:
    tokens: list[str] = []
    raw_tokens = normalize_text(value).split()
    index = 0
    while index < len(raw_tokens):
        token = raw_tokens[index]
        if (
            token == "disse"
            and index + 1 < len(raw_tokens)
            and raw_tokens[index + 1] == "nao"
        ):
            token = "recusar"
            index += 1
        if token in _TOPIC_FILLER_WORDS:
            index += 1
            continue
        canonical = _TOPIC_EQUIVALENTS.get(token, token)
        if canonical not in tokens:
            tokens.append(canonical)
        index += 1
    return tuple(tokens)


def _topics_are_obvious_paraphrases(left: str, right: str) -> bool:
    left_tokens = _canonical_topic_tokens(left)
    right_tokens = _canonical_topic_tokens(right)
    if len(left_tokens) < 2 or len(right_tokens) < 2:
        return False

    left_set = set(left_tokens)
    right_set = set(right_tokens)
    shared = left_set.intersection(right_set)
    overlap = len(shared) / min(len(left_set), len(right_set))
    if len(shared) < 2 or overlap < 0.8:
        return False

    ordered_similarity = SequenceMatcher(
        None,
        " ".join(left_tokens),
        " ".join(right_tokens),
    ).ratio()
    return left_set == right_set or ordered_similarity >= 0.62


def find_duplicate_candidate(
    project_root: Path,
    *,
    topic: str = "",
    slug: str = "",
    song: str = "",
    artist: str = "",
    exclude_slug: str | None = None,
) -> DuplicateMatch | None:
    root = project_root.resolve()
    candidate_slug = normalize_text(slug)
    topic_value = str(topic or "").strip()
    topic_norm = normalize_text(topic_value)
    song_norm = normalize_text(song)
    artist_norm = normalize_text(artist)
    exclude_norm = normalize_text(exclude_slug or "")

    episodes_root = root / "episodes"
    if episodes_root.is_dir():
        for episode_dir in sorted(
            path for path in episodes_root.iterdir() if path.is_dir()
        ):
            existing_slug = episode_dir.name
            existing_norm = normalize_text(existing_slug)
            if exclude_norm and existing_norm == exclude_norm:
                continue
            if candidate_slug and existing_norm == candidate_slug:
                return DuplicateMatch(
                    "episode",
                    f"episodes/{existing_slug}",
                    existing_slug,
                    "exact_slug",
                )

            story_path = episode_dir / "story.json"
            if not story_path.is_file():
                continue
            existing_topic = infer_topic_from_story(story_path)
            existing_topic_norm = normalize_text(existing_topic)
            if topic_norm and existing_topic_norm == topic_norm:
                return DuplicateMatch(
                    "episode",
                    f"episodes/{existing_slug}",
                    existing_slug,
                    "same_topic",
                )
            if topic_norm and _topics_are_obvious_paraphrases(
                topic_value, existing_topic
            ):
                return DuplicateMatch(
                    "episode",
                    f"episodes/{existing_slug}",
                    existing_slug,
                    "semantically_similar_topic",
                )

            existing_song, existing_artist = infer_identity_from_story(story_path)
            if (
                song_norm
                and artist_norm
                and normalize_text(existing_song) == song_norm
                and normalize_text(existing_artist) == artist_norm
            ):
                return DuplicateMatch(
                    "episode",
                    f"episodes/{existing_slug}",
                    existing_slug,
                    "same_song_and_artist",
                )

            corpus = _story_corpus(story_path, existing_slug)
            if (
                song_norm
                and artist_norm
                and song_norm in corpus
                and artist_norm in corpus
            ):
                return DuplicateMatch(
                    "episode",
                    f"episodes/{existing_slug}",
                    existing_slug,
                    "song_and_artist_present_in_story",
                )

    for directory_name, kind in (
        (".publish-queue", "queue"),
        (".publish-retry", "retry"),
    ):
        directory = root / directory_name
        if not directory.is_dir():
            continue
        for trigger in sorted(directory.glob("*.txt")):
            trigger_slug = (
                _slug_from_retry_name(trigger.stem) if kind == "retry" else trigger.stem
            )
            if exclude_norm and normalize_text(trigger_slug) == exclude_norm:
                continue
            if candidate_slug and normalize_text(trigger_slug) == candidate_slug:
                return DuplicateMatch(
                    kind,
                    f"{directory_name}/{trigger.name}",
                    trigger_slug,
                    "existing_publish_trigger",
                )

    return None


def format_duplicate(match: DuplicateMatch) -> str:
    return (
        f"{DUPLICATE_CODE}: kind={match.kind}; path={match.path}; "
        f"slug={match.slug}; reason={match.reason}"
    )
