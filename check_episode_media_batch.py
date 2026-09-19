from __future__ import annotations

import argparse
import json
from pathlib import Path

from check_episode_media import (
    _assert_background_is_fresh,
    _classify_preflight_failure,
    _single_line,
    _visual_aliases,
)
from engine.assets import AssetManager
from engine.config import load_project_config
from engine.episode import load_episode
from engine.music import resolve_background_music

MAX_VIDEO_SOURCE_USES = 10
DEFAULT_VIDEO_REUSE_WINDOW_SECONDS = 4.0


def _error_record(exc: Exception, slug: str, *, scope: str = "") -> dict[str, object]:
    code, recoverable, target, action = _classify_preflight_failure(exc, slug)
    record: dict[str, object] = {
        "code": code,
        "class": exc.__class__.__name__,
        "detail": _single_line(exc) or exc.__class__.__name__,
        "recoverable": recoverable,
        "target": target,
        "recommended_action": action,
        "same_slug": slug or "UNKNOWN",
    }
    if scope:
        record["scope"] = scope
    return record


def _emit_batch(errors: list[dict[str, object]], slug: str) -> int:
    if not errors:
        print("MEDIA_PREFLIGHT_RESULT=PASS")
        print("MEDIA_PREFLIGHT_ERROR_COUNT=0")
        print("MEDIA_PREFLIGHT_SAME_SLUG=" + slug)
        return 0

    payload = json.dumps(errors, ensure_ascii=False, separators=(",", ":"))
    first = errors[0]

    print("MEDIA_PREFLIGHT_RESULT=FAIL")
    print(f"MEDIA_PREFLIGHT_ERROR_COUNT={len(errors)}")
    print(f"MEDIA_PREFLIGHT_ERRORS_JSON={payload}")
    print(f"MEDIA_PREFLIGHT_ERROR_CODE={first['code']}")
    print(f"MEDIA_PREFLIGHT_ERROR_CLASS={first['class']}")
    print(f"MEDIA_PREFLIGHT_ERROR_DETAIL={first['detail']}")
    print(
        "MEDIA_PREFLIGHT_RECOVERABLE="
        + ("true" if bool(first.get("recoverable")) else "false")
    )
    print(f"MEDIA_PREFLIGHT_TARGET={first['target']}")
    print(f"MEDIA_PREFLIGHT_RECOMMENDED_ACTION={first['recommended_action']}")
    print(f"MEDIA_PREFLIGHT_SAME_SLUG={slug or 'UNKNOWN'}")

    for index, error in enumerate(errors, start=1):
        print(
            "MEDIA_PREFLIGHT_ERROR_ITEM="
            + json.dumps({"index": index, **error}, ensure_ascii=False, separators=(",", ":"))
        )
    return 1


def _video_source_identity(asset) -> tuple[str, str]:
    aliases = _visual_aliases(asset)
    for preferred_kind in ("file", "url"):
        for identity in aliases:
            if identity[0] == preferred_kind:
                return identity
    return ("asset_id", asset.id.casefold())


def _shot_source_interval(shot) -> tuple[float, float]:
    start = float(shot.source_start_seconds or 0.0)
    if shot.source_end_seconds is not None:
        end = float(shot.source_end_seconds)
    else:
        end = start + DEFAULT_VIDEO_REUSE_WINDOW_SECONDS
    return start, end


