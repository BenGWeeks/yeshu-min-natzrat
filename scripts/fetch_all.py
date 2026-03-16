"""Run all fetch scripts to populate chapters/ and appendices/ directories."""

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent

SCRIPTS = [
    "fetch_web_texts.py",
    "fetch_thomas.py",
    "fetch_mary.py",
    "fetch_apocryphon_james.py",
    "fetch_didache.py",
    "fetch_hymn_pearl.py",
    "fetch_philip_mary.py",
]


def main():
    failed = []
    for script in SCRIPTS:
        path = SCRIPTS_DIR / script
        print(f"\n{'='*60}")
        print(f"Running {script}...")
        print(f"{'='*60}")
        result = subprocess.run(
            [sys.executable, str(path)],
            capture_output=False,
        )
        if result.returncode != 0:
            print(f"FAILED: {script}")
            failed.append(script)

    print(f"\n{'='*60}")
    if failed:
        print(f"Failed scripts: {', '.join(failed)}")
        sys.exit(1)
    else:
        print("All scripts completed successfully.")


if __name__ == "__main__":
    main()
