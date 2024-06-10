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

from __future__ import annotations

import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from requests import get


def get_pypi_json(package_name: str) -> tuple[dict, dict]:
    """Get the JSON data for a package on PyPI.

    :param package_name: package name
    :return: dict.
    """
    pypi_base_url = "https://pypi.org/pypi"
    pypi_json = get(
        f"{pypi_base_url}/{package_name}/json", headers={"Accept": "application/json"}, timeout=10
    )
    try:
        pypi_info = pypi_json.json()["info"]
    except KeyError as e:
        sys.exit(f"Cannot find {e}")
    pypi_json = get(
        f"{pypi_base_url}/{package_name}/{pypi_info['version']}/json",
        headers={"Accept": "application/json"},
        timeout=10,
    )
    try:
        pypi_info = pypi_json.json()["info"]
    except KeyError as e:
        sys.exit(f"Cannot find {e}")
    try:
        pypi_urls = pypi_json.json()["urls"]
    except KeyError as e:
        sys.exit(f"Cannot find {e}")
    return pypi_info, pypi_urls


def write_spec(spec_file_name: str, pypi_info: dict, pypi_urls: dict) -> tuple[Path, Path]:
    """Write the RPM SPEC file.

    :param spec_file_name: spec file name
    :param pypi_info: PyPI information data
    :param pypi_urls: PyPI url data
    :return: tuple[Path, Path].
    """
    environment = Environment(autoescape=False, loader=FileSystemLoader("pypi2rpm/templates/"))  # noqa: S701
    template = environment.get_template("python-package.spec.j2")
    source_url = None
    for pypi_url in pypi_urls:
        if pypi_url["packagetype"] == "sdist" and pypi_url["python_version"] == "source":
            source_url = pypi_url["url"]
    if not source_url:
        sys.exit(f"Cannot find a source URL for '{pypi_info['name']}'")
    source_file = Path(source_url.split("/")[-1])
    source_data = get(source_url, stream=True, timeout=10)
    with source_file.open("wb") as data:
        for chunk in source_data.iter_content(chunk_size=1024):
            if chunk:
                data.write(chunk)
    content = template.render(
        lc_name=pypi_info["name"].lower(),
        version=pypi_info["version"],
        summary=pypi_info["summary"],
        license=pypi_info["license"],
        home_page=pypi_info["home_page"],
        source_url=source_url,
        description=pypi_info["summary"],
        name=pypi_info["name"],
    )
    spec_file = Path(spec_file_name)
    with spec_file.open(mode="w", encoding="utf-8") as spec:
        spec.write(content)
    return spec_file, source_file
