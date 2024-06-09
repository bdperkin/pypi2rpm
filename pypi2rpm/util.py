"""Utilities for the pypi2rpm package.

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

from os import environ, set_blocking
from pathlib import Path
from select import EPOLLHUP, EPOLLIN, epoll
from subprocess import PIPE, Popen  # noqa: S404
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger


def run_cmd(logger: Logger, command: str, env_variables: dict[str, str] | None) -> tuple[int, str, str]:
    """Run command in a subprocess.

    :param logger: output logger
    :param command: command to run
    :param env_variables: environmental variables
    :return: tuple[int, str, str]
    """
    environ["PYTHONUNBUFFERED"] = "1"
    if env_variables is None:
        env_variables = {**environ}
    logger.info("Running command '%s'", command)
    with Popen(
        command,
        env={
            **env_variables,
            "PATH": env_variables["PATH"].replace("~", str(Path.home().expanduser())),
        },
        shell=True,  # noqa: S602  # NOTE: security issue
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True,
        universal_newlines=True,
    ) as s_proc:
        # file descriptors for std-out and std-err
        fd_out = s_proc.stdout.fileno()  # type: ignore[union-attr]
        fd_err = s_proc.stderr.fileno()  # type: ignore[union-attr]
        set_blocking(fd_out, False)
        set_blocking(fd_err, False)
        poller = epoll()
        # EPOLLIN   -> Available for read
        # EPOLLHUP  -> Hung up
        poller.register(fd_out, EPOLLIN | EPOLLHUP)
        poller.register(fd_err, EPOLLIN | EPOLLHUP)
        stdout: list[str] = []
        stderr: list[str] = []
        while True:
            # fd -> file descriptor
            # ev -> triggered event
            for fd, ev in poller.poll(timeout=1):
                if ev & EPOLLIN:
                    lines = None
                    if fd == fd_out:
                        lines = s_proc.stdout.readlines()  # type: ignore[union-attr]
                        stdout.extend(lines)
                    elif fd == fd_err:
                        lines = s_proc.stderr.readlines()  # type: ignore[union-attr]
                        stderr.extend(lines)
                    if lines:
                        logger.debug("Command '%s' output:\n%s", command, "".join(lines).rstrip())
                # on hang up unregister
                if ev & EPOLLHUP:
                    poller.unregister(fd)
            # process finished
            if s_proc.poll() is not None:
                break
        exit_code = s_proc.returncode
    return exit_code, "".join(stdout), "".join(stderr)
