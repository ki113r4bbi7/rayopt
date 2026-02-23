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

from __future__ import absolute_import, print_function, unicode_literals

import os
import tempfile
import unittest
from pathlib import Path

from rayopt.desktop_organizer import (
    CATEGORIES,
    OTHERS_FOLDER,
    DesktopOrganizer,
    _classify,
    _unique_path,
)


class ClassifyTest(unittest.TestCase):
    """Tests for the _classify helper."""

    def test_image_extensions(self):
        for ext in ("jpg", "jpeg", "png", "gif", "bmp", "svg",
                    "ico", "tiff", "tif", "webp", "heic"):
            self.assertEqual(_classify(ext), "Images",
                             "expected Images for .{}".format(ext))

    def test_document_extensions(self):
        for ext in ("pdf", "doc", "docx", "xls", "xlsx", "ppt",
                    "pptx", "txt", "md", "rst", "csv", "odt", "ods"):
            self.assertEqual(_classify(ext), "Documents")

    def test_video_extensions(self):
        for ext in ("mp4", "mkv", "avi", "mov", "wmv", "flv", "webm", "m4v"):
            self.assertEqual(_classify(ext), "Videos")

    def test_music_extensions(self):
        for ext in ("mp3", "wav", "flac", "aac", "ogg", "m4a", "wma"):
            self.assertEqual(_classify(ext), "Music")

    def test_code_extensions(self):
        for ext in ("py", "js", "ts", "html", "css", "java", "cpp",
                    "c", "h", "go", "rs", "rb", "php", "swift", "kt"):
            self.assertEqual(_classify(ext), "Code")

    def test_archive_extensions(self):
        for ext in ("zip", "rar", "tar", "gz", "bz2", "7z", "xz"):
            self.assertEqual(_classify(ext), "Archives")

    def test_unknown_extension_falls_back_to_others(self):
        self.assertEqual(_classify("xyz"), OTHERS_FOLDER)
        self.assertEqual(_classify(""), OTHERS_FOLDER)

    def test_case_insensitive(self):
        self.assertEqual(_classify("JPG"), "Images")
        self.assertEqual(_classify("PDF"), "Documents")
        self.assertEqual(_classify("MP3"), "Music")


class UniquePathTest(unittest.TestCase):
    """Tests for the _unique_path helper."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_no_conflict(self):
        p = Path(self.tmp) / "file.txt"
        result = _unique_path(p)
        self.assertEqual(result, p)

    def test_conflict_adds_counter(self):
        p = Path(self.tmp) / "file.txt"
        p.touch()
        result = _unique_path(p)
        self.assertEqual(result, Path(self.tmp) / "file_1.txt")

    def test_multiple_conflicts(self):
        p = Path(self.tmp) / "file.txt"
        p.touch()
        (Path(self.tmp) / "file_1.txt").touch()
        result = _unique_path(p)
        self.assertEqual(result, Path(self.tmp) / "file_2.txt")


class DesktopOrganizerTest(unittest.TestCase):
    """Integration tests for DesktopOrganizer."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.desktop = Path(self.tmp)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _create_file(self, name):
        p = self.desktop / name
        p.write_text("test content")
        return p

    def test_scan_returns_only_files(self):
        self._create_file("photo.jpg")
        self._create_file("notes.txt")
        # create a sub-directory – should be excluded from scan
        (self.desktop / "subdir").mkdir()
        organizer = DesktopOrganizer(self.desktop)
        scanned = organizer.scan()
        names = {p.name for p in scanned}
        self.assertIn("photo.jpg", names)
        self.assertIn("notes.txt", names)
        self.assertNotIn("subdir", names)

    def test_scan_excludes_hidden_files(self):
        self._create_file(".hidden_file")
        self._create_file("visible.txt")
        organizer = DesktopOrganizer(self.desktop)
        names = {p.name for p in organizer.scan()}
        self.assertNotIn(".hidden_file", names)
        self.assertIn("visible.txt", names)

    def test_plan_maps_files_to_correct_category(self):
        self._create_file("photo.jpg")
        self._create_file("report.pdf")
        self._create_file("video.mp4")
        self._create_file("song.mp3")
        self._create_file("script.py")
        self._create_file("archive.zip")
        self._create_file("random.xyz")
        organizer = DesktopOrganizer(self.desktop)
        mapping = {src.name: dst.parent.name for src, dst in organizer.plan()}
        self.assertEqual(mapping["photo.jpg"], "Images")
        self.assertEqual(mapping["report.pdf"], "Documents")
        self.assertEqual(mapping["video.mp4"], "Videos")
        self.assertEqual(mapping["song.mp3"], "Music")
        self.assertEqual(mapping["script.py"], "Code")
        self.assertEqual(mapping["archive.zip"], "Archives")
        self.assertEqual(mapping["random.xyz"], OTHERS_FOLDER)

    def test_dry_run_does_not_move_files(self):
        self._create_file("photo.jpg")
        organizer = DesktopOrganizer(self.desktop)
        organizer.organize(dry_run=True)
        # File must still be in place after a dry run
        self.assertTrue((self.desktop / "photo.jpg").exists())
        self.assertFalse((self.desktop / "Images" / "photo.jpg").exists())

    def test_organize_moves_files(self):
        self._create_file("photo.jpg")
        self._create_file("notes.txt")
        organizer = DesktopOrganizer(self.desktop)
        organizer.organize()
        self.assertFalse((self.desktop / "photo.jpg").exists())
        self.assertTrue((self.desktop / "Images" / "photo.jpg").exists())
        self.assertFalse((self.desktop / "notes.txt").exists())
        self.assertTrue((self.desktop / "Documents" / "notes.txt").exists())

    def test_organize_creates_category_directories(self):
        self._create_file("photo.png")
        organizer = DesktopOrganizer(self.desktop)
        organizer.organize()
        self.assertTrue((self.desktop / "Images").is_dir())

    def test_organize_handles_duplicate_filenames(self):
        self._create_file("photo.jpg")
        # Pre-create a file in Images with the same name
        (self.desktop / "Images").mkdir()
        (self.desktop / "Images" / "photo.jpg").write_text("existing")
        organizer = DesktopOrganizer(self.desktop)
        organizer.organize()
        # Original destination already taken – organizer must use a numbered name
        self.assertTrue((self.desktop / "Images" / "photo_1.jpg").exists())

    def test_organize_returns_move_list(self):
        self._create_file("song.mp3")
        organizer = DesktopOrganizer(self.desktop)
        moves = organizer.organize()
        self.assertEqual(len(moves), 1)
        src, dst = moves[0]
        self.assertEqual(src.name, "song.mp3")
        self.assertEqual(dst.parent.name, "Music")

    def test_organize_empty_desktop(self):
        organizer = DesktopOrganizer(self.desktop)
        moves = organizer.organize()
        self.assertEqual(moves, [])


if __name__ == "__main__":
    unittest.main()
