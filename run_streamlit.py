import os
import subprocess
import sys


if __name__ == "__main__":
    os.environ["PYTHONPATH"] = "src"

    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app/streamlit_app.py",
        ],
        check=True,
    )