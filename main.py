"""Entry program for the dense-grid front page of 24 November 2026.

The composed page lives next to this file as ``entry.png``.  This
script only hands that file over to the harness: it copies it into
the directory named by ``MAKEFUN_OUTPUT_DIR`` and reports the path
it wrote.  Nothing is generated here, nothing is fetched, and the
run is byte-for-byte repeatable.
"""

import os
import shutil
import sys
from pathlib import Path

PAGE_NAME = "entry.png"


def publish() -> int:
    here = Path(__file__).resolve().parent
    page = here / PAGE_NAME
    if not page.is_file():
        print(f"missing {PAGE_NAME} beside {__file__}", file=sys.stderr)
        return 2
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        print("MAKEFUN_OUTPUT_DIR is not set", file=sys.stderr)
        return 2
    target = Path(out_dir) / PAGE_NAME
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(page, target)
    print(target)
    return 0


raise SystemExit(publish())
