"""Offline tests for the Heartwood cell-label calibration eval.

Every human label in this file is SYNTHETIC, made up to check the arithmetic and
plumbing. None of it is one of Cameron's labels. The only real data used is the
recorded Jev file and the authored grid already in examples/heartwood/.
"""

from __future__ import annotations

import csv
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

from evals.judge_calibration import heartwood as hw
from evals.judge_calibration import label_server, score

KEY_NAMES = ("TYPESAFE_API_KEY", "XAI_API_KEY")
KEY_LIKE = [
    re.compile(r"(?:sk|xai|tsk?)-[A-Za-z0-9_\-]{8,}"),
    re.compile(r"Bearer\s+[A-Za-z0-9._\-]{8,}"),
    # long mixed-case token with digits, the usual shape of an API key
    re.compile(
        r"(?=[A-Za-z0-9_\-]*[A-Z])(?=[A-Za-z0-9_\-]*[a-z])(?=[A-Za-z0-9_\-]*\d)"
        r"[A-Za-z0-9_\-]{24,}"
    ),
]


def synthetic_rows(walkable=(), fungus=(), skip=()):
    """SYNTHETIC labels: every cell labeled, yes only for the given cells."""
    rows = hw.blank_rows()
    for r in rows:
        c = r["cell_id"]
        for k in hw.LABELS:
            r[k] = "skip" if c in skip else hw.NO
        if c in skip:
            continue
        if c in walkable:
            r["walkable"] = hw.YES
        else:
            r["walk_fail_cant_stand"] = hw.YES
        if c in fungus:
            r["fungus"] = hw.YES
    return rows


class Metrics(unittest.TestCase):
    def test_kappa_matches_a_hand_worked_binary_example(self):
        # SYNTHETIC: 20 agree-yes, 5 human-yes/judge-no, 10 human-no/judge-yes, 15 agree-no.
        human = ["yes"] * 25 + ["no"] * 25
        judge = ["yes"] * 20 + ["no"] * 5 + ["yes"] * 10 + ["no"] * 15
        self.assertEqual(score.confusion(human, judge, score.CLASSES), [[20, 5], [10, 15]])
        self.assertAlmostEqual(score.agreement(human, judge), 0.7)
        self.assertAlmostEqual(score.cohens_kappa(human, judge, score.CLASSES), 0.4)
        pc = score.per_class(human, judge, score.CLASSES)
        self.assertAlmostEqual(pc["yes"]["precision"], 20 / 30)
        self.assertAlmostEqual(pc["yes"]["recall"], 20 / 25)
        self.assertAlmostEqual(pc["no"]["precision"], 15 / 20)

    def test_kappa_edges(self):
        same = ["yes", "no", "no", "yes"]  # SYNTHETIC
        self.assertEqual(score.cohens_kappa(same, same, score.CLASSES), 1.0)
        self.assertAlmostEqual(score.cohens_kappa(same, ["no"] * 4, score.CLASSES), 0.0)
        lo, hi = score.bootstrap_kappa(same * 5, same * 5, score.CLASSES, reps=50)
        self.assertEqual((lo, hi), (1.0, 1.0))

    def test_brier_bins_and_sweep(self):
        human = ["yes", "yes", "no", "no"]  # SYNTHETIC
        probs = [1.0, 0.7, 0.3, 0.0]
        self.assertAlmostEqual(score.brier(human, probs), (0 + 0.09 + 0.09 + 0) / 4)
        bins = {b["bin"]: b for b in score.calibration_bins(human, probs)}
        self.assertEqual(bins["0.8-1.0"]["n"], 1)  # 1.0 lands in the top bin
        self.assertEqual(bins["0.6-0.8"]["human_yes_rate"], 1.0)
        self.assertEqual(bins["0.0-0.2"]["human_yes_rate"], 0.0)
        self.assertIsNone(bins["0.4-0.6"]["mean_p"])
        by_t = {r["threshold"]: r for r in score.sweep(human, probs)}
        self.assertEqual(by_t[0.5]["agreement"], 1.0)
        self.assertEqual(by_t[0.8]["recall"], 0.5)


