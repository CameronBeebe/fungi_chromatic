"""Review a bounded scene contract, compile a native prototype, and play it.

prepare snapshots existing encoded art and engine sources. serve presents a local
editor; only its explicit Approve & build action records human approval. verify
builds a clearly marked automation fixture without pretending a human approved it.
"""

from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
from functools import partial
import http.server
import io
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import tempfile
import threading

import heartwood_patch_audit as patch
import jev_scene_inspect as inspect
import scene_contract as contract

PROJECT = Path(__file__).resolve().parents[1]
NATIVE = PROJECT / "art-tests/heartwood-playable"
OUT = PROJECT / "art-tests/scene-prototype/build"
ART_FILES = (
    "master.til",
    "master.map",
    "master.atr",
    "master.pal",
    "master.c",
    "master.h",
    "assets.h",
)
ENGINE_FILES = {
    "main.c": NATIVE / "src/main.c",
    "scene_defaults.h": NATIVE / "src/scene_defaults.h",
    "gbc_hicolor.c": PROJECT / "art-tests/hearth-hicolor/src/gbc_hicolor.c",
    "gbc_hicolor.h": PROJECT / "art-tests/hearth-hicolor/src/gbc_hicolor.h",
}


def json_write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def prepare(review_dir, controls_dir=None):
    parent = json.loads((review_dir / "review.json").read_text())
    if (
        inspect.hash_json({k: v for k, v in parent.items() if k != "revision"})
        != parent["revision"]
    ):
        raise ValueError("Review identity mismatch")
    before, _, _, audit = patch.load_patch(NATIVE / "build")
    if audit != parent["exactAudit"]:
        raise ValueError("Review and encoded art do not match")
    assets = (NATIVE / "build/assets.h").read_text()
    walk = patch.c_array(assets, "walkable", 8)
    candidate = {
        "schemaVersion": 1,
        "adapter": "heartwood-single-harvest-v1",
        "artHashes": {
            name: patch.sha((NATIVE / "build" / name).read_bytes()) for name in ART_FILES
        },
        "engineHashes": {name: patch.sha(path.read_bytes()) for name, path in ENGINE_FILES.items()},
        "reviewRevision": parent["revision"],
        "inspectRevision": parent["inspectRevision"],
        "sourceSHA256": parent["sourceSHA256"],
        "footprintXYWH": list(patch.FOOTPRINT),
        "defaults": {
            "walkable": walk,
            "spawn": [5, 12],
            "approach": [12, 12],
            "workTicks": 60,
            "yield": 2,
            "cost": 1,
            "startSupplies": 3,
        },
        "walkMaskSource": "Existing authored and playtested harness foot grid. Jev evidence is advisory; it has not silently replaced collision.",
        "limitations": [
            "One room and one fixed encoded harvest patch. New scenes need a compatible asset bundle/adapter.",
            "Review foot clearance, elevation and occlusion visually; connectivity alone cannot prove them.",
            "Supply costs and loot are prototype counters. No extraction, hideout, save or trading integration yet.",
        ],
    }
    if controls_dir:
        controls = json.loads((controls_dir / "controls.json").read_text())
        if (
            inspect.hash_json({k: v for k, v in controls.items() if k != "revision"})
            != controls["revision"]
            or controls["parentRevision"] != parent["revision"]
        ):
            raise ValueError("Control report does not belong to this review")
        candidate["controlsRevision"] = controls["revision"]
    # Freeze what the reviewer sees as well as what the compiler consumes.
    png = io.BytesIO()
    before.save(png, format="PNG")
    evidence = {
        "source.png": png.getvalue(),
        "review-evidence.json": (json.dumps(parent, indent=2) + "\n").encode(),
    }
    if controls_dir:
        evidence["control-evidence.json"] = (json.dumps(controls, indent=2) + "\n").encode()
    inspect_source = (
        review_dir.parent.parent / "inspect" / parent["inspectRevision"][:16] / "scene.json"
    )
    if inspect_source.exists():
        original = json.loads(inspect_source.read_text())
        if (
            original.get("revision") != parent["inspectRevision"]
            or original.get("sourceSHA256") != parent["sourceSHA256"]
            or inspect.hash_json({k: v for k, v in original.items() if k != "revision"})
            != original["revision"]
        ):
            raise ValueError("Inspect evidence identity mismatch")
        evidence["labels.json"] = (json.dumps(original["cells"], indent=2) + "\n").encode()
    candidate["presentationHashes"] = {name: patch.sha(data) for name, data in evidence.items()}
    candidate["revision"] = contract.identity(candidate)
    folder = OUT / candidate["revision"][:16]
    folder.mkdir(parents=True, exist_ok=True)
    for sub in ("art", "engine"):
        (folder / sub).mkdir(exist_ok=True)
    for name in ART_FILES:
        shutil.copy2(NATIVE / "build" / name, folder / "art" / name)
    for name, path in ENGINE_FILES.items():
        shutil.copy2(path, folder / "engine" / name)
    json_write(folder / "candidate.json", candidate)
    for name, data in evidence.items():
        (folder / name).write_bytes(data)
    return folder, candidate


