"""Serve this exact standalone ROM in the repository's licensed Binjgb player."""

from pathlib import Path
from functools import partial
import http.server
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parent
template = ROOT.parent / "hearth-hicolor/web"
web = ROOT / "build/web"
web.mkdir(exist_ok=True)
for directory in ("js", "css"):
    shutil.copytree(template / directory, web / directory, dirs_exist_ok=True)
(web / "rom").mkdir(exist_ok=True)
shutil.copy2(ROOT / "build/heartwood-playable.gbc", web / "rom/heartwood-playable.gbc")
config = json.loads((template / "gbstudio.json").read_text())
config["rom"] = "rom/heartwood-playable.gbc"
(web / "gbstudio.json").write_text(json.dumps(config, indent=2) + "\n")
html = (
    (template / "index.html")
    .read_text()
    .replace("Root Hearth — Hi-Color Study", "Heartwood — Playable Hi-Color Study")
)
start = html.index('<div class="study-note">')
end = html.index("</div>", start) + 6
html = (
    html[:start]
    + """<div class="study-note"><strong>HEARTWOOD · PLAYABLE HI-COLOR TEST</strong><br>Enter: room/help · Arrows: cursor · Z: queue walk/harvest<br>X: reveal art test · Shift: reset · Bag count in help<br>Standalone experiment · No save or audio</div>"""
    + html[end:]
)
html = html.replace(
    "</head>", "<style>#game { top:104px; height:calc(100% - 112px); }</style></head>"
)
(web / "index.html").write_text(html)
if "--prepare-only" in sys.argv:
    raise SystemExit(0)
handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(web))
server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
print(f"http://127.0.0.1:{server.server_port}/", flush=True)
server.serve_forever()
