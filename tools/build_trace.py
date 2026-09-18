"""Recompute and stage the worked example's browser evidence and downloads."""
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
destination = ROOT / "viewer" / "trace"
subprocess.run([sys.executable, str(ROOT / "examples/trace_example.py"), str(destination)], check=True)
shutil.copyfile(ROOT / "examples/trace_example.py", destination / "trace_example.py")
