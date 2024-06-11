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

import sys
from pathlib import Path
from shutil import move

from pypi2rpm.logger import get_logger
from pypi2rpm.util import debug_pprint, run_cmd

logger = get_logger(__name__)


def setup_rpmbuild() -> dict[str, Path]:
    """Set up the 'rpmbuild' directories.

    :return: dict[str, Path].
    """
    logger.info("Setting up the 'rpmbuild' directories")
    top_dir = Path().cwd()
    rpmbuild_dir = top_dir / "rpmbuild"
    rpmbuild_dirs = {
        "_topdir": top_dir,
        "rpmbuild": rpmbuild_dir,
    }
    rpmbuild_dir.mkdir(exist_ok=True)
    for subdir in ["BUILD", "BUILDROOT", "RPMS", "SOURCES", "SPECS", "SRPMS"]:
        rpmbuild_subdir = rpmbuild_dir / subdir
        rpmbuild_dirs[subdir] = rpmbuild_subdir
        rpmbuild_subdir.mkdir(exist_ok=True)
    return rpmbuild_dirs


def run_rpmbuild(spec_file: Path, rpmbuild_dir: Path, dist: str) -> int:
    """Run the 'rpmbuild' command.

    :param spec_file: spec file path
    :param rpmbuild_dir: top-level rpmbuild directory
    :param dist: dist string for rpms
    :return: int.
    """
    logger.info("Running the 'rpmbuild' command on '%s' with dist '%s'", spec_file, dist)
    define_dist = ""
    if dist:
        define_dist = f'--define "dist {dist}"'
    cmd = f'rpmbuild --define "_topdir {rpmbuild_dir}/rpmbuild" {define_dist} -ba {spec_file}'
    exit_code, stdout, stderr = run_cmd(cmd, None)
    debug_pprint(stdout)
    if exit_code:
        logger.error(stderr)
    return exit_code


def run_mock(spec_file: Path, rpmbuild_dir: Path, dist: str, mock_config: str) -> int:
    """Run the 'mock' command.

    :param spec_file: spec file path
    :param rpmbuild_dir: top-level rpmbuild directory
    :param dist: dist string for rpms
    :param mock_config: mock configuration
    :return: int.
    """
    logger.info(
        "Running the 'mock' command on '%s' with dist '%s' and '%s' mock config", spec_file, dist, mock_config
    )
    define_dist = ""
    if dist:
        define_dist = f'--define "dist {dist}"'
    cmd = (
        f"mock {define_dist} --root {mock_config} "
        f"--sources {rpmbuild_dir}/rpmbuild/SOURCES --spec {spec_file}"
    )
    exit_code, stdout, stderr = run_cmd(cmd, None)
    debug_pprint(stdout)
    if exit_code:
        logger.error(stderr)
    result_path = Path("/var/lib/mock") / mock_config / "result"
    src_rpms = result_path.glob("python-*.src.rpm")
    for src_rpm in src_rpms:
        move(str(src_rpm), rpmbuild_dir / "rpmbuild" / "SRPMS" / src_rpm.name)
    bin_rpms = result_path.glob("python3-*.rpm")
    for bin_rpm in bin_rpms:
        cmd = f"rpm -qp --queryformat=%{{ARCH}} {bin_rpm}"
        _, bin_rpm_arch, _ = run_cmd(cmd, None)
        rpm_bin_dir = rpmbuild_dir / "rpmbuild" / "RPMS" / bin_rpm_arch
        rpm_bin_dir.mkdir(exist_ok=True)
        move(str(bin_rpm), rpm_bin_dir / bin_rpm.name)
    for file in result_path.iterdir():
        if not str(file).endswith(".log"):
            logger.critical("Found additional files in '%s'", result_path)
            sys.exit(f"Found additional files in '{result_path}'")
    return exit_code
