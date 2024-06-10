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
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
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


def write_spec(spec_file_name: str, pypi_data: dict) -> Path:
    """Write the RPM SPEC file.

    :param spec_file_name: spec file name
    :param pypi_data: PyPI data
    :return: str.
    """
    environment = Environment(autoescape=True, loader=FileSystemLoader("pypi2rpm/templates/"))
    template = environment.get_template("python-package.spec.j2")
    content = template.render(pypi_data)
    spec_file = Path(spec_file_name)
    with spec_file.open(mode="w", encoding="utf-8") as message:
        message.write(content)
        return spec_file
