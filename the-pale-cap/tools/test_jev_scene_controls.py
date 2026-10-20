import unittest
from PIL import Image
import jev_scene_controls as controls
import jev_scene_review as review
from jev_scene_package import fingerprint


class ControlsTests(unittest.TestCase):
    def test_expected_labels_never_enter_requests(self):
        a = Image.new("RGB", (160, 144))
        b = a.copy()
        b.putpixel((110, 90), (255, 0, 0))
        payload = controls.transition_request(a, b)
        self.assertNotIn("expected", payload["state"])
        self.assertNotIn("intent", payload["state"])
        self.assertEqual(set(payload["questions"]), {"changed", "material_lost", "material_gained"})
        self.assertNotEqual(fingerprint(payload), fingerprint(controls.transition_request(b, a)))

    def test_crop_box_maps_into_full_scene(self):
        box = {"left": 0.25, "top": 0.25, "right": 0.75, "bottom": 0.75}
        self.assertEqual(controls.native_box(box, controls.CROP), [108, 82, 132, 102])
        metrics = controls.box_metrics([108, 82, 132, 102])
        self.assertTrue(metrics["centerInAuthoredFootprint"])
        self.assertEqual(metrics["fractionOfBoxInsideFootprint"], 1)

    def test_guidance_is_explicit_and_absent_in_full_search(self):
        im = Image.new("RGB", (160, 144))
        full = controls.localization_request(im, False)
        guided = controls.localization_request(im, True)
        self.assertEqual(len(full["assets"]), 1)
        self.assertEqual(len(guided["assets"]), 2)
        self.assertIn("CROP", guided["questions"]["bounds"]["instructions"])
        self.assertNotIn("crop", full["state"])

    def test_high_box_confidence_cannot_override_presence_or_clip(self):
        answer = {
            "presence": {"noul": 0.2},
            "bounds": {
                "box": {"left": 0.25, "top": 0.25, "right": 0.75, "bottom": 0.75},
                "confidence": 0.99,
            },
        }
        answer.update(
            {"clipped_" + edge: {"noul": 0.05} for edge in ("left", "right", "top", "bottom")}
        )
        self.assertFalse(controls.compile_location(answer, True)["supportedCandidate"])
        answer["presence"]["noul"] = 0.9
        answer["clipped_top"]["noul"] = 0.9
        self.assertFalse(controls.compile_location(answer, True)["supportedCandidate"])
        answer["clipped_top"]["noul"] = 0.05
        result = controls.compile_location(answer, True)
        self.assertTrue(result["supportedCandidate"])
        self.assertFalse(result["automaticallyLinked"])

    def test_same_state_harvest_score_is_not_treated_as_success(self):
        case = controls.CASES[2]
        result = controls.evaluate_case(
            case, "original", {"depleted_readable": {"noul": 0.95}}, {"changedPixels": 0}
        )
        self.assertFalse(result["meetsAllExpectations"])
        answers = {k: {"noul": 0.01} for k in controls.QUESTIONS}
        self.assertTrue(
            controls.evaluate_case(case, "transition", answers, {})["meetsAllExpectations"]
        )

    def test_no_change_is_not_a_global_asset_failure_and_reverse_is_not_harvest(self):
        reverse = controls.CASES[3]
        answers = {
            "changed": {"noul": 0.99},
            "material_lost": {"noul": 0.01},
            "material_gained": {"noul": 0.99},
        }
        self.assertTrue(
            controls.evaluate_case(reverse, "transition", answers, {})["meetsAllExpectations"]
        )
        identical = Image.new("RGB", (160, 144))
        payload = review.comparison_request(identical, identical)
        self.assertEqual(
            fingerprint(payload), fingerprint(review.comparison_request(identical, identical))
        )


if __name__ == "__main__":
    unittest.main()
