# -*- coding: utf-8 -*-
#
#   pyrayopt - raytracing for optical imaging systems
#   Copyright (C) 2012 Robert Jordens <jordens@phys.ethz.ch>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Desktop organizer: automatically sort desktop files into categorized folders.

Organization rules
------------------
Files on the desktop are moved into sub-folders based on their extension:

============  ======================================================
Folder        Extensions
============  ======================================================
Images        jpg jpeg png gif bmp svg ico tiff tif webp heic
Documents     pdf doc docx xls xlsx ppt pptx txt md rst csv odt ods
Videos        mp4 mkv avi mov wmv flv webm m4v
Music         mp3 wav flac aac ogg m4a wma
Code          py js ts html css java cpp c h go rs rb php swift kt
Archives      zip rar tar gz bz2 7z xz
Others        any extension not matched above
============  ======================================================

Directories and hidden files (names starting with ``.``) are skipped.

Usage::

    from rayopt.desktop_organizer import DesktopOrganizer
    organizer = DesktopOrganizer()
    # Preview what would be moved (dry run):
    organizer.organize(dry_run=True)
    # Actually move the files:
    organizer.organize()

Command-line usage::

    python -m rayopt.desktop_organizer [--desktop PATH] [--dry-run]
"""

from __future__ import absolute_import, print_function, unicode_literals

import os
import shutil
import argparse
from pathlib import Path

# ---------------------------------------------------------------------------
# Category definitions: folder name -> set of lower-case extensions
# ---------------------------------------------------------------------------
CATEGORIES = {
    "Images": {
        "jpg", "jpeg", "png", "gif", "bmp", "svg", "ico",
        "tiff", "tif", "webp", "heic",
    },
    "Documents": {
        "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx",
        "txt", "md", "rst", "csv", "odt", "ods",
    },
    "Videos": {
        "mp4", "mkv", "avi", "mov", "wmv", "flv", "webm", "m4v",
    },
    "Music": {
        "mp3", "wav", "flac", "aac", "ogg", "m4a", "wma",
    },
    "Code": {
        "py", "js", "ts", "html", "css", "java", "cpp", "c",
        "h", "go", "rs", "rb", "php", "swift", "kt",
    },
    "Archives": {
        "zip", "rar", "tar", "gz", "bz2", "7z", "xz",
    },
}

# Fallback category for unrecognised extensions
OTHERS_FOLDER = "Others"


def _get_default_desktop():
    """Return the platform-specific default desktop path."""
    return Path.home() / "Desktop"


def _classify(extension):
    """Return the folder name for the given file extension (without dot).

    Parameters
    ----------
    extension : str
        File extension without leading dot, e.g. ``"jpg"``.

    Returns
    -------
    str
        The destination folder name.
    """
    ext = extension.lower()
    for folder, extensions in CATEGORIES.items():
        if ext in extensions:
            return folder
    return OTHERS_FOLDER


def _unique_path(destination):
    """Return *destination* or a numbered variant if the path already exists.

    Parameters
    ----------
    destination : Path
        The desired destination path.

    Returns
    -------
    Path
        A path that does not yet exist on the filesystem.
    """
    if not destination.exists():
        return destination
    stem = destination.stem
    suffix = destination.suffix
    parent = destination.parent
    counter = 1
    while True:
        candidate = parent / "{}_{}{}".format(stem, counter, suffix)
        if not candidate.exists():
            return candidate
        counter += 1


class DesktopOrganizer:
    """Organizes files on the desktop into categorized sub-folders.

    Parameters
    ----------
    desktop_path : str or Path, optional
        Path to the desktop directory.  Defaults to ``~/Desktop``.
    """

    def __init__(self, desktop_path=None):
        if desktop_path is None:
            self.desktop_path = _get_default_desktop()
        else:
            self.desktop_path = Path(desktop_path)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def scan(self):
        """List all files on the desktop that would be organised.

        Hidden files (starting with ``.``) and directories are excluded.

        Returns
        -------
        list of Path
            Files eligible for organisation.
        """
        return [
            p for p in self.desktop_path.iterdir()
            if p.is_file() and not p.name.startswith(".")
        ]

    def plan(self):
        """Return a mapping of source file to intended destination path.

        Returns
        -------
        list of (Path, Path)
            Each tuple is ``(source, destination)`` with the destination
            inside the appropriate category sub-folder.
        """
        moves = []
        for src in self.scan():
            folder = _classify(src.suffix.lstrip("."))
            dst_dir = self.desktop_path / folder
            dst = _unique_path(dst_dir / src.name)
            moves.append((src, dst))
        return moves

    def organize(self, dry_run=False):
        """Move files into their category sub-folders.

        Parameters
        ----------
        dry_run : bool, optional
            When ``True``, print what *would* be moved without actually
            moving anything.  Defaults to ``False``.

        Returns
        -------
        list of (Path, Path)
            Each tuple is ``(source, destination)`` for every file that
            was (or would be) moved.
        """
        moves = self.plan()
        for src, dst in moves:
            if dry_run:
                print("[dry-run] {} -> {}".format(src, dst))
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
                print("Moved: {} -> {}".format(src, dst))
        if not moves:
            print("Desktop is already clean – nothing to organize.")
        return moves


# ---------------------------------------------------------------------------
# Command-line entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Automatically organise desktop files into sub-folders."
    )
    parser.add_argument(
        "--desktop",
        default=None,
        help="Path to the desktop directory (default: ~/Desktop).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be moved without making any changes.",
    )
    args = parser.parse_args()
    organizer = DesktopOrganizer(desktop_path=args.desktop)
    organizer.organize(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
