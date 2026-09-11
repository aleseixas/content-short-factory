from __future__ import annotations

import argparse
from pathlib import Path
import sys
from collections.abc import Sequence

from engine.config import load_project_config
from engine.content import (
    ContentRequest,
    TopicSelector,
    load_content_request,
    load_topic_history,
    resolve_content_request,
    slugify_topic,
)
from engine.duplicates import find_duplicate_candidate, format_duplicate
from engine.episode import create_episode
from publishing.metadata import create_post_template


def main(
    argv: Sequence[str] | None = None,
    default_project_root: Path | None = None,
    *,
    topic_selector: TopicSelector | None = None,
) -> int:
    parser = argparse.ArgumentParser(
        description="Cria os templates de um episodio novo."
    )
    parser.add_argument(
        "episode",
        nargs="?",
        default="",
        help="Slug opcional; quando omitido, e derivado de --topic.",
    )
    parser.add_argument("--topic", default="", help="Tema livre do conteudo.")
    parser.add_argument(
        "--request",
        type=Path,
        default=None,
        help="Arquivo JSON com o contrato editorial Topic/Profile Mode.",
    )
    parser.add_argument(
        "--content-profile",
        default="",
        help=(
            "Perfil editorial livre. Sem --topic, exige um seletor externo "
            "injetado na API de main()."
        ),
    )
    parser.add_argument("--category", default="", help="Categoria editorial opcional.")
    parser.add_argument("--angle", default="", help="Angulo narrativo opcional.")
    parser.add_argument(
        "--target-duration",
        type=float,
        default=None,
        help="Duracao alvo em segundos.",
    )
    parser.add_argument("--language", default="", help="Idioma editorial opcional.")
    parser.add_argument(
        "--additional-instructions",
        default="",
        help="Instrucoes editoriais adicionais.",
    )
    parser.add_argument(
        "--entity", action="append", default=[], help="Entidade relevante; repetivel."
    )
    parser.add_argument(
        "--event", action="append", default=[], help="Evento relevante; repetivel."
    )
    parser.add_argument(
        "--location", action="append", default=[], help="Local relevante; repetivel."
    )
    parser.add_argument("--time-period", default="", help="Periodo temporal opcional.")
    parser.add_argument(
        "--visual-keyword",
        action="append",
        default=[],
        help="Palavra-chave visual; repetivel.",
    )
    parser.add_argument(
        "--song",
        default="",
        help="Compatibilidade legada: nome da musica para duplicidade.",
    )
    parser.add_argument(
        "--artist",
        default="",
        help="Compatibilidade legada: artista para duplicidade.",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=default_project_root or Path.cwd(),
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args(argv)
    project_root = args.project_root.resolve()
    try:
        config = load_project_config(project_root / "config" / "config.json")
        editorial_input = any(
            (
                args.topic.strip(),
                args.content_profile.strip(),
                args.category.strip(),
                args.angle.strip(),
                args.target_duration is not None,
                args.language.strip(),
                args.additional_instructions.strip(),
                args.entity,
                args.event,
                args.location,
                args.time_period.strip(),
                args.visual_keyword,
            )
        )
        content: ContentRequest | None = None
        if args.request is not None and editorial_input:
            raise ValueError(
                "Use --request ou os campos editoriais da CLI, nao os dois ao mesmo tempo."
            )
        if args.request is not None:
            request_path = args.request
            if not request_path.is_absolute():
                request_path = project_root / request_path
            content = load_content_request(request_path.resolve())
        elif editorial_input:
            request = ContentRequest(
                topic=args.topic,
                content_profile=args.content_profile,
                category=args.category,
                angle=args.angle,
                target_duration=args.target_duration,
                language=args.language,
                additional_instructions=args.additional_instructions,
                entities=tuple(args.entity),
                events=tuple(args.event),
                locations=tuple(args.location),
                time_period=args.time_period,
                visual_keywords=tuple(args.visual_keyword),
            )
            content = request
        elif args.song.strip() and args.artist.strip():
            content = ContentRequest(
                topic=f"{args.artist.strip()} — {args.song.strip()}"
            )
        else:
            raise ValueError("Informe --topic ou --content-profile.")

        history = (
            load_topic_history(project_root, config.paths.episodes_dir)
            if content.topic is None
            else ()
        )
        content = resolve_content_request(
            content,
            history,
            selector=topic_selector,
        )

        episode_slug = args.episode.strip()
        if not episode_slug and content.topic is not None:
            episode_slug = slugify_topic(content.topic)
        if not episode_slug:
            raise ValueError("Informe o slug posicional ou --topic para deriva-lo.")

        duplicate = find_duplicate_candidate(
            project_root,
            topic=content.topic,
            song=args.song,
            artist=args.artist,
            slug=episode_slug,
        )
        if duplicate is not None:
            print(f"ERRO: {format_duplicate(duplicate)}", file=sys.stderr)
            print(
                "Descarte somente esta candidata e avance para o proximo topico.",
                file=sys.stderr,
            )
            return 2

        destination = create_episode(
            project_root,
            config.paths.episodes_dir,
            episode_slug,
            content=content,
        )
        create_post_template(destination)
    except (RuntimeError, ValueError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1
    print(f"Episodio criado em: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(default_project_root=Path(__file__).resolve().parent))
