import copy
import json
from pathlib import Path
import tempfile
import shutil
from unittest.mock import patch
import unittest

import scene_contract as contract
import scene_prototype as prototype


class PrototypeTests(unittest.TestCase):
    def test_public_example_materializes_offline_and_preserves_existing_runs(self):
        with tempfile.TemporaryDirectory() as temp:
            folder, candidate = prototype.example(output_dir=Path(temp))
            self.assertEqual(prototype.load_candidate(folder), candidate)
            spec = {**candidate["defaults"], "candidateRevision": candidate["revision"]}
            contract.validate(spec, candidate["revision"])
            (folder / "runs").mkdir()
            (folder / "runs/keep.txt").write_text("existing review")
            again, _ = prototype.example(output_dir=Path(temp))
            self.assertEqual(folder, again)
            self.assertEqual((folder / "runs/keep.txt").read_text(), "existing review")
            (folder / "source.png").write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "Snapshot changed"):
                prototype.example(output_dir=Path(temp))

    def test_public_example_rejects_modified_source_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "seed"
            shutil.copytree(prototype.PROJECT.parent / "examples/heartwood", source)
            (source / "labels.json").write_text("[]")
            with self.assertRaisesRegex(ValueError, "Snapshot changed"):
                prototype.example(source, Path(temp) / "output")

    def test_public_example_snapshots_current_engine(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first, old = prototype.example(output_dir=root / "output")
            engine = dict(prototype.ENGINE_FILES)
            engine["main.c"] = root / "new-main.c"
            engine["main.c"].write_text(
                prototype.ENGINE_FILES["main.c"].read_text() + "\n// new revision\n"
            )
            with patch.object(prototype, "ENGINE_FILES", engine):
                second, new = prototype.example(output_dir=root / "output")
            self.assertNotEqual(first, second)
            self.assertNotEqual(old["engineHashes"], new["engineHashes"])
            prototype.load_candidate(first)
            prototype.load_candidate(second)

    def test_public_example_art_matches_recorded_review(self):
        source = prototype.PROJECT.parent / "examples/heartwood"
        before, _, _, audit = prototype.patch.load_patch(source / "art")
        review = json.loads((source / "review-evidence.json").read_text())
        self.assertEqual(audit, review["exactAudit"])
        from PIL import Image

        with Image.open(source / "source.png") as image:
            self.assertEqual(before.convert("RGB").tobytes(), image.convert("RGB").tobytes())

    def test_review_requires_two_explicit_booleans(self):
        payload = {"spec": {"example": 1}, "reviewedGeometry": True, "reviewedMechanics": True}
        self.assertEqual(prototype.approved_spec(payload), payload["spec"])
        for key in ("reviewedGeometry", "reviewedMechanics"):
            for value in (False, 1, "true", None):
                changed = {**payload, key: value}
                with self.assertRaises(ValueError):
                    prototype.approved_spec(changed)
        with self.assertRaises(ValueError):
            prototype.approved_spec({**payload, "runCommand": "anything"})

    def test_snapshot_changes_invalidate_candidate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "art").mkdir()
            (root / "engine").mkdir()
            (root / "art/master.til").write_bytes(b"original")
            candidate = {
                "artHashes": {"master.til": prototype.patch.sha(b"original")},
                "engineHashes": {},
                "presentationHashes": {},
            }
            candidate["revision"] = contract.identity(candidate)
            prototype.json_write(root / "candidate.json", candidate)
            self.assertEqual(prototype.load_candidate(root), candidate)
            (root / "art/master.til").write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "Snapshot changed"):
                prototype.load_candidate(root)

    def test_reviewer_pixels_are_bound_to_candidate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "source.png").write_bytes(b"original")
            candidate = {
                "artHashes": {},
                "engineHashes": {},
                "presentationHashes": {"source.png": prototype.patch.sha(b"original")},
            }
            candidate["revision"] = contract.identity(candidate)
            prototype.json_write(root / "candidate.json", candidate)
            prototype.load_candidate(root)
            (root / "source.png").write_bytes(b"different image")
            with self.assertRaisesRegex(ValueError, "Snapshot changed"):
                prototype.load_candidate(root)

    def test_candidate_metadata_change_is_not_silent(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            candidate = {"artHashes": {}, "engineHashes": {}, "defaults": {"yield": 2}}
            candidate["revision"] = contract.identity(candidate)
            candidate["defaults"]["yield"] = 99
            prototype.json_write(root / "candidate.json", candidate)
            with self.assertRaisesRegex(ValueError, "Candidate was changed"):
                prototype.load_candidate(root)

    def test_embedded_evidence_cannot_close_script(self):
        output = prototype.render_editor({"note": "</script><script>bad()</script>"}, [])
        self.assertNotIn("</script><script>bad()", output)
        self.assertIn("\\u003c/script\\u003e", output)


if __name__ == "__main__":
    unittest.main()
