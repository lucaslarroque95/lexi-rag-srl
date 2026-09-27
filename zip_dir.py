#!/usr/bin/env python3
"""Zips a directory's contents (relative paths, no zip CLI needed — some
build machines don't have it). Usage: zip_dir.py <src_dir> <out_zip>"""
import sys
import zipfile
from pathlib import Path


def main() -> None:
    src_dir, out_zip = Path(sys.argv[1]), Path(sys.argv[2])
    out_zip.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(src_dir.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(src_dir))


if __name__ == "__main__":
    main()
