"""No-network invariants for proposals, independent evidence and Inspect gating."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

import jev_scene_inspect as inspect


def proposal():
    return {
        "objects": [
            {
                "name": "Shelf fungus",
                "locator": "The amber shelf on the left trunk",
                "anchorCell": "D4",
                "inspectText": "Amber shelves hug the old bark.",
                "tags": ["fungus", "amber"],
            }
        ]
    }


def fixture():
    cells = {
        c + "_" + k: {"type": "noul", "noul": 0.1} for c in inspect.CELL_IDS for k in inspect.LABELS
    }
    objs = {
        "object_0_" + k: {"type": "noul", "noul": 0.95}
        for k in ("presence", "visual_fit", "no_promises", "tag_0", "tag_1")
    }
    objs["object_0_box"] = {
        "type": "box",
        "box": {"left": 0.1, "top": 0.1, "right": 0.4, "bottom": 0.4},
        "confidence": 0.9,
    }
    return cells, objs


class InspectTests(unittest.TestCase):
    def test_overlapping_walkable_structure_preserved_without_exclusivity(self):
        c, o = fixture()
        for k in ("walkable", "built_structure"):
            c["H2_" + k]["noul"] = 0.98
        scene = inspect.compile_study("art", proposal(), c, o, [])
        labels = next(c for c in scene["cells"] if c["id"] == "H2")["labels"]
        self.assertEqual(labels["walkable"], 0.98)
        self.assertEqual(labels["built_structure"], 0.98)
        self.assertGreater(sum(labels.values()), 1)

    def test_high_fungus_does_not_enable_harvest(self):
        c, o = fixture()
        c["D4_fungus"]["noul"] = 1
        c["D4_harvest_candidate"]["noul"] = 0.1
        scene = inspect.compile_study("art", proposal(), c, o, [])
        self.assertEqual(scene["objects"][0]["enabledActions"], ["inspect"])
        self.assertFalse(scene["runtimeReady"])

    def test_absent_target_cannot_enter_inspect_even_with_box(self):
        c, o = fixture()
        o["object_0_presence"]["noul"] = 0.05
        obj = inspect.compile_study("art", proposal(), c, o, [])["objects"][0]
        self.assertFalse(obj["accepted"])
        self.assertEqual(obj["enabledActions"], [])
        self.assertIn("presence", obj["reviewReasons"])

    def test_promised_mechanics_or_visual_contradiction_held_for_review(self):
        for k in ("visual_fit", "no_promises"):
            c, o = fixture()
            o["object_0_" + k]["noul"] = 0.2
            obj = inspect.compile_study("art", proposal(), c, o, [])["objects"][0]
            self.assertFalse(obj["accepted"])
            self.assertIn(k, obj["reviewReasons"])

    def test_different_anchor_and_box_locations_held_for_review(self):
        c, o = fixture()
        o["object_0_box"]["box"] = {"left": 0.8, "top": 0.8, "right": 0.9, "bottom": 0.9}
        obj = inspect.compile_study("art", proposal(), c, o, [])["objects"][0]
        self.assertFalse(obj["accepted"])
        self.assertIn("anchor_box_disagreement", obj["reviewReasons"])

    def test_bad_proposal_location_and_duplicates_rejected(self):
        p = proposal()
        p["objects"][0]["anchorCell"] = "K10"
        with self.assertRaises(ValueError):
            inspect.validate_proposals(p)
        p = proposal()
        p["objects"] *= 2
        with self.assertRaises(ValueError):
            inspect.validate_proposals(p)

    def test_missing_nonfinite_and_boolean_probabilities_rejected(self):
        for v in (None, float("nan"), float("inf"), True, 1.1):
            with self.assertRaises(ValueError):
                inspect.probability({"noul": v})
        c, o = fixture()
        del c["D4_fungus"]
        with self.assertRaises(ValueError):
            inspect.compile_study("art", proposal(), c, o, [])

    def test_invalid_boxes_and_wrong_models_rejected(self):
        payload = {"questions": {"box": {"type": "box"}}}
        response = {
            "model": inspect.JUDGE,
            "answers": {
                "box": {
                    "type": "box",
                    "box": {"left": 0.5, "right": 0.4, "top": 0, "bottom": 1},
                    "confidence": 0.9,
                }
            },
        }
        with self.assertRaises(ValueError):
            inspect.validate_judgments(payload, response)
        response["answers"]["box"]["box"]["right"] = 0.9
        inspect.validate_judgments(payload, response)
        response["model"] = "other"
        with self.assertRaises(ValueError):
            inspect.validate_judgments(payload, response)

    def test_freeze_roundtrip_and_content_changes_revision(self):
        c, o = fixture()
        p = proposal()
        a = inspect.compile_study("art", p, c, o, [])
        self.assertEqual(a, json.loads(json.dumps(a)))
        self.assertEqual(a, inspect.compile_study("art", p, c, o, []))
        p["objects"][0]["inspectText"] = "Copper shelves cling to bark."
        self.assertNotEqual(a["revision"], inspect.compile_study("art", p, c, o, [])["revision"])

    def test_generated_text_cannot_escape_script(self):
        c, o = fixture()
        p = proposal()
        p["objects"][0]["inspectText"] = "</script><script>alert(1)</script>"
        page = inspect.render(
            inspect.compile_study("art", p, c, o, []), "data:image/png;base64,AA=="
        )
        self.assertNotIn(p["objects"][0]["inspectText"], page)
        self.assertIn("\\u003c/script\\u003e", page)
        self.assertNotIn("__STUDY_DATA__", page)

    def test_brief_is_snapshotted_and_changes_request_identity(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "brief.txt"
            path.write_text("Amber shelves; keep the walkway clear.")
            first = inspect.load_brief(path)
            image = inspect.Image.new("RGB", (160, 144))
            old = inspect.proposal_request(image, image, "test")
            a = inspect.proposal_request(image, image, "test", first)
            self.assertNotEqual(inspect.hash_json(old), inspect.hash_json(a))
            self.assertIn(first["text"], a["messages"][1]["content"][0]["text"])
            path.write_text("Blue shelves; keep the walkway clear.")
            second = inspect.load_brief(path)
            self.assertNotEqual(first["sha256"], second["sha256"])
            self.assertIn("Amber", first["text"])
            self.assertNotEqual(
                inspect.hash_json(a),
                inspect.hash_json(inspect.proposal_request(image, image, "test", second)),
            )

    def test_bad_briefs_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "brief.txt"
            for raw in (b"  ", b"bad\x00text", b"x" * 16385, b"\xff"):
                path.write_bytes(raw)
                with self.assertRaises((ValueError, UnicodeDecodeError)):
                    inspect.load_brief(path)

    def test_brief_cannot_override_absence_and_is_frozen(self):
        c, o = fixture()
        o["object_0_presence"]["noul"] = 0.01
        o["object_0_brief_alignment"] = {"type": "noul", "noul": 1}
        brief = {"text": "Include an amber fungus", "sha256": "test", "role": "intent"}
        result = inspect.compile_study("art", proposal(), c, o, [], brief)
        self.assertFalse(result["objects"][0]["accepted"])
        self.assertEqual(result["objects"][0]["briefAlignment"], 1)
        brief["text"] = "Changed"
        self.assertEqual(result["artBrief"]["text"], "Include an amber fungus")
        self.assertNotEqual(
            result["revision"],
            inspect.compile_study("art", proposal(), c, o, [], brief)["revision"],
        )

    def test_object_judgment_receives_brief_but_cell_labels_do_not(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "scene.png"
            inspect.Image.new("RGB", (160, 144)).save(path)
            brief = {"text": "An amber fungus", "sha256": "test"}
            payload = inspect.object_request(path, proposal()["objects"], 0, brief)
            self.assertEqual(payload["state"]["artBrief"], brief)
            self.assertIn("object_0_brief_alignment", payload["questions"])
            self.assertIn("pixels", payload["questions"]["object_0_presence"]["instructions"])
            _, cell_payload = inspect.cell_request(path, 0)
            self.assertNotIn("artBrief", cell_payload["state"])

    def test_cache_replay_needs_no_key_and_changed_payload_does_not_reuse(self):
        with tempfile.TemporaryDirectory() as d:
            payload = {"model": "test"}
            fp = inspect.hash_json(payload)
            folder = Path(d) / "requests" / ("test-" + fp[:16])
            folder.mkdir(parents=True)
            saved = {"fingerprint": fp, "response": {"ok": True}, "elapsedSeconds": 1}
            (folder / "response.json").write_text(json.dumps(saved))

            def forbidden(*args):
                raise AssertionError("Network must not be called")

            self.assertEqual(
                saved, inspect.cached_call(Path(d), "test", payload, False, "NO_KEY", forbidden)
            )
            with self.assertRaises(SystemExit):
                inspect.cached_call(
                    Path(d), "test", {"model": "changed"}, False, "NO_KEY", forbidden
                )


if __name__ == "__main__":
    unittest.main()
