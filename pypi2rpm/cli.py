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

from pypi2rpm.logger import debug_pprint, get_logger
from pypi2rpm.pypi import get_pypi_json, write_spec
from pypi2rpm.util import run_cmd
from pypi2rpm.version import version

app_name = "pypi2rpm"


def main() -> int:
    """Top-level code.

    :return: int.
    """
    parser = ArgumentParser()
    parser.add_argument("-L", "--log-level", help="log level name", choices=list(_nameToLevel.keys()))
    parser.add_argument(
        "-V", "--version", help="show version string and exit", action="version", version=version
    )
    parser.add_argument(
        "requirement_specifier",
        help="PyPI (and other indexes) requirement specifier",
    )
    args = parser.parse_args()
    package_name = args.requirement_specifier
    log_level = "WARNING"
    if args.log_level:
        log_level = args.log_level
    logger = get_logger(app_name, log_level)
    logger.debug("'%s' starting", __name__)
    logger.info("Processing package '%s'", package_name)
    cmd = "pip freeze"
    exit_code, stdout, stderr = run_cmd(logger, cmd, None)
    debug_pprint(logger, stdout)
    if stderr:
        logger.error(stderr)
    if exit_code:
        return exit_code
    pypi_data = get_pypi_json(package_name)
    debug_pprint(logger, pypi_data)
    logger.info("Package name: '%s' Package version: '%s'", pypi_data["name"], pypi_data["version"])
    spec_file_name = f"python-{pypi_data['name'].lower()}.spec"
    spec_file = write_spec(spec_file_name, pypi_data)
    logger.info("SPEC file written to '%s'", spec_file)
    return 0


if __name__ == "__main__":
    sys.exit(main())
