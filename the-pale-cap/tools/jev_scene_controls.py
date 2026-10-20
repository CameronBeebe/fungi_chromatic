"""Bounded visual controls and target localization; no art or game mutations.

Run once per prompt version, preserve all results, and never retry until pass.
Expected control labels are used only by code, never included in model requests.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from PIL import Image
import heartwood_patch_audit as patch
import jev_scene_inspect as inspect
import jev_scene_review as review
import jev_scene_probe as probe
from jev_scene_package import fingerprint

CROP = (96, 72, 144, 112)
CASES = [
    {
        "id": "forward",
        "name": "Intact → depleted",
        "before": "intact",
        "after": "depleted",
        "expected": {
            "depleted_readable": True,
            "changed": True,
            "material_lost": True,
            "material_gained": False,
        },
    },
    {
        "id": "same_intact",
        "name": "Intact → same intact",
        "before": "intact",
        "after": "intact",
        "expected": {
            "depleted_readable": False,
            "changed": False,
            "material_lost": False,
            "material_gained": False,
        },
    },
    {
        "id": "same_depleted",
        "name": "Depleted → same depleted",
        "before": "depleted",
        "after": "depleted",
        "expected": {
            "depleted_readable": False,
            "changed": False,
            "material_lost": False,
            "material_gained": False,
        },
    },
    {
        "id": "reverse",
        "name": "Depleted → intact",
        "before": "depleted",
        "after": "intact",
        "expected": {
            "depleted_readable": False,
            "changed": True,
            "material_lost": False,
            "material_gained": True,
        },
    },
]
QUESTIONS = {
    "changed": "Is there any discernible difference in the depicted objects or ground INSIDE the central target area between the first and second image? Identical images mean no, regardless of whether the scene looks depleted.",
    "material_lost": "From the first image to the second, has visible above-ground material in the central target cluster been removed or reduced? Compare corresponding pixels and shapes. A depleted-looking second image alone is insufficient: the first must show material that the second lacks. No for unchanged images or material appearing.",
    "material_gained": "From the first image to the second, has visible above-ground material appeared or increased in the central target cluster? Compare corresponding pixels and shapes. No for unchanged images or material disappearing.",
}
POLICY = {
    "version": 1,
    "expectedYesMinimum": 0.7,
    "expectedNoMaximum": 0.3,
    "presenceMinimum": 0.65,
    "scope": "Four deliberately constructed pairs from one authored patch, not a held-out accuracy benchmark. Cutoffs are provisional. No automatic promotion.",
}
TARGET = "The single small cluster of three ochre fan-shaped mushroom caps on the open ground in the lower-right clearing, separate from the huge shelves on the trunk"


def transition_request(before, after):
    payload = review.request_base()
    review.add_image(payload, "first", before)
    review.add_image(payload, "second", after)
    review.add_image(payload, "first_crop", before.crop(CROP))
    review.add_image(payload, "second_crop", after.crop(CROP))
    payload["state"].update(
        {
            "nativeSize": [160, 144],
            "cropBoundsXYXY": list(CROP),
            "targetFootprintXYWH": list(patch.FOOTPRINT),
            "context": "Two ordered views of the same native scene and the same registered crop. Compare first to second. Either view may be identical to the other; either direction of change is possible. No intended edit, expected answer, previous score or difference image is supplied. The target area is the authored footprint, not the whole forest. Images use nearest-neighbor enlargement.",
        }
    )
    for key, question in QUESTIONS.items():
        payload["questions"][key] = {
            "type": "noul",
            "instructions": "Use `first`, `second`, `first_crop` and `second_crop`. " + question,
        }
    return payload


def localization_request(image, guided):
    payload = review.request_base()
    review.add_image(payload, "scene", image)
    payload["state"][
        "context"
    ] = "Locate visible artwork, not a conceptual feature. Do not assume the named target exists. No previous model bounds, anchor, scores or desired box are supplied. Presence and Box are independent questions."
    target_image = "scene"
    if guided:
        review.add_image(payload, "crop", image.crop(CROP))
        payload["state"][
            "context"
        ] += " The crop is an authored search neighborhood, not a predicted object boundary. Use the scene only for context; return box edges relative to the CROP image."
        target_image = "crop"
    payload["questions"]["presence"] = {
        "type": "noul",
        "instructions": f"In `{target_image}`, is this target visibly identifiable: {TARGET}? Judge the actual pixels, not the fact that a region was supplied.",
    }
    payload["questions"]["bounds"] = {
        "type": "box",
        "instructions": f"Locate the entire cluster described here in `{target_image}`: {TARGET}. Return one tight box around the cluster, including all its caps and stems, in {target_image.upper()} image coordinates.",
    }
    if guided:
        for edge in ("left", "top", "right", "bottom"):
            payload["questions"]["clipped_" + edge] = {
                "type": "noul",
                "instructions": f"Does the target cluster ({TARGET}) visibly continue beyond the {edge} edge of `crop`? Ignore unrelated scenery. This asks whether the supplied crop cuts off the target, not whether a predicted box is correct.",
            }
    return payload


def native_box(box, frame):
    x0, y0, x1, y1 = frame
    return [
        x0 + box["left"] * (x1 - x0),
        y0 + box["top"] * (y1 - y0),
        x0 + box["right"] * (x1 - x0),
        y0 + box["bottom"] * (y1 - y0),
    ]


def box_metrics(bounds):
    left, top, right, bottom = bounds
    x, y, w, h = patch.FOOTPRINT
    area = (right - left) * (bottom - top)
    overlap = max(0, min(right, x + w) - max(left, x)) * max(0, min(bottom, y + h) - max(top, y))
    return {
        "boundsXYXY": bounds,
        "widthPixels": right - left,
        "heightPixels": bottom - top,
        "centerInAuthoredFootprint": x <= (left + right) / 2 < x + w
        and y <= (top + bottom) / 2 < y + h,
        "fractionOfBoxInsideFootprint": overlap / area if area > 0 else 0,
        "note": "An edit footprint is larger than object art. Overlap is a location diagnostic, not segmentation accuracy.",
    }


def overlap_iou(a, b):
    intersection = max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(
        0, min(a[3], b[3]) - max(a[1], b[1])
    )
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - intersection
    return intersection / union if union > 0 else 0


def compile_location(answer, guided):
    p = inspect.probability(answer.get("presence"))
    box = answer["bounds"]["box"]
    metrics = box_metrics(native_box(box, CROP if guided else (0, 0, 160, 144)))
    clipping = (
        {
            edge: inspect.probability(answer.get("clipped_" + edge))
            for edge in ("left", "top", "right", "bottom")
        }
        if guided
        else {}
    )
    reasons = []
    if p < POLICY["presenceMinimum"]:
        reasons.append("target_presence_uncertain")
    if not metrics["centerInAuthoredFootprint"]:
        reasons.append("center_outside_authored_site")
    if metrics["heightPixels"] < 2 or metrics["widthPixels"] < 2:
        reasons.append("implausibly_thin_cluster_box")
    if any(v > POLICY["expectedNoMaximum"] for v in clipping.values()):
        reasons.append("crop_may_clip_target")
    return {
        "presence": p,
        "boxConfidence": answer["bounds"]["confidence"],
        "box": box,
        "coordinateFrame": "crop" if guided else "full_scene",
        "metrics": metrics,
        "clipping": clipping,
        "reviewReasons": reasons,
        "supportedCandidate": not reasons,
        "automaticallyLinked": False,
    }


def evaluate_case(case, version, answers, exact):
    keys = ["depleted_readable"] if version == "original" else list(QUESTIONS)
    scored = {}
    for key in keys:
        value = inspect.probability(answers.get(key))
        expected = case["expected"][key]
        matched = (
            value >= POLICY["expectedYesMinimum"]
            if expected
            else value <= POLICY["expectedNoMaximum"]
        )
        scored[key] = {
            "probability": value,
            "expected": expected,
            "meetsProvisionalExpectation": matched,
        }
    return {
        "id": case["id"],
        "name": case["name"],
        "before": case["before"],
        "after": case["after"],
        "version": version,
        "judgments": scored,
        "exactAudit": exact,
        "meetsAllExpectations": all(v["meetsProvisionalExpectation"] for v in scored.values()),
    }


def render(study):
    text = json.dumps(study).replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    return Path(__file__).with_suffix(".html").read_text().replace("__CONTROL_DATA__", text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review_dir", type=Path)
    parser.add_argument(
        "--native-build", type=Path, default=Path("the-pale-cap/art-tests/heartwood-playable/build")
    )
    parser.add_argument(
        "--out", type=Path, default=Path("the-pale-cap/art-tests/jev-scene-probe/build/controls")
    )
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--target-id", default="heartwood.inspect.05")
    args = parser.parse_args()
    parent = json.loads((args.review_dir / "review.json").read_text())
    identity = {k: v for k, v in parent.items() if k != "revision"}
    if inspect.hash_json(identity) != parent["revision"]:
        raise ValueError("Parent review identity mismatch")
    targets = [o for o in parent["objects"] if o["id"] == args.target_id]
    if len(targets) != 1:
        raise ValueError("Target must identify one object in the parent review")
    target = targets[0]
    before, after, _, exact = patch.load_patch(args.native_build)
    if exact != parent["exactAudit"]:
        raise ValueError("Native patch differs from the parent review")
    images = {"intact": before, "depleted": after}
    jobs = []
    for version in ("original", "transition"):
        for case in CASES:
            a, b = images[case["before"]], images[case["after"]]
            payload = (
                review.comparison_request(a, b)
                if version == "original"
                else transition_request(a, b)
            )
            jobs.append(
                (
                    version + "_" + case["id"],
                    "harvest-comparison" if version == "original" else "transition-v2",
                    payload,
                )
            )
    for guided in (False, True):
        stage = "localize_guided" if guided else "localize_full"
        jobs.append((stage, stage, localization_request(before, guided)))
    cache = args.review_dir.parent
    pending = sum(
        not (cache / "requests" / f"{stage}-{fingerprint(payload)[:16]}" / "response.json").exists()
        for _, stage, payload in jobs
    )
    # One saved forward request must be reusable; this run is a bounded follow-up.
    if pending > 9:
        raise ValueError(
            "Expected the original forward comparison cache; at most nine new calls are allowed"
        )
    args.out.mkdir(parents=True, exist_ok=True)
    plan = {
        "parentRevision": parent["revision"],
        "cases": CASES,
        "policy": POLICY,
        "requestFingerprints": {name: fingerprint(payload) for name, _, payload in jobs},
        "maximumNewCalls": 9,
        "runPolicy": "One request per input and prompt version; no automatic retries. Expected labels are not sent to the model.",
    }
    (args.out / ("plan-" + inspect.hash_json(plan)[:16] + ".json")).write_text(
        json.dumps(plan, indent=2) + "\n"
    )
    answers = {}
    calls = []
    for name, stage, payload in jobs:
        saved = inspect.cached_call(
            cache, stage, payload, args.run, "TYPESAFE_API_KEY", probe.evaluate
        )
        inspect.validate_judgments(payload, saved["response"])
        answers[name] = saved["response"]["answers"]
        calls.append(
            {
                "name": name,
                "model": saved["response"]["model"],
                "requestFingerprint": saved["fingerprint"],
                "usage": saved["response"].get("usage", {}),
                "elapsedSeconds": saved["elapsedSeconds"],
            }
        )
    records = []
    for version in ("original", "transition"):
        for case in CASES:
            measured, _ = patch.audit_pixels(images[case["before"]], images[case["after"]])
            records.append(
                evaluate_case(case, version, answers[version + "_" + case["id"]], measured)
            )
    result = {
        "schemaVersion": 1,
        "parentRevision": parent["revision"],
        "inspectRevision": parent["inspectRevision"],
        "sourceSHA256": parent["sourceSHA256"],
        "runtimeReady": False,
        "plan": plan,
        "cases": records,
        "originalTarget": copy.deepcopy(target),
        "originalBoxMetrics": box_metrics(native_box(target["box"], (0, 0, 160, 144))),
        "localization": {
            "full": compile_location(answers["localize_full"], False),
            "guided": compile_location(answers["localize_guided"], True),
        },
        "cropBoundsXYXY": list(CROP),
        "footprintXYWH": list(patch.FOOTPRINT),
        "transitionQuestions": QUESTIONS,
        "originalQuestion": review.CHECKS["depleted_readable"],
        "provenance": [
            {k: v for k, v in c.items() if k not in ("usage", "elapsedSeconds")} for c in calls
        ],
        "notes": [
            "Known unchanged pairs have zero changed pixels. Nonempty-change failure is expected for those controls, not an asset bug.",
            "The guided search uses an authored region, not an automatically discovered location.",
            "The parent proposal, its acceptance status and its ID are unchanged. New boxes are review candidates, not collision masks.",
            "These four related cases diagnose one scene. They do not establish general accuracy or calibrated probabilities.",
        ],
    }
    result["localizationAgreement"] = {
        "intersectionOverUnion": overlap_iou(
            result["localization"]["full"]["metrics"]["boundsXYXY"],
            result["localization"]["guided"]["metrics"]["boundsXYXY"],
        ),
        "requiresHumanReview": True,
        "automaticallyLinked": False,
    }
    result["revision"] = inspect.hash_json(result)
    folder = args.out / result["revision"][:16]
    folder.mkdir(exist_ok=True)
    for name, im in images.items():
        im.save(folder / (name + ".png"))
    (folder / "controls.json").write_text(json.dumps(result, indent=2) + "\n")
    (folder / "evidence.json").write_text(
        json.dumps({"answers": answers, "calls": calls}, indent=2) + "\n"
    )
    (folder / "index.html").write_text(render(result))
    (args.out / "index.html").write_text(
        f'<!doctype html><meta charset="utf-8"><title>Scene controls</title><a href="{folder.name}/">Latest visual controls and localization</a>'
    )
    print(
        json.dumps(
            {
                "dashboard": str(folder / "index.html"),
                "newCallsNeededAtStart": pending,
                "controlMatches": {
                    v: sum(c["meetsAllExpectations"] for c in records if c["version"] == v)
                    for v in ("original", "transition")
                },
                "localization": result["localization"],
            }
        )
    )


if __name__ == "__main__":
    main()
