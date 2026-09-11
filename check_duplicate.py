from __future__ import annotations

import argparse
from pathlib import Path
import sys

from engine.duplicates import (
    find_duplicate_candidate,
    format_duplicate,
    infer_identity_from_story,
    infer_topic_from_story,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detecta episodio/candidata duplicada."
    )
    parser.add_argument("--topic", default="", help="Tema livre da candidata.")
    parser.add_argument(
        "--song", default="", help="Compatibilidade legada: nome da musica candidata."
    )
    parser.add_argument(
        "--artist", default="", help="Compatibilidade legada: artista da candidata."
    )
    parser.add_argument("--slug", default="", help="Slug provavel da candidata.")
    parser.add_argument(
        "--episode",
        default="",
        help="Slug ja criado; infere topic (ou title legado) e ignora o proprio slug.",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args()
    root = args.project_root.resolve()

    topic = args.topic.strip()
    song = args.song.strip()
    artist = args.artist.strip()
    slug = args.slug.strip()
    exclude_slug: str | None = None

    if args.episode:
        episode = args.episode.strip()
        story_path = root / "episodes" / episode / "story.json"
        if not story_path.is_file():
            print(f"ERRO: story.json nao encontrado para {episode!r}.", file=sys.stderr)
            return 1
        topic = topic or infer_topic_from_story(story_path)
        inferred_song, inferred_artist = infer_identity_from_story(story_path)
        song = song or inferred_song
        artist = artist or inferred_artist
        slug = slug or episode
        exclude_slug = episode

    if not slug and not topic and not (song and artist):
        print("ERRO: informe --topic, --slug ou --song + --artist.", file=sys.stderr)
        return 1

    match = find_duplicate_candidate(
        root,
        topic=topic,
        song=song,
        artist=artist,
        slug=slug,
        exclude_slug=exclude_slug,
    )
    if match is not None:
        print(format_duplicate(match))
        return 2

    print(
        f"CANDIDATE_UNIQUE: topic={topic or 'N/A'}; slug={slug or 'N/A'}; "
        f"song={song or 'N/A'}; artist={artist or 'N/A'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
