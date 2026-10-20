"""Local-only native studies fail clearly before writing incomplete build output."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class ToolPrerequisiteTests(unittest.TestCase):
    def run_builder(self, study, *arguments):
        env = dict(os.environ)
        env.pop("GBDK_PATH", None)
        return subprocess.run(
            [sys.executable, str(ROOT / "the-pale-cap/art-tests" / study / "build.py"), *arguments],
            env=env,
            capture_output=True,
            text=True,
        )

    def test_missing_gbdk_has_actionable_error(self):
        for study in ("heartwood-playable", "overworld-gallery"):
            result = self.run_builder(study)
            self.assertEqual(result.returncode, 2)
            self.assertIn("Set GBDK_PATH", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_missing_local_art_is_explained_without_compilation(self):
        with tempfile.TemporaryDirectory() as folder:
            gbdk = Path(folder)
            (gbdk / "bin").mkdir()
            for name in ("lcc", "png2hicolorgb"):
                (gbdk / "bin" / name).touch()
            for study in ("heartwood-playable", "overworld-gallery"):
                result = self.run_builder(
                    study, "--gbdk", folder, "--source", str(gbdk / "missing-art")
                )
                self.assertEqual(result.returncode, 2)
                self.assertIn("concept-art/", result.stderr)
                self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
