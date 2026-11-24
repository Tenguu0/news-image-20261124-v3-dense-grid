import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"


def publish():
    target_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not target_dir:
        print("error: MAKEFUN_OUTPUT_DIR is not set", file=sys.stderr)
        return 2
    if not SOURCE.is_file():
        print("error: entry.png is missing next to main.py", file=sys.stderr)
        return 2
    dest = Path(target_dir) / "entry.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, dest)
    print("copied entry.png to", dest)
    return 0


raise SystemExit(publish())