def _collect_visual_structure_errors(episode, slug: str) -> list[dict[str, object]]:
    errors: list[dict[str, object]] = []
    seen_images: dict[tuple[str, str], tuple[str, str]] = {}
    video_usages: dict[tuple[str, str], list[tuple[str, str, float, float]]] = {}

    for shot in episode.shots:
        asset = episode.assets.get(shot.asset_id)
        if asset is None:
            exc = RuntimeError(
                f"Shot {shot.id!r} referencia asset inexistente {shot.asset_id!r}."
            )
            errors.append(_error_record(exc, slug, scope=f"shot:{shot.id}"))
            continue

        if not asset.is_video:
            aliases = _visual_aliases(asset)
            duplicate_found = False
            for identity in aliases:
                previous = seen_images.get(identity)
                if previous is None:
                    continue
                previous_shot, previous_asset = previous
                identity_kind, identity_value = identity
                exc = RuntimeError(
                    "INTRA_EPISODE_VISUAL_REUSE_BLOCKED: a mesma imagem foi usada "
                    "mais de uma vez dentro do episodio. "
                    f"Shot {shot.id!r} (asset={asset.id!r}) repete a imagem de "
                    f"{previous_shot!r} (asset={previous_asset!r}); "
                    f"identidade={identity_kind}:{identity_value}."
                )
                errors.append(_error_record(exc, slug, scope=f"shot:{shot.id}"))
                duplicate_found = True
                break
            if not duplicate_found:
                for identity in aliases:
                    seen_images[identity] = (shot.id, asset.id)
            continue

        identity = _video_source_identity(asset)
        usages = video_usages.setdefault(identity, [])
        start, end = _shot_source_interval(shot)

        if end <= start:
            exc = RuntimeError(
                "INTRA_EPISODE_VISUAL_REUSE_BLOCKED: intervalo de video invalido para "
                f"shot={shot.id!r} asset={asset.id!r}; start={start:.3f} end={end:.3f}."
            )
            errors.append(_error_record(exc, slug, scope=f"shot:{shot.id}"))
            continue

        if len(usages) >= MAX_VIDEO_SOURCE_USES:
            identity_kind, identity_value = identity
            exc = RuntimeError(
                "INTRA_EPISODE_VISUAL_REUSE_BLOCKED: a mesma fonte de video excedeu "
                f"o limite de {MAX_VIDEO_SOURCE_USES} shots; shot={shot.id!r} "
                f"asset={asset.id!r} identidade={identity_kind}:{identity_value}."
            )
            errors.append(_error_record(exc, slug, scope=f"shot:{shot.id}"))
            continue

        overlap = next(
            (
                previous
                for previous in usages
                if start < previous[3] and previous[2] < end
            ),
            None,
        )
        if overlap is not None:
            previous_shot, previous_asset, previous_start, previous_end = overlap
            identity_kind, identity_value = identity
            exc = RuntimeError(
                "INTRA_EPISODE_VISUAL_REUSE_BLOCKED: a mesma fonte de video usa "
                "intervalos sobrepostos. "
                f"Shot {shot.id!r} (asset={asset.id!r}, {start:.3f}-{end:.3f}s) "
                f"sobrepoe {previous_shot!r} (asset={previous_asset!r}, "
                f"{previous_start:.3f}-{previous_end:.3f}s); "
                f"identidade={identity_kind}:{identity_value}."
            )
            errors.append(_error_record(exc, slug, scope=f"shot:{shot.id}"))
            continue

        usages.append((shot.id, asset.id, start, end))

    if not errors:
        print(
            "[preflight] intra-episode visual uniqueness OK: "
            f"{len(episode.shots)} shot(s); imagens unicas e videos com segmentos nao sobrepostos"
        )
    return errors
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate all independent episode media checks and report failures as one batch."
    )
    parser.add_argument("episode", help="Episode slug")
    args = parser.parse_args()
    slug = args.episode.strip()

    root = Path(__file__).resolve().parent
    errors: list[dict[str, object]] = []

    try:
        config = load_project_config(root / "config" / "config.json")
        episodes_dir = Path(config.paths.episodes_dir)
        cache_dir = Path(config.paths.cache_dir)
        if not cache_dir.is_absolute():
            cache_dir = root / cache_dir
        episode = load_episode(root, config.paths.episodes_dir, slug)
    except Exception as exc:
        return _emit_batch([_error_record(exc, slug, scope="episode-load")], slug)

    work_dir = root / config.paths.work_dir / ".media-preflight" / episode.name
    video_cache = cache_dir / "video"
    try:
        manager = AssetManager(
            assets_dir=episode.assets_dir,
            work_dir=work_dir,
            width=config.render.width,
            height=config.render.height,
            scale=1,
            allowed_assets_root=episode.directory,
            video_cache_dir=video_cache,
        )
    except Exception as exc:
        return _emit_batch([_error_record(exc, slug, scope="asset-manager")], slug)

    print("[preflight] validating intra-episode visual structure...")
    errors.extend(_collect_visual_structure_errors(episode, slug))

    print(f"[preflight] validating {len(episode.assets)} episode assets independently...")
    asset_failures = 0
    for asset in episode.assets.values():
        try:
            manager.ensure(asset)
        except Exception as exc:
            asset_failures += 1
            errors.append(_error_record(exc, slug, scope=f"asset:{asset.id}"))
    if asset_failures:
        print(f"[preflight] asset failures collected: {asset_failures}")
    else:
        print("[preflight] assets OK")

    resolved_music = None
    try:
        resolved_music = resolve_background_music(
            root,
            episode.background_music,
            episode.name,
            cache_root=cache_dir,
        )
    except Exception as exc:
        errors.append(_error_record(exc, slug, scope="background-music-resolve"))

    if resolved_music is None:
        if episode.background_music is None:
            print("[preflight] background music: none")
    else:
        print(
            f"[preflight] background music OK: profile={resolved_music.profile} "
            f"file={resolved_music.path}"
        )
        if episode.background_music is not None:
            try:
                _assert_background_is_fresh(
                    root,
                    episodes_dir,
                    cache_dir,
                    episode.name,
                    episode.background_music,
                    resolved_music.path,
                )
            except Exception as exc:
                errors.append(_error_record(exc, slug, scope="background-music-freshness"))

    # De-duplicate identical diagnostics while preserving deterministic order.
    unique: list[dict[str, object]] = []
    seen_keys: set[tuple[str, str, str]] = set()
    for error in errors:
        key = (
            str(error.get("code") or ""),
            str(error.get("detail") or ""),
            str(error.get("scope") or ""),
        )
        if key in seen_keys:
            continue
        seen_keys.add(key)
        unique.append(error)

    return _emit_batch(unique, slug)


if __name__ == "__main__":
    raise SystemExit(main())
