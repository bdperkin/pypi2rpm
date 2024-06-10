"""The RPM Package Manager (RPM) functions for the pypi2rpm package.

Copyright 2024 Brandon Perkins

This file is part of pypi2rpm.

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, see
<http://www.gnu.org/licenses/>.
"""

from __future__ import annotations

from pathlib import Path


def setup_rpmbuild() -> dict[str, Path]:
    """Set up the 'rpmbuild' directories.

    :return: dict[str, Path].
    """
    rpmbuild_dir = Path().cwd() / "rpmbuild"
    rpmbuild_dirs = {
        "_topdir": rpmbuild_dir,
    }
    if not rpmbuild_dir.exists():
        rpmbuild_dir.mkdir()
    for subdir in ["SOURCES", "SPECS"]:
        rpmbuild_subdir = rpmbuild_dir / subdir
        rpmbuild_dirs[subdir] = rpmbuild_subdir
        if not rpmbuild_subdir.exists():
            rpmbuild_subdir.mkdir()
    return rpmbuild_dirs
