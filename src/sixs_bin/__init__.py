"""
Compiled binaries for the 6S Radiative Transfer Model exposed as package resources.
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

import importlib.metadata
import importlib.resources
import pathlib
from importlib.abc import Traversable
from typing import TYPE_CHECKING, Final, Literal

from typing_extensions import TypeAlias

# Py6S may not be installed.
if TYPE_CHECKING:
    from Py6S import SixS

SixSVersion: TypeAlias = Literal["1.1", "2.1"]

DISTRIBUTION_NAME: Final[str] = "6s-bin"

_RESOURCE_ROOT: Final[Traversable] = importlib.resources.files(__package__)

_SIXS_BINARIES: Final[dict[SixSVersion, Traversable]] = {
    "1.1": _RESOURCE_ROOT / "sixsV1.1",
    "2.1": _RESOURCE_ROOT / "sixsV2.1",
}

__version__ = importlib.metadata.version(DISTRIBUTION_NAME)


def get_path(version: SixSVersion) -> pathlib.Path:
    """Retrieve the path to a 6S executable from this package's resources."""

    try:
        binary = _SIXS_BINARIES[version]
    except KeyError as ex:
        raise ValueError(
            f"invalid 6S version '{version}' - must be one of {list(_SIXS_BINARIES.keys())}"
        ) from ex

    if not isinstance(binary, pathlib.Path):
        raise RuntimeError(
            f"6S binary package resource represented as non-path resource: {binary}"
        )

    return binary


def make_wrapper(version: SixSVersion = "1.1") -> SixS:
    """
    Create ``Py6s.SixS`` wrapper instance using the specified 6S executable.

    Defaults to 6S v1.1. Currently, this is the only version that Py6S supports.

    Requires ``Py6S`` to be installed.
    """
    wrapper_class = _import_wrapper()
    return wrapper_class(get_path(version))


def _import_wrapper() -> type[SixS]:
    try:
        from Py6S import SixS
    except ImportError as ex:
        raise ImportError(
            f"Unable to import Py6S. Make sure it's installed. "
            f"Install {DISTRIBUTION_NAME} with the [wrapper] extra enabled to install "
            f"Py6S automatically."
        ) from ex
    return SixS  # type: ignore
