import json
import tempfile
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import new_episode
from engine.content import (
    ContentRequest,
    load_content_request,
    load_topic_history,
    resolve_content_request,
    slugify_topic,
)


class ContentRequestTests(unittest.TestCase):
    def test_requires_topic_or_content_profile(self):
        with self.assertRaisesRegex(ValueError, "topic.*content_profile"):
            ContentRequest(category="historia")

    def test_topic_is_free_text_and_bypasses_selector(self):
        request = ContentRequest(
            topic="  Por que a Blockbuster recusou comprar a Netflix?  ",
            content_profile="curiosidades empresariais em ritmo rapido",
        )
        selector = Mock(side_effect=AssertionError("selector must not run"))

        resolved = resolve_content_request(
            request,
            ("Topico anterior",),
            selector=selector,
        )

        self.assertIs(resolved, request)
        self.assertEqual(
            resolved.topic, "Por que a Blockbuster recusou comprar a Netflix?"
        )
        selector.assert_not_called()

    def test_profile_only_uses_injected_selector_with_history(self):
        request = ContentRequest(
            content_profile="historias de negocios pouco conhecidas",
            language="pt-BR",
            additional_instructions="Evite conselhos de investimento pessoal.",
        )
        observed = []

        def selector(received, history):
            observed.append((received, history))
            return "A disputa que criou o padrao VHS"

        resolved = resolve_content_request(
            request,
            ["A historia da fita cassete"],
            selector=selector,
        )

        self.assertEqual(resolved.topic, "A disputa que criou o padrao VHS")
        self.assertEqual(observed, [(request, ("A historia da fita cassete",))])
        self.assertEqual(
            resolved.additional_instructions,
            "Evite conselhos de investimento pessoal.",
        )

    def test_content_profile_accepts_any_natural_language_niche(self):
        profiles = (
            "economia",
            "tecnologia",
            "grandes acontecimentos historicos",
            "curiosidades cientificas visualmente impressionantes",
            "negocios e grandes decisoes",
            "cinema e entretenimento",
            "musica e bastidores da industria musical",
        )

        for profile in profiles:
            with self.subTest(profile=profile):
                request = ContentRequest.from_mapping({"content_profile": profile})
                self.assertEqual(request.content_profile, profile)

    def test_profile_only_requires_external_selector(self):
        with self.assertRaisesRegex(RuntimeError, "seletor externo"):
            resolve_content_request(ContentRequest(content_profile="perfil livre"))

    def test_generic_entities_are_optional_and_normalized(self):
        request = ContentRequest(
            topic="A origem de Brasilia",
            entities=["Oscar Niemeyer", " Oscar Niemeyer "],
            events=["Construcao da capital"],
            locations=["Brasilia"],
            time_period="  anos 1950  ",
            visual_keywords=["arquitetura modernista"],
        )

        self.assertEqual(request.entities, ("Oscar Niemeyer",))
        self.assertEqual(request.events, ("Construcao da capital",))
        self.assertEqual(request.locations, ("Brasilia",))
        self.assertEqual(request.time_period, "anos 1950")
        self.assertEqual(request.visual_keywords, ("arquitetura modernista",))

    def test_generic_entity_fields_reject_json_objects(self):
        with self.assertRaisesRegex(ValueError, "entities precisa"):
            ContentRequest.from_mapping(
                {"topic": "Tema", "entities": {"empresa": "Netflix"}}
            )

    def test_topic_history_prefers_explicit_topic_and_falls_back_to_title(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for slug, payload in (
                (
                    "current",
                    {"topic": "Topico canonico", "title": "Titulo de exibicao"},
                ),
                ("legacy", {"title": "Titulo legado"}),
                ("duplicate", {"topic": "topico CANONICO"}),
            ):
                episode = root / "episodes" / slug
                episode.mkdir(parents=True)
                (episode / "story.json").write_text(
                    json.dumps(payload, ensure_ascii=False), encoding="utf-8"
                )
            malformed = root / "episodes" / "malformed"
            malformed.mkdir(parents=True)
            (malformed / "story.json").write_text("{", encoding="utf-8")

            history = load_topic_history(root)

        self.assertEqual(set(history), {"Topico canonico", "Titulo legado"})

    def test_load_content_request_supports_topic_and_profile_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            topic_path = root / "topic.json"
            topic_path.write_text(
                json.dumps(
                    {
                        "topic": "O desastre do submarino Titan",
                        "language": "pt-BR",
                    }
                ),
                encoding="utf-8",
            )
            profile_path = root / "profile.json"
            profile_path.write_text(
                json.dumps(
                    {
                        "topic": None,
                        "content_profile": "tecnologia e historias de empresas",
                        "additional_instructions": "Priorize grandes decisoes.",
                    }
                ),
                encoding="utf-8",
            )

            topic_request = load_content_request(topic_path)
            profile_request = load_content_request(profile_path)

        self.assertEqual(topic_request.topic, "O desastre do submarino Titan")
        self.assertIsNone(topic_request.content_profile)
        self.assertEqual(
            profile_request.content_profile,
            "tecnologia e historias de empresas",
        )
        self.assertIsNone(profile_request.topic)

    def test_slugify_topic_handles_portuguese_unicode(self):
        self.assertEqual(slugify_topic("Águas de Março"), "aguas_de_marco")
        self.assertEqual(
            slugify_topic("Por que a Blockbuster recusou comprar a Netflix?"),
            "por_que_a_blockbuster_recusou_comprar_a_netflix",
        )
        with self.assertRaisesRegex(ValueError, "derivar um slug"):
            slugify_topic("?!")


class NewEpisodeCliTests(unittest.TestCase):
    @staticmethod
    def _config():
        return SimpleNamespace(paths=SimpleNamespace(episodes_dir="episodes"))

    def test_topic_mode_creates_complete_generic_scaffold_without_music_identity(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_dir = root / "config"
            config_dir.mkdir()
            (config_dir / "config.json").write_text(
                json.dumps(
                    {
                        "paths": {},
                        "render": {},
                        "duration": {},
                        "tts": {},
                        "mix": {},
                    }
                ),
                encoding="utf-8",
            )

            result = new_episode.main(
                [
                    "--topic",
                    "O erro de software da Knight Capital",
                    "--content-profile",
                    "tecnologia e negocios",
                ],
                default_project_root=root,
            )
            episode = root / "episodes" / "o_erro_de_software_da_knight_capital"
            story = json.loads((episode / "story.json").read_text(encoding="utf-8"))
            post = json.loads((episode / "post.json").read_text(encoding="utf-8"))

        self.assertEqual(result, 0)
        self.assertEqual(story["topic"], "O erro de software da Knight Capital")
        self.assertEqual(story["content_profile"], "tecnologia e negocios")
        self.assertNotIn("artist", story)
        self.assertNotIn("song", story)
        self.assertEqual(post["youtube"]["category_id"], "22")
        self.assertEqual(post["youtube"]["hashtags"], ["shorts"])

    def test_topic_derives_slug_and_creates_post_template(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            destination = root / "episodes" / "aguas_de_marco"
            with (
                patch.object(
                    new_episode, "load_project_config", return_value=self._config()
                ),
                patch.object(
                    new_episode, "find_duplicate_candidate", return_value=None
                ),
                patch.object(
                    new_episode, "create_episode", return_value=destination
                ) as create,
                patch.object(new_episode, "create_post_template") as create_post,
            ):
                result = new_episode.main(
                    ["--topic", "Águas de Março", "--entity", "Tom Jobim"],
                    default_project_root=root,
                )

        self.assertEqual(result, 0)
        _, _, slug = create.call_args.args
        content = create.call_args.kwargs["content"]
        self.assertEqual(slug, "aguas_de_marco")
        self.assertEqual(content.topic, "Águas de Março")
        self.assertEqual(content.entities, ("Tom Jobim",))
        create_post.assert_called_once_with(destination)

    def test_explicit_slug_overrides_derived_slug_and_creates_post_template(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            destination = root / "episodes" / "custom_slug"
            with (
                patch.object(
                    new_episode, "load_project_config", return_value=self._config()
                ),
                patch.object(
                    new_episode, "find_duplicate_candidate", return_value=None
                ),
                patch.object(
                    new_episode, "create_episode", return_value=destination
                ) as create,
                patch.object(new_episode, "create_post_template") as create_post,
            ):
                result = new_episode.main(
                    ["custom_slug", "--topic", "Tema especifico"],
                    default_project_root=root,
                )

        self.assertEqual(result, 0)
        self.assertEqual(create.call_args.args[2], "custom_slug")
        self.assertEqual(create.call_args.kwargs["content"].topic, "Tema especifico")
        create_post.assert_called_once_with(destination)

    def test_slug_without_topic_or_profile_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            stderr = StringIO()
            with (
                patch.object(
                    new_episode, "load_project_config", return_value=self._config()
                ),
                patch.object(new_episode, "create_episode") as create,
                redirect_stderr(stderr),
            ):
                result = new_episode.main(["orphan_slug"], default_project_root=root)

        self.assertEqual(result, 1)
        self.assertIn("--topic", stderr.getvalue())
        self.assertIn("--content-profile", stderr.getvalue())
        create.assert_not_called()

    def test_legacy_song_and_artist_pair_becomes_a_topic(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            destination = root / "episodes" / "legacy_music_slug"
            with (
                patch.object(
                    new_episode, "load_project_config", return_value=self._config()
                ),
                patch.object(
                    new_episode, "find_duplicate_candidate", return_value=None
                ),
                patch.object(
                    new_episode, "create_episode", return_value=destination
                ) as create,
                patch.object(new_episode, "create_post_template") as create_post,
            ):
                result = new_episode.main(
                    [
                        "legacy_music_slug",
                        "--song",
                        "Bohemian Rhapsody",
                        "--artist",
                        "Queen",
                    ],
                    default_project_root=root,
                )

        self.assertEqual(result, 0)
        self.assertEqual(create.call_args.args[2], "legacy_music_slug")
        self.assertEqual(
            create.call_args.kwargs["content"].topic,
            "Queen — Bohemian Rhapsody",
        )
        create_post.assert_called_once_with(destination)

    def test_profile_only_reports_missing_external_selector(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            stderr = StringIO()
            with (
                patch.object(
                    new_episode, "load_project_config", return_value=self._config()
                ),
                redirect_stderr(stderr),
            ):
                result = new_episode.main(
                    ["--content-profile", "perfil livre"],
                    default_project_root=root,
                )

        self.assertEqual(result, 1)
        self.assertIn("seletor externo", stderr.getvalue())

    def test_profile_request_json_uses_selector_and_derives_final_slug(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            request_path = root / "request.json"
            request_path.write_text(
                json.dumps(
                    {
                        "content_profile": "tecnologia e historias de empresas",
                        "additional_instructions": "Priorize grandes decisoes.",
                    }
                ),
                encoding="utf-8",
            )
            destination = root / "episodes" / "como_a_kodak_perdeu_a_revolucao_digital"
            selector = Mock(return_value="Como a Kodak perdeu a revolucao digital")
            with (
                patch.object(
                    new_episode, "load_project_config", return_value=self._config()
                ),
                patch.object(
                    new_episode,
                    "load_topic_history",
                    return_value=("Topico anterior",),
                ),
                patch.object(
                    new_episode, "find_duplicate_candidate", return_value=None
                ),
                patch.object(
                    new_episode, "create_episode", return_value=destination
                ) as create,
                patch.object(new_episode, "create_post_template") as create_post,
            ):
                result = new_episode.main(
                    ["--request", str(request_path)],
                    default_project_root=root,
                    topic_selector=selector,
                )

        self.assertEqual(result, 0)
        self.assertEqual(
            create.call_args.args[2],
            "como_a_kodak_perdeu_a_revolucao_digital",
        )
        resolved = create.call_args.kwargs["content"]
        self.assertEqual(resolved.topic, "Como a Kodak perdeu a revolucao digital")
        self.assertEqual(resolved.content_profile, "tecnologia e historias de empresas")
        selector.assert_called_once()
        create_post.assert_called_once_with(destination)

    def test_profile_only_can_use_injected_selector_and_derives_slug(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            legacy = root / "episodes" / "legacy"
            legacy.mkdir(parents=True)
            (legacy / "story.json").write_text(
                json.dumps({"title": "Uma crise bancaria anterior"}),
                encoding="utf-8",
            )
            destination = root / "episodes" / "corrida_aos_bancos"
            selector = Mock(return_value="Como uma corrida aos bancos comeca")
            with (
                patch.object(
                    new_episode, "load_project_config", return_value=self._config()
                ),
                patch.object(
                    new_episode, "find_duplicate_candidate", return_value=None
                ),
                patch.object(
                    new_episode, "create_episode", return_value=destination
                ) as create,
                patch.object(new_episode, "create_post_template") as create_post,
            ):
                result = new_episode.main(
                    ["--content-profile", "economia"],
                    default_project_root=root,
                    topic_selector=selector,
                )

        self.assertEqual(result, 0)
        selected_request, history = selector.call_args.args
        self.assertEqual(selected_request.content_profile, "economia")
        self.assertEqual(history, ("Uma crise bancaria anterior",))
        self.assertEqual(create.call_args.args[2], "como_uma_corrida_aos_bancos_comeca")
        self.assertEqual(
            create.call_args.kwargs["content"].topic,
            "Como uma corrida aos bancos comeca",
        )
        create_post.assert_called_once_with(destination)


if __name__ == "__main__":
    unittest.main()
