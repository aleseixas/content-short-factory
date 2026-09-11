from __future__ import annotations

from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ContentWorkflowContractTests(unittest.TestCase):
    def test_duplicate_preflight_is_topic_driven(self):
        workflow = (
            PROJECT_ROOT / ".github" / "workflows" / "duplicate-preflight.yml"
        ).read_text(encoding="utf-8")

        self.assertIn('topic = optional_text("topic")', workflow)
        self.assertIn('content_profile = optional_text("content_profile")', workflow)
        self.assertIn("if value is None:", workflow)
        self.assertIn('check_duplicate.py --topic "$TOPIC" --slug "$SLUG"', workflow)
        self.assertNotIn("request precisa conter song, artist", workflow)

    def test_legacy_music_request_is_only_a_compatibility_fallback(self):
        workflow = (
            PROJECT_ROOT / ".github" / "workflows" / "duplicate-preflight.yml"
        ).read_text(encoding="utf-8")

        self.assertIn("if not topic and song and artist", workflow)
        self.assertIn('topic = f"{artist} — {song}"', workflow)
        self.assertIn('--song "$SONG" --artist "$ARTIST"', workflow)


if __name__ == "__main__":
    unittest.main()