class HeartwoodData(unittest.TestCase):
    def test_recorded_files_cover_all_90_cells(self):
        self.assertEqual(len(hw.load_jev()), 90)
        self.assertEqual(len(hw.load_authored_walkable()), 90)

    def test_authored_baseline_matches_the_earlier_check(self):
        jev, authored = hw.load_jev(), hw.load_authored_walkable()
        ids = hw.cell_ids()
        ref = ["yes" if authored[c] else "no" for c in ids]
        judge = [score.to_label(jev[c]["walkable"], 0.5) for c in ids]
        self.assertEqual(score.confusion(ref, judge, score.CLASSES), [[21, 0], [33, 36]])
        self.assertAlmostEqual(score.cohens_kappa(ref, judge, score.CLASSES), 0.337, places=3)

    def test_connectivity_flags_isolated_patch(self):
        # SYNTHETIC: a 3-cell strip plus a lone cell far away.
        rows = synthetic_rows(walkable={"C5", "D5", "E5", "J1"})
        human = {r["cell_id"]: r for r in rows}
        self.assertEqual(hw.isolated_walkable(human), ["J1"])
        # Diagonal contact is not a connection.
        rows = synthetic_rows(walkable={"C5", "D5", "E6"})
        self.assertEqual(hw.isolated_walkable({r["cell_id"]: r for r in rows}), ["E6"])

    def test_template_is_blank(self):
        with open(hw.HERE / "labels_template.csv", newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual([r["cell_id"] for r in rows], hw.cell_ids())
        self.assertTrue(all(r[k] == "" for r in rows for k in hw.LABELS))


class Report(unittest.TestCase):
    def test_pending_report_shows_only_baseline(self):
        report = score.build_report(labels_path="/nonexistent/labels.csv")
        self.assertIn("Labels pending", report)
        self.assertIn("not human labels", report)
        self.assertNotIn("## walkable", report)

    def test_report_with_synthetic_labels_and_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            labels = Path(tmp) / "labels.csv"
            hw.write_rows(
                labels,
                synthetic_rows(walkable={"C5", "D5", "E5", "J1"}, fungus={"D1", "E1"}, skip={"A1"}),
            )
            other = json.loads((hw.EXAMPLE / "labels.json").read_text())
            other[1]["labels"]["walkable"] = 0.99  # SYNTHETIC second judge run: B1 flips
            compare = Path(tmp) / "other.json"
            compare.write_text(json.dumps(other))
            report = score.build_report(labels, compare_path=compare)
        self.assertIn("Scored: 89. Unlabeled or skip: 1.", report)
        self.assertIn("agreement with designer preference, not accuracy", report)
        self.assertIn("Connectivity check", report)
        self.assertIn("J1", report)
        self.assertIn("Brier score", report)
        self.assertIn("Calibration by bin", report)
        self.assertIn("Human walkable vs the authored grid", report)
        self.assertIn("- cant_stand: 85", report)
        self.assertIn("walkable: 90 shared", report)
        self.assertIn("changed: B1", report)

    def test_invalid_label_is_reported_not_scored(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows = synthetic_rows()
            rows[0]["water"] = "maybe"  # SYNTHETIC bad value
            labels = Path(tmp) / "labels.csv"
            hw.write_rows(labels, rows)
            report = score.build_report(labels)
        self.assertIn("Invalid labels: A1=maybe", report)


class Server(unittest.TestCase):
    def test_page_data_never_contains_jev_probabilities(self):
        data = label_server.page_data(Path("/nonexistent/labels.csv"))
        text = json.dumps(data)
        self.assertNotIn("0.", text)
        self.assertEqual(len(data["current"]), 90)
        self.assertTrue(all(r["walkable"] == "" for r in data["current"]))

    def test_clean_rows_rejects_bad_input(self):
        good = {"rows": [dict(r) for r in synthetic_rows()]}
        self.assertEqual(len(label_server.clean_rows(good)), 90)
        bad = {"rows": good["rows"][:-1]}
        self.assertRaises(ValueError, label_server.clean_rows, bad)
        worse = {"rows": [dict(r) for r in synthetic_rows()]}
        worse["rows"][0]["fungus"] = "<script>"
        self.assertRaises(ValueError, label_server.clean_rows, worse)

    def test_serves_and_saves_locally(self):
        with tempfile.TemporaryDirectory() as tmp:
            labels = Path(tmp) / "labels.csv"
            server = ThreadingHTTPServer(("127.0.0.1", 0), label_server.make_handler(labels))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{server.server_address[1]}"
            try:
                page = urllib.request.urlopen(base + "/").read().decode()
                self.assertIn("(a) the cell is connected to the main walkable region", page)
                self.assertEqual(
                    urllib.request.urlopen(base + "/source.png").read()[:4], b"\x89PNG"
                )
                rows = synthetic_rows(walkable={"C5", "D5", "J1"})  # SYNTHETIC
                req = urllib.request.Request(
                    base + "/save",
                    data=json.dumps({"rows": rows}).encode(),
                    headers={"Content-Type": "application/json"},
                )
                out = json.loads(urllib.request.urlopen(req).read())
                self.assertEqual(out["isolated"], ["J1"])
                saved = hw.load_human(labels)
                self.assertEqual(saved["C5"]["walkable"], "yes")
                data = json.loads(urllib.request.urlopen(base + "/data.json").read())
                self.assertEqual(data["current"][0]["walkable"], "no")
            finally:
                server.shutdown()
                server.server_close()


class KeySafety(unittest.TestCase):
    def _run(self, env, tmp):
        labels = Path(tmp) / "labels.csv"
        hw.write_rows(labels, synthetic_rows(walkable={"C5", "D5"}))  # SYNTHETIC
        report = Path(tmp) / "report.md"
        cmd = [
            sys.executable,
            "-m",
            "evals.judge_calibration.score",
            "--labels",
            str(labels),
            "--out",
            str(report),
        ]
        proc = subprocess.run(cmd, cwd=hw.ROOT, env=env, capture_output=True, text=True, check=True)
        page = (hw.HERE / "label.html").read_text(encoding="utf-8")
        data = json.dumps(label_server.page_data(labels))
        return "\n".join(
            [proc.stdout, proc.stderr, report.read_text(), labels.read_text(), page, data]
        )

    def test_runs_with_keys_unset_and_outputs_have_nothing_key_like(self):
        env = {k: v for k, v in os.environ.items() if k not in KEY_NAMES}
        with tempfile.TemporaryDirectory() as tmp:
            text = self._run(env, tmp)
        for pattern in KEY_LIKE:
            self.assertIsNone(pattern.search(text), pattern.pattern)

    def test_synthetic_canary_keys_in_env_never_reach_outputs(self):
        # SYNTHETIC canaries, not real keys. If any code read the env, they could leak.
        canaries = {"TYPESAFE_API_KEY": "canaryQ7wZ3tsKx", "XAI_API_KEY": "canaryM2pV9xaiR"}
        env = {k: v for k, v in os.environ.items() if k not in KEY_NAMES}
        env.update(canaries)
        with tempfile.TemporaryDirectory() as tmp:
            text = self._run(env, tmp)
        for value in canaries.values():
            for i in range(len(value) - 5):
                self.assertNotIn(value[i : i + 6], text)

    def test_eval_code_has_no_network_client_or_key_reads(self):
        for name in ("heartwood.py", "score.py", "label_server.py", "label.html"):
            src = (hw.HERE / name).read_text(encoding="utf-8")
            for banned in (
                "urllib.request",
                "API_KEY",
                "environ",
                "api.x.ai",
                "typesafe.ai",
                "http://",
                "https://",
            ):
                if banned == "http://" and name == "label_server.py":
                    continue  # prints the local 127.0.0.1 address only
                self.assertNotIn(banned, src, f"{banned} in {name}")


if __name__ == "__main__":
    unittest.main()
