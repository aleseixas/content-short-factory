from pathlib import Path
import sys

from engine.cli import main
from engine.duplicates import (
    find_duplicate_candidate,
    format_duplicate,
    infer_identity_from_story,
    infer_topic_from_story,
)


def _guard_duplicate_episode(project_root: Path, argv: list[str]) -> int | None:
    if len(argv) < 2 or argv[1].startswith("-"):
        return None

    episode = argv[1].strip()
    story_path = project_root / "episodes" / episode / "story.json"
    if not story_path.is_file():
        return None

    topic = infer_topic_from_story(story_path)
    song, artist = infer_identity_from_story(story_path)
    match = find_duplicate_candidate(
        project_root,
        topic=topic,
        song=song,
        artist=artist,
        slug=episode,
        exclude_slug=episode,
    )
    if match is None:
        return None

    print(f"ERRO: {format_duplicate(match)}", file=sys.stderr)
    print(
        "Esta candidata e duplicada. Descarte somente este topico e avance para a proxima candidata; nao trate como SEM_CANDIDATO global.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    duplicate_exit = _guard_duplicate_episode(root, sys.argv)
    if duplicate_exit is not None:
        raise SystemExit(duplicate_exit)
    raise SystemExit(main(default_project_root=root))
