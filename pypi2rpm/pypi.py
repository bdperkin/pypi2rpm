"""The Python Package Index (PyPI) functions for the pypi2rpm package.

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

from requests import get


def get_pypi_json(package_name: str) -> dict:
    """Get the JSON data for a package on PyPI.

    :param package_name: package name
    :return: dict.
    """
    pypi_base_url = "https://pypi.org/pypi"
    pypi_json = get(
        f"{pypi_base_url}/{package_name}/json", headers={"Accept": "application/json"}, timeout=10
    )
    try:
        pypi_data = pypi_json.json()["info"]
    except KeyError as e:
        sys.exit(f"Cannot find {e}")
    return pypi_data