def load_candidate(folder):
    candidate = json.loads((folder / "candidate.json").read_text())
    if (
        contract.identity({k: v for k, v in candidate.items() if k != "revision"})
        != candidate["revision"]
    ):
        raise ValueError("Candidate was changed; prepare a new revision")
    for category, key in [
        ("art", "artHashes"),
        ("engine", "engineHashes"),
        ("", "presentationHashes"),
    ]:
        for name, digest in candidate[key].items():
            if (
                Path(name).name != name
                or patch.sha((folder / category / name).read_bytes()) != digest
            ):
                raise ValueError("Snapshot changed: " + category + "/" + name)
    return candidate


def smoke_test(folder, spec):
    from pyboy import PyBoy

    symbols = {
        name: int(addr, 16)
        for addr, name in re.findall(
            r"\b([0-9A-F]{8})\s+(_\w+)", (folder / "prototype.map").read_text()
        )
    }
    with tempfile.TemporaryDirectory() as temporary:
        rom = Path(temporary) / "test.gbc"
        shutil.copy2(folder / "prototype.gbc", rom)
        p = PyBoy(str(rom), window="null", sound_emulated=False)
        p.set_emulation_speed(0)
        try:

            def value(name):
                return p.memory[symbols["_" + name]]

            def tick(n):
                p.tick(n, True)

            def press(button, rest=2):
                p.button_press(button)
                tick(2)
                p.button_release(button)
                tick(rest)

            tick(180)
            press("start", 90)
            if [value("bram_x") // 8, value("bram_y") // 8] != spec["spawn"]:
                raise ValueError("ROM spawn differs from contract")
            if value("supplies") != spec["startSupplies"]:
                raise ValueError("ROM supplies differ from contract")
            p.screen.image.save(folder / "before.png")
            press("a")
            visited = set()
            max_work = 0
            affordable = spec["startSupplies"] >= spec["cost"]
            for _ in range(1600):
                tick(1)
                cell = (value("bram_y") // 8) * 20 + value("bram_x") // 8
                if not spec["walkable"][cell]:
                    raise ValueError("Actor crossed a blocked foot cell")
                visited.add(cell)
                max_work = max(max_work, value("work_ticks"))
                if not value("queue_count"):
                    break
            if value("queue_count"):
                raise ValueError("Order did not finish within the test budget")
            if affordable:
                if (
                    value("harvested") != 1
                    or value("loot") != spec["yield"]
                    or value("supplies") != spec["startSupplies"] - spec["cost"]
                ):
                    raise ValueError("ROM harvest/cost/reward differs from contract")
                if spec["workTicks"] > 4 and max_work != spec["workTicks"] - 1:
                    raise ValueError("Work duration differs from contract")
                tick(30)
                p.screen.image.save(folder / "after.png")
                press("a", 30)
                if (
                    value("loot") != spec["yield"]
                    or value("supplies") != spec["startSupplies"] - spec["cost"]
                ):
                    raise ValueError("Duplicate harvest changed the economy")
                press("start", 20)
                press("start", 40)
                if value("harvested") != 1 or value("loot") != spec["yield"]:
                    raise ValueError("Revisit lost resource state")
            else:
                if (
                    value("harvested")
                    or value("loot")
                    or value("supplies") != spec["startSupplies"]
                ):
                    raise ValueError("Unaffordable work was not blocked")
                p.screen.image.save(folder / "after.png")
            press("select", 40)
            if value("harvested") or value("loot") or value("supplies") != spec["startSupplies"]:
                raise ValueError("Prototype reset did not restore the reviewed economy")
            return {
                "passed": True,
                "initiallyAffordable": affordable,
                "harvestCompleted": affordable,
                "visitedFootCells": len(visited),
                "observedMaxWorkTicks": max_work,
                "checks": [
                    "spawn",
                    "walk mask",
                    "configured supply/cost/yield",
                    "single-yield or unaffordable rejection",
                    "reset",
                ]
                + (["menu revisit persistence", "configured work duration"] if affordable else []),
                "scope": "Actual PyBoy ROM inputs and memory. No save, audio or physical-device certification.",
            }
        finally:
            p.stop(save=False)


def make_web(folder, approval_kind):
    template = PROJECT / "art-tests/hearth-hicolor/web"
    web = folder / "web"
    web.mkdir(exist_ok=True)
    for directory in ("js", "css"):
        shutil.copytree(template / directory, web / directory, dirs_exist_ok=True)
    (web / "rom").mkdir(exist_ok=True)
    shutil.copy2(folder / "prototype.gbc", web / "rom/prototype.gbc")
    config = json.loads((template / "gbstudio.json").read_text())
    config["rom"] = "rom/prototype.gbc"
    json_write(web / "gbstudio.json", config)
    html = (
        (template / "index.html")
        .read_text()
        .replace("Root Hearth — Hi-Color Study", "Heartwood — Reviewed Mechanics Prototype")
    )
    start = html.index('<div class="study-note">')
    end = html.index("</div>", start) + 6
    label = (
        "HUMAN-REVIEWED PROTOTYPE"
        if approval_kind == "human_review"
        else "AUTOMATION TEST FIXTURE · NOT HUMAN APPROVED"
    )
    html = (
        html[:start]
        + '<div class="study-note"><strong>'
        + label
        + "</strong><br>Enter: room/help · Arrows: cursor · Z: queue walk/harvest<br>X: reveal test · Shift: reset · Supplies and bag in help</div>"
        + html[end:]
    )
    html = html.replace(
        "</head>", "<style>#game { top:104px; height:calc(100% - 112px); }</style></head>"
    )
    (web / "index.html").write_text(html)


def build(folder, spec, approval_kind):
    if approval_kind not in ("human_review", "automation_fixture"):
        raise ValueError("Unknown approval source")
    candidate = load_candidate(folder)
    validation = contract.validate(spec, candidate["revision"])
    configured = os.environ.get("GBDK_PATH")
    if not configured:
        raise ValueError("Set GBDK_PATH to a GBDK-2020 installation before building a ROM")
    lcc = Path(configured).expanduser() / "bin/lcc"
    if not lcc.is_file():
        raise ValueError("Configured GBDK compiler is unavailable")
    recipe = {
        "candidateRevision": candidate["revision"],
        "spec": spec,
        "approvalKind": approval_kind,
        "compilerSHA256": patch.sha(lcc.read_bytes()),
        "builderSHA256": patch.sha(Path(__file__).read_bytes()),
        "contractSHA256": patch.sha(Path(contract.__file__).read_bytes()),
    }
    revision = contract.identity(recipe)
    target = folder / "runs" / revision[:16]
    target.mkdir(parents=True, exist_ok=True)
    ready = target / "manifest.json"
    if ready.exists():
        prior = json.loads(ready.read_text())
        if (
            prior["revision"] == revision
            and patch.sha((target / "prototype.gbc").read_bytes()) == prior["romSHA256"]
        ):
            return target, prior
        raise ValueError("Existing build evidence changed")
    json_write(target / "reviewed-spec.json", spec)
    json_write(
        target / "approval.json",
        {
            "kind": approval_kind,
            "recipeRevision": revision,
            "recordedAt": datetime.now(timezone.utc).isoformat(),
            "note": (
                "Human clicked Approve & build in the local editor."
                if approval_kind == "human_review"
                else "Automated verification fixture only. This is not human acceptance."
            ),
        },
    )
    for name in ART_FILES:
        shutil.copy2(folder / "art" / name, target / name)
    for name in ENGINE_FILES:
        shutil.copy2(folder / "engine" / name, target / name)
    asset_text = (target / "assets.h").read_text()
    asset_text, count = re.subn(
        r"const uint8_t walkable\[\]\s*=\s*\{[^}]*\};",
        contract.array("walkable", spec["walkable"]).strip(),
        asset_text,
    )
    if count != 1:
        raise ValueError("Expected one native walk mask")
    (target / "assets.h").write_text(asset_text)
    (target / "scene_config.h").write_text(contract.header(spec))
    (target / "routes.c").write_text(contract.routes(spec["walkable"]))
    command = [
        str(lcc),
        "-Wm-yC",
        "-Wl-yt0x19",
        "-Wl-m",
        "-Wl-w",
        "-autobank",
        "-Wb-ext=.rel",
        "-DSCENE_CONFIGURED",
        "-I.",
        "-o",
        "prototype.gbc",
        "main.c",
        "gbc_hicolor.c",
        "master.c",
        "routes.c",
    ]
    proc = subprocess.run(command, cwd=target, text=True, capture_output=True, timeout=120)
    (target / "compiler.log").write_text(proc.stdout + proc.stderr)
    if proc.returncode:
        raise ValueError("Native compilation failed; compiler.log retains diagnostics")
    rom = (target / "prototype.gbc").read_bytes()
    if len(rom) > 65536 or len(rom) < 32768 or rom[0x143] not in (0x80, 0xC0):
        raise ValueError("Unexpected ROM size/color header")
    checksum = 0
    for b in rom[0x134:0x14D]:
        checksum = (checksum - b - 1) & 255
    if checksum != rom[0x14D]:
        raise ValueError("ROM header checksum failed")
    evidence = smoke_test(target, spec)
    json_write(target / "verification.json", evidence)
    make_web(target, approval_kind)
    manifest = {
        "revision": revision,
        "candidateRevision": candidate["revision"],
        "approvalKind": approval_kind,
        "romSHA256": patch.sha(rom),
        "romBytes": len(rom),
        "validation": validation,
        "verification": evidence,
        "recipe": recipe,
        "productionReady": False,
    }
    json_write(ready, manifest)
    return target, manifest


def render_editor(candidate, labels, fixture=None):
    data = {"candidate": candidate, "labels": labels, "fixture": fixture}
    encoded = (
        json.dumps(data).replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    )
    return Path(__file__).with_suffix(".html").read_text().replace("__EDITOR_DATA__", encoded)


def approved_spec(payload):
    if (
        not isinstance(payload, dict)
        or set(payload) != {"spec", "reviewedGeometry", "reviewedMechanics"}
        or payload["reviewedGeometry"] is not True
        or payload["reviewedMechanics"] is not True
    ):
        raise ValueError("Both explicit review confirmations are required")
    return payload["spec"]


def serve(folder):
    candidate = load_candidate(folder)
    labels = (
        json.loads((folder / "labels.json").read_text())
        if (folder / "labels.json").exists()
        else []
    )
    fixtures = []
    for path in (folder / "runs").glob("*/manifest.json"):
        manifest = json.loads(path.read_text())
        if manifest["approvalKind"] == "automation_fixture":
            fixtures.append({"path": str(path.parent.relative_to(folder)), "manifest": manifest})
    # The default test is the useful starting preview, not an arbitrary last
    # experiment (which may intentionally be unaffordable).
    default_spec = {**candidate["defaults"], "candidateRevision": candidate["revision"]}
    fixture = next((f for f in fixtures if f["manifest"]["recipe"]["spec"] == default_spec), None)
    token = secrets.token_urlsafe(24)
    lock = threading.Lock()

    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            prefix = "/" + token + "/"
            if not self.path.startswith(prefix):
                self.send_error(404)
                return
            path = self.path[len(prefix) :]
            if path == "":
                body = render_editor(candidate, labels, fixture).encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            self.path = "/" + path
            super().do_GET()

        def do_POST(self):
            expected_origin = f"http://127.0.0.1:{self.server.server_port}"
            if (
                self.path != "/" + token + "/approve-build"
                or self.headers.get("Origin") != expected_origin
            ):
                self.send_error(403)
                return
            if self.headers.get("Content-Type") != "application/json":
                self.send_error(415)
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self.send_error(400)
                return
            if not 0 < size <= 32768:
                self.send_error(413)
                return
            if not lock.acquire(blocking=False):
                self.send_error(409)
                return
            try:
                payload = json.loads(self.rfile.read(size))
                target, manifest = build(folder, approved_spec(payload), "human_review")
                result = {"ok": True, "path": str(target.relative_to(folder)), "manifest": manifest}
                status = 200
            except (
                ValueError,
                KeyError,
                TypeError,
                json.JSONDecodeError,
                subprocess.SubprocessError,
                OSError,
            ) as exc:
                result = {"ok": False, "error": str(exc)[:500]}
                status = 400
            finally:
                lock.release()
            body = json.dumps(result).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = http.server.ThreadingHTTPServer(
        ("127.0.0.1", 0), partial(Handler, directory=str(folder))
    )
    print(f"http://127.0.0.1:{server.server_port}/{token}/", flush=True)
    server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("review_dir", type=Path)
    p.add_argument("--controls", type=Path)
    for command in ("serve", "verify"):
        p = sub.add_parser(command)
        p.add_argument("candidate_dir", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        folder, candidate = prepare(args.review_dir, args.controls)
        print(json.dumps({"candidate": str(folder), "revision": candidate["revision"]}))
    elif args.command == "serve":
        serve(args.candidate_dir.resolve())
    else:
        candidate = load_candidate(args.candidate_dir)
        spec = {**copy.deepcopy(candidate["defaults"]), "candidateRevision": candidate["revision"]}
        folder, manifest = build(args.candidate_dir.resolve(), spec, "automation_fixture")
        print(json.dumps({"fixture": str(folder), "manifest": manifest}))


if __name__ == "__main__":
    main()
