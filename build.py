"""
Build script.

Builds 6S in a temporary directory and installs it as a package resource.
"""
# Copyright (C) 2023 Brian Schubert.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import hashlib
import http
import http.client
import io
import logging
import logging.config
import os
import pathlib
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Final, NamedTuple

# Build script is always invoked from the base directory of the current distribution.
DISTRIBUTION_ROOT: Final = pathlib.Path.cwd()
PACKAGE_ROOT: Final = DISTRIBUTION_ROOT / "src" / "sixs_bin"


class BuildError(RuntimeError):
    """Raised on build failure."""


class SixSTarget(NamedTuple):
    target_name: str
    "Name of this target's compiled 6S binary"

    archive_urls: list[str]
    """
    URL(s) to obtain 6S source archive from. 
    
    To avoid downloading a new copy, configure a cache directory using SIXS_ARCHIVE_DIR.
    """

    archive_sha256: str
    """Expected SHA256 has of the 6S archive file as a 64-character hexstring."""


@dataclass
class BuildConfig:
    archive_dir: pathlib.Path | None = None
    fc_override: str | None = None
    fc_append: str | None = None
    log_file: pathlib.Path | None = None

    @classmethod
    def from_env(cls) -> BuildConfig:
        archive_dir = os.environ.get("SIXS_ARCHIVE_DIR")
        if archive_dir is not None:
            archive_dir = pathlib.Path(archive_dir)

        fc_override = os.environ.get("SIXS_FC_OVERRIDE")
        fc_append = os.environ.get("SIXS_FC_APPEND")

        log_file = os.environ.get("SIXS_BUILD_LOG")
        if log_file is not None:
            log_file = pathlib.Path(log_file)

        return cls(
            archive_dir=archive_dir,
            fc_override=fc_override,
            fc_append=fc_append,
            log_file=log_file,
        )


