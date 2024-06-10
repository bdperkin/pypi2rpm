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
from typing import TYPE_CHECKING

from pypi2rpm.logger import debug_pprint
from pypi2rpm.util import run_cmd

if TYPE_CHECKING:
    from logging import Logger


def setup_rpmbuild() -> dict[str, Path]:
    """Set up the 'rpmbuild' directories.

    :return: dict[str, Path].
    """
    top_dir = Path().cwd()
    rpmbuild_dir = top_dir / "rpmbuild"
    rpmbuild_dirs = {
        "_topdir": top_dir,
        "rpmbuild": rpmbuild_dir,
    }
    if not rpmbuild_dir.exists():
        rpmbuild_dir.mkdir()
    for subdir in ["SOURCES", "SPECS"]:
        rpmbuild_subdir = rpmbuild_dir / subdir
        rpmbuild_dirs[subdir] = rpmbuild_subdir
        if not rpmbuild_subdir.exists():
            rpmbuild_subdir.mkdir()
    return rpmbuild_dirs


def run_rpmbuild(logger: Logger, spec_file: Path, rpmbuild_dir: Path) -> int:
    """Run the 'rpmbuild' command.

    :param logger: output logger
    :param spec_file: spec file path
    :param rpmbuild_dir: top-level rpmbuild directory
    :return: int.
    """
    cmd = f'rpmbuild --define "_topdir {rpmbuild_dir}/rpmbuild" -ba {spec_file}'
    exit_code, stdout, stderr = run_cmd(logger, cmd, None)
    debug_pprint(logger, stdout)
    if stderr:
        logger.error(stderr)
    return exit_code
