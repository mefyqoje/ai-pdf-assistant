import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"


if __name__ == "__main__":
    environment = os.environ.copy()

    current_pythonpath = environment.get("PYTHONPATH", "")

    if current_pythonpath:
        environment["PYTHONPATH"] = (
            f"{SRC_DIR}{os.pathsep}{current_pythonpath}"
        )
    else:
        environment["PYTHONPATH"] = str(SRC_DIR)

    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(PROJECT_ROOT / "app" / "streamlit_app.py"),
        ],
        check=True,
        cwd=PROJECT_ROOT,
        env=environment,
    )