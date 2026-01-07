import os
import sys
import subprocess
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
VENV_PYTHON = PROJECT_DIR / ".venv" / "bin" / "python"
SCRIPT = PROJECT_DIR / "listeningGPT.py"

# Windows venv path fallback
if sys.platform.startswith("win"):
    VENV_PYTHON = PROJECT_DIR / ".venv" / "Scripts" / "python.exe"

if not VENV_PYTHON.exists():
    print("Virtual environment python not found:", VENV_PYTHON)
    sys.exit(1)

if sys.platform.startswith("linux"):
    subprocess.Popen([
        "gnome-terminal", "--",
        str(VENV_PYTHON), str(SCRIPT)
    ])

elif sys.platform == "darwin":
    subprocess.Popen([
        "open", "-a", "Terminal.app",
        str(VENV_PYTHON), str(SCRIPT)
    ])

elif sys.platform.startswith("win"):
    subprocess.Popen([
        "cmd", "/k",
        str(VENV_PYTHON), str(SCRIPT)
    ])

else:
    print("Unsupported OS:", sys.platform)
