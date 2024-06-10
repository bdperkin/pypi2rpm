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
import tarfile
from datetime import datetime, timezone
from hashlib import md5
from typing import TYPE_CHECKING

from jinja2 import Environment, FileSystemLoader
from requests import get

from pypi2rpm.logger import debug_pprint
from pypi2rpm.util import run_cmd

if TYPE_CHECKING:
    from logging import Logger
    from pathlib import Path


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


def get_source(sources_dir: Path, pypi_info: dict, pypi_urls: dict) -> tuple[str, Path, str]:
    """Get the source archive and file.

    :param sources_dir: sources rpmbuild directory
    :param pypi_info: PyPI information data
    :param pypi_urls: PyPI url data
    :return: tuple[str, Path].
    """
    source_url = None
    source_md5 = None
    for pypi_url in pypi_urls:
        if pypi_url["packagetype"] == "sdist" and pypi_url["python_version"] == "source":
            source_url = pypi_url["url"]
            source_md5 = pypi_url["md5_digest"]
    if not source_url or not source_md5:
        sys.exit(f"Cannot find a source URL or MD5SUM for '{pypi_info['name']}'")
    source_file = sources_dir / source_url.split("/")[-1]
    if source_file.exists():
        md5sum = md5(source_file.open("rb").read()).hexdigest()  # noqa: S324
        if md5sum != source_md5:
            source_file.unlink()
    if not source_file.exists():
        source_data = get(source_url, stream=True, timeout=10)
        with source_file.open("wb") as data:
            for chunk in source_data.iter_content(chunk_size=1024):
                if chunk:
                    data.write(chunk)
        md5sum = md5(source_file.open("rb").read()).hexdigest()  # noqa: S324
        if md5sum != source_md5:
            source_file.unlink()
            sys.exit(f"MD5SUM of file '{source_file}' does not match '{source_md5}'")
    tar = tarfile.open(source_file)
    extract_dir = tar.getnames()[0].split("/")[0]
    return source_url, source_file, extract_dir


def write_spec(
    logger: Logger, spec_file: Path, sources_dir: Path, pypi_info: dict, pypi_urls: dict
) -> tuple[Path, Path]:
    """Write the RPM SPEC file.

    :param logger: output logger
    :param spec_file: spec file path
    :param sources_dir: sources rpmbuild directory
    :param pypi_info: PyPI information data
    :param pypi_urls: PyPI url data
    :return: tuple[Path, Path].
    """
    environment = Environment(autoescape=False, loader=FileSystemLoader("pypi2rpm/templates/"))  # noqa: S701
    template = environment.get_template("python-package.spec.j2")
    source_url, source_file, extract_dir = get_source(sources_dir, pypi_info, pypi_urls)
    license_name = "GPL-2.0-or-later"
    if pypi_info["license"]:
        license_name = pypi_info["license"]
    home_page = pypi_info["home_page"]
    if not home_page:
        home_page = pypi_info["project_url"]
    cmd = "rpmdev-packager"
    exit_code, stdout, stderr = run_cmd(logger, cmd, None)
    debug_pprint(logger, stdout)
    if stderr:
        logger.error(stderr)
    if exit_code:
        sys.exit("Cannot get RPM packager")
    rpmdev_packager = stdout.rstrip()
    content = template.render(
        name=pypi_info["name"].lower(),
        version=pypi_info["version"],
        summary=pypi_info["summary"],
        license=license_name,
        home_page=home_page,
        source_url=source_url,
        description=pypi_info["summary"],
        extract_dir=extract_dir,
        date=datetime.now(timezone.utc).strftime("%a %b %d %Y"),
        rpmdev_packager=rpmdev_packager,
    )
    with spec_file.open(mode="w", encoding="utf-8") as spec:
        spec.write(content)
    return spec_file, source_file
