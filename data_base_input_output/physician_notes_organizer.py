#!/usr/bin/env python3
"""
organize_physician_notes.py

For each immediate subdirectory of PARENT_DIR:
  1) create a 'physician_notes' folder
  2) if '1.pdf' exists, rename it to 'Scan2.pdf' inside physician_notes
  3) move all other .pdf files into physician_notes
"""

import argparse
from pathlib import Path
import shutil
import sys

def main():
    parser = argparse.ArgumentParser(
        description="Organize PDF files into physician_notes folders."
    )
    parser.add_argument(
        "parent_dir",
        type=Path,
        help="Path to the parent directory containing subdirectories."
    )
    args = parser.parse_args()
    parent_dir = args.parent_dir

    if not parent_dir.is_dir():
        print(f"Error: {parent_dir!r} is not a directory.", file=sys.stderr)
        sys.exit(1)

    for subdir in parent_dir.iterdir():
        if not subdir.is_dir():
            continue

        notes_dir = subdir / "physician_notes"
        notes_dir.mkdir(exist_ok=True)

        # 1) Rename '1.pdf' → 'Scan2.pdf' inside physician_notes
        one_pdf = subdir / "1.pdf"
        if one_pdf.is_file():
            target = notes_dir / "Scan2.pdf"
            one_pdf.rename(target)
            print(f"Renamed: {one_pdf.name} → {target.relative_to(subdir)}")

        # 2) Move all remaining *.pdf files into physician_notes
        for f in subdir.iterdir():
            if f.is_file() and f.suffix.lower() == ".pdf":
                dest = notes_dir / f.name
                shutil.move(str(f), str(dest))
                print(f"Moved: {f.name} → {notes_dir.name}/")

if __name__ == "__main__":
    main()
