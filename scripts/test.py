"""Run the offline suite: host C state tests and all scene-tool unit tests."""

import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
env = {k: v for k, v in os.environ.items() if k not in ("TYPESAFE_API_KEY", "XAI_API_KEY")}
commands = [
    [sys.executable, "the-pale-cap/tests/test_home_save.py"],
    [sys.executable, "the-pale-cap/tests/test_inventory.py"],
    [sys.executable, "-m", "unittest", "discover", "-s", "the-pale-cap/tools", "-p", "test_*.py"],
]
for command in commands:
    subprocess.run(command, cwd=ROOT, env=env, check=True)
print("PASS: offline suite; no model API keys passed to test processes")
