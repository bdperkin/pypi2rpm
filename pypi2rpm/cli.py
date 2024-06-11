"""Command-line interface for the pypi2rpm package.

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

import sys
from argparse import ArgumentParser
from logging import _nameToLevel  # noqa: PLC2701
from pathlib import Path

from pypi2rpm.logger import debug_pprint, get_logger
from pypi2rpm.pypi import get_pypi_json, write_spec
from pypi2rpm.rpm import run_mock, run_rpmbuild, setup_rpmbuild
from pypi2rpm.version import version

app_name = "pypi2rpm"


def main() -> int:
    """Top-level code.

    :return: int.
    """
    mock_cfgs = []
    mock_path = Path("/etc/mock")
    if mock_path.exists() and mock_path.is_dir():
        mock_cfgs = [x.stem for x in mock_path.glob("*-x86_64.cfg")]
    parser = ArgumentParser()
    parser.add_argument("--dist", help="'dist' string for rpms")
    parser.add_argument("-L", "--log-level", help="log level name", choices=list(_nameToLevel.keys()))
    parser.add_argument("-M", "--mock", help="use 'mock' instead of 'rpmbuild'", choices=sorted(mock_cfgs))
    parser.add_argument(
        "-V", "--version", help="show version string and exit", action="version", version=version
    )
    parser.add_argument(
        "requirement_specifier",
        help="PyPI (and other indexes) requirement specifier",
    )
    args = parser.parse_args()
    package_name = args.requirement_specifier
    dist = ""
    if args.dist:
        dist = args.dist
    log_level = "WARNING"
    if args.log_level:
        log_level = args.log_level
    logger = get_logger(app_name, log_level)
    logger.debug("'%s' starting", __name__)
    logger.info("Processing package '%s'", package_name)
    mock_config = None
    if args.mock:
        mock_config = args.mock
    rpmbuild_dirs = setup_rpmbuild()
    pypi_info, pypi_urls = get_pypi_json(package_name)
    debug_pprint(logger, pypi_info)
    debug_pprint(logger, pypi_urls)
    logger.info("Package name: '%s' Package version: '%s'", pypi_info["name"], pypi_info["version"])
    spec_file = rpmbuild_dirs["SPECS"] / f"python-{pypi_info['name'].lower()}.spec"
    spec_file, source_file = write_spec(logger, spec_file, rpmbuild_dirs["SOURCES"], pypi_info, pypi_urls)
    logger.info("SPEC file written to '%s' Source file written to '%s'", spec_file, source_file)
    if mock_config:
        return run_mock(logger, spec_file, rpmbuild_dirs["_topdir"], dist)
    return run_rpmbuild(logger, spec_file, rpmbuild_dirs["_topdir"], dist)


if __name__ == "__main__":
    sys.exit(main())