class WrapFormatter(logging.Formatter):
    indent: str

    def __init__(self, *args: Any, indent=".. ", **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._indent = f"\n{indent}"

    def format(self, record: logging.LogRecord) -> str:
        entry = super().format(record)
        return entry.replace("\n", self._indent)


TARGETS: Final = [
    SixSTarget(
        target_name="sixsV1.1",
        archive_urls=[
            # Mirror from archive.org snapshot.
            "https://web.archive.org/web/20220912090811if_/https://rtwilson.com/downloads/6SV-1.1.tar",
            # From Py6S author's website.
            "https://rtwilson.com/downloads/6SV-1.1.tar",
        ],
        archive_sha256="eedf652e6743b3991b5b9e586da2f55c73f9c9148335a193396bf3893c2bc88f",
    ),
    SixSTarget(
        target_name="sixsV2.1",
        archive_urls=[
            # Mirror from archive.org snapshot.
            "https://web.archive.org/web/20220909154857if_/https://salsa.umd.edu/files/6S/6sV2.1.tar",
            # From SALSA website.
            "https://salsa.umd.edu/files/6S/6sV2.1.tar",
        ],
        archive_sha256="42422db29c095a49eaa98556b416405eb818be1ee30139d2a1913dbf3b0c7de1",
    ),
]


def _url_filename(url: str) -> str:
    """Extract filename from URL."""
    return pathlib.PurePath(urllib.parse.urlparse(url).path).name


def _assert_detect_command(cmd: list[str]) -> None:
    """
    Run the given command in a subprocess and write its outputs to stdout.

    Used to validate that a system dependency is installed and working correctly.
    """
    logger = logging.getLogger(__name__)

    prog = cmd[0]
    try:
        logger.debug(f"running {cmd}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError) as ex:
        raise BuildError(f"unable to run {prog}") from ex
    logger.info(f"detected {prog}:\n{result.stdout.strip()}")


def _resolve_source(
    target: SixSTarget, directory: pathlib.Path, archive_directory: pathlib.Path | None
) -> None:
    """
    Locate or download the given 6S target's source archive, validate it, and extract it
    to the specified directory.

    Raises ``BuildError`` on download or validation failure.
    """
    logger = logging.getLogger(__name__)

    for archive_url in target.archive_urls:
        logger.debug("Trying archive source '%s'", archive_url)
        archive_name = _url_filename(archive_url)

        # Check for cached archive.
        if (
            archive_directory is not None
            and (cached_archive := archive_directory.joinpath(archive_name)).exists()
        ):
            logger.info(f"Using cached source '{cached_archive}'")
            sixs_source = cached_archive.read_bytes()
            break

        # No cached source - download fresh copy.

        logger.debug(
            "no cached archive found for %s in '%s'", archive_name, archive_directory
        )
        logger.info(f"Downloading 6S archive from '{archive_url}'")

        try:
            response: http.client.HTTPResponse = urllib.request.urlopen(archive_url)
        except urllib.error.URLError as ex:
            logger.warning("failed to access '%s'", archive_url, exc_info=ex)
            continue

        if response.status == http.HTTPStatus.OK.value:
            sixs_source = response.read()
            break

        logger.warning(
            f"failed to download 6S archive - got response "
            f"{response.status} {response.reason}"
        )
    else:
        raise BuildError("failed to retrieve 6S source")

    logger.debug("validating archive against expected hash %r", target.archive_sha256)
    digest = hashlib.sha256(sixs_source).hexdigest()
    if digest != target.archive_sha256:
        raise BuildError(
            f"6S archive hash validation failed. "
            f"Expected SHA256={target.archive_sha256}, got SHA256={digest}"
        )

    logger.info(f"Extracting source...")
    logger.debug("Extracting %d byte payload to '%s'", len(sixs_source), directory)
    buffer = io.BytesIO(sixs_source)
    tar_file = tarfile.open(fileobj=buffer, mode="r:")
    tar_file.extractall(directory)


def _install(binary: pathlib.Path, target: pathlib.Path) -> None:
    shutil.copyfile(binary, target)
    # Make sure file has owner execute permissions.
    os.chmod(target, target.stat().st_mode | stat.S_IXUSR)


def build(target: SixSTarget, build_dir: pathlib.Path, config: BuildConfig) -> None:
    """Run build in the given directory."""
    logger = logging.getLogger(__name__)
    logger.debug(
        f"building %s in '{build_dir}' with config %r", target.target_name, config
    )

    binary_dest = PACKAGE_ROOT.joinpath(target.target_name)
    logger.debug(f"destination for %s is '%s'", target.target_name, binary_dest)

    if binary_dest.is_file():
        # Binary already exists in package. Skip rebuilding.
        logger.info(f"target {binary_dest} already exists - skipping build")
        return

    logger.info(f"Resolving 6S source...")
    _resolve_source(target, build_dir, config.archive_dir)
    logger.debug("source contents: %r", sorted(build_dir.glob("**/*")))

    # Make 6S executable.
    logger.info("Building...")
    try:
        # If 6S source contains a directory beginning with 6S, build from that directory.
        (src_dir,) = build_dir.glob("6S*")
    except (FileNotFoundError, ValueError):
        # No 6S* subdirectory. Build from source root.
        src_dir = build_dir
    logger.debug("resolved source directory to be '%s'", src_dir)

    if not src_dir.joinpath("Makefile").exists():
        raise BuildError(f"could not find Makefile in source directory '{src_dir}'")

    fc_override = config.fc_override
    if fc_override is None:
        fc_override = "FC=gfortran -std=legacy -ffixed-line-length-none -ffpe-summary=none $(FFLAGS)"
    if config.fc_append is not None:
        fc_override += f" {config.fc_append}"

    make_command = ["make", "-j", "sixs", fc_override]
    logger.debug("running make command %r", make_command)
    try:
        result = subprocess.run(
            make_command,
            cwd=src_dir,
            capture_output=True,
            check=True,
            text=True,
        )
    except subprocess.CalledProcessError as ex:
        raise BuildError(
            f"make exited with non-zero exit status {ex.returncode}\nstdout:\n{ex.stdout}\nstderr:\n{ex.stderr}",
        ) from ex
    logger.debug("make output\nstdout:\n%s\nstderr:\n%s", result.stdout, result.stderr)

    # Path to built binary.
    sixs_binary = src_dir.joinpath(target.target_name)
    if not sixs_binary.is_file():
        raise BuildError(f"make did not produce binary at '{sixs_binary}'")
    logger.debug(
        "output binary %s has size %d", sixs_binary, sixs_binary.stat().st_size
    )

    # Install 6S executable into package source.
    logger.info("Installing...")
    logger.debug("copying '%s' to '%s'", sixs_binary, binary_dest)
    _install(sixs_binary, binary_dest)


def _setup_logging(log_file: pathlib.Path | None) -> None:
    logger = logging.getLogger(__name__)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        WrapFormatter("{levelname}: {message}", style="{", validate=True)
    )
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    if log_file is not None:
        file_handler = logging.FileHandler(log_file, mode="a")
        file_handler.setFormatter(
            WrapFormatter(
                "[{asctime}] {levelname:7s} {funcName}:{lineno} {message}",
                style="{",
                datefmt="%Y-%m-%d %H:%M:%S",
                validate=True,
            )
        )
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

    logger.setLevel(logging.DEBUG)


def main() -> None:
    """Build script entrypoint."""
    config = BuildConfig.from_env()

    _setup_logging(config.log_file)
    logger = logging.getLogger(__name__)
    logger.info(f"Building from '%s' with config %r", pathlib.Path.cwd(), config)

    # Check system dependencies
    logger.info("Checking system dependencies...")
    _assert_detect_command(["make", "--version"])
    _assert_detect_command(["gfortran", "--version"])

    # Build each 6S target.
    for target in TARGETS:
        logger.info(f"Processing target {target.target_name}")
        with tempfile.TemporaryDirectory() as build_dir:
            build(target, pathlib.Path(build_dir), config)

    logger.info("Build finished normally")


if __name__ == "__main__":
    main()
