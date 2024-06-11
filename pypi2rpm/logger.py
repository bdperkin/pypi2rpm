"""Logging functions for the pypi2rpm package.

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
from logging import Logger

from colorlog import ColoredFormatter, StreamHandler, getLogger

from pypi2rpm import settings


def get_logger(app_name: str) -> Logger:
    """Get the logger.

    :param app_name: application name
    :return: Logger.
    """
    fmt = "%(log_color)s%(levelname)-8s%(reset)s %(log_color)s%(name)-8s%(reset)s %(log_color)s%(message)s"
    formatter = ColoredFormatter(
        fmt,
        datefmt=None,
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
        secondary_log_colors={},
        style="%",
    )
    handler = StreamHandler()
    handler.setFormatter(formatter)
    logger = getLogger(app_name)
    logger.addHandler(handler)
    try:
        logger.setLevel(settings.log_level)
    except ValueError as e:
        logger.critical(e)
        sys.exit(1)
    logger.debug("Logger for '%s' started at the '%s' level", app_name, settings.log_level)
    return logger
