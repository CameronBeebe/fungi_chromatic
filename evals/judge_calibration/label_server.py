"""Local labeling page for the Heartwood cell-label eval.

Serves label.html, the scene image and the current labels on 127.0.0.1 only, and
saves labels to evals/judge_calibration/labels.csv. No external services, no
model calls, and Jev's probabilities are never sent to the page.

Usage, from the repo root:
    uv run --locked python -m evals.judge_calibration.label_server
then open http://127.0.0.1:8765/ in a browser.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from evals.judge_calibration import heartwood as hw

PAGE = hw.HERE / "label.html"
SOURCE = hw.EXAMPLE / "source.png"
MAX_BODY = 256 * 1024
MAX_NOTE = 500
ALLOWED = {"", hw.YES, hw.NO, "skip"}


def current_rows(labels_path: Path) -> list[dict[str, str]]:
    rows = {r["cell_id"]: r for r in hw.blank_rows()}
    if labels_path.exists():
        for cid, row in hw.load_human(labels_path).items():
            rows[cid].update({f: (row.get(f) or "") for f in hw.CSV_FIELDS if f != "cell_id"})
    return [rows[c] for c in hw.cell_ids()]


def page_data(labels_path: Path) -> dict:
    """Everything the page needs. Deliberately excludes Jev's probabilities."""
    authored = hw.load_authored_walkable()
    return {
        "cells": hw.cell_ids(),
        "cols": hw.COLS,
        "rows": hw.ROWS,
        "cell": hw.CELL,
        "labels": hw.LABELS,
        "walkFail": hw.WALK_FAIL,
        "current": current_rows(labels_path),
        "authoredWalkable": [c for c in hw.cell_ids() if authored[c]],
        "labelsFile": labels_path.name,
    }


def clean_rows(payload: object) -> list[dict[str, str]]:
    """Validate a save request into exactly 90 CSV rows. Raises ValueError."""
    if not isinstance(payload, dict) or not isinstance(payload.get("rows"), list):
        raise ValueError("Expected {rows: [...]}")
    by_id = {}
    for row in payload["rows"]:
        if not isinstance(row, dict):
            raise ValueError("Each row must be an object")
        cid = str(row.get("cell_id", "")).upper()
        x, y = hw.cell_xy(cid)
        out = {"cell_id": cid, "row": str(y + 1), "col": str(x + 1)}
        for f in hw.LABELS + ["walk_fail_" + r for r in hw.WALK_FAIL]:
            value = str(row.get(f, "")).strip().lower()
            if value not in ALLOWED:
                raise ValueError(f"Bad value for {cid} {f}")
            out[f] = value
        note = str(row.get("notes", ""))
        if len(note) > MAX_NOTE:
            raise ValueError("Note too long for " + cid)
        out["notes"] = " ".join(note.split())
        by_id[cid] = out
    if sorted(by_id) != sorted(hw.cell_ids()):
        raise ValueError("Expected all 90 cells")
    return [by_id[c] for c in hw.cell_ids()]


def save(labels_path: Path, payload: object) -> dict:
    rows = clean_rows(payload)
    tmp = labels_path.with_suffix(".csv.tmp")
    hw.write_rows(tmp, rows)
    os.replace(tmp, labels_path)
    human = {r["cell_id"]: r for r in rows}
    return {"saved": labels_path.name, "isolated": hw.isolated_walkable(human)}


def make_handler(labels_path: Path):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, code: int, body: bytes, kind: str) -> None:
            self.send_response(code)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _json(self, code: int, value: object) -> None:
            self._send(code, json.dumps(value).encode(), "application/json")

        def do_GET(self) -> None:  # noqa: N802
            path = self.path.split("?", 1)[0]
            if path in ("/", "/index.html"):
                self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
            elif path == "/source.png":
                self._send(200, SOURCE.read_bytes(), "image/png")
            elif path == "/data.json":
                self._json(200, page_data(labels_path))
            else:
                self._send(404, b"not found", "text/plain")

        def do_POST(self) -> None:  # noqa: N802
            if self.path != "/save":
                return self._send(404, b"not found", "text/plain")
            length = int(self.headers.get("Content-Length") or 0)
            if not 0 < length <= MAX_BODY:
                return self._json(400, {"error": "Bad request size"})
            try:
                result = save(labels_path, json.loads(self.rfile.read(length)))
            except (ValueError, json.JSONDecodeError) as err:
                return self._json(400, {"error": str(err)})
            self._json(200, result)

        def log_message(self, fmt: str, *args) -> None:
            pass

    return Handler


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Serve the Heartwood labeling page locally.")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--labels", default=str(hw.HERE / "labels.csv"))
    args = parser.parse_args(argv)
    labels_path = Path(args.labels).resolve()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(labels_path))
    print(
        f"Labeling page: http://127.0.0.1:{args.port}/  (saves to {labels_path.name}; Ctrl+C stops)"
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
