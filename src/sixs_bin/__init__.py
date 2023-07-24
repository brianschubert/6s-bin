from __future__ import annotations

import importlib.resources
import importlib.metadata
import pathlib
from importlib.abc import Traversable
from typing import TYPE_CHECKING, Final

# Py6S may not be installed.
if TYPE_CHECKING:
    from Py6S import SixS

__version__ = importlib.metadata.version("6s-bin")

_RESOURCE_ROOT: Final[Traversable] = importlib.resources.files(__package__)

_SIXS_BIN: Final[Traversable] = _RESOURCE_ROOT / f"sixsV1.1"


def sixs_bin() -> pathlib.Path:
    """Retrieve the path to the 6S executable from this package's resources."""
    if not isinstance(_SIXS_BIN, pathlib.Path):
        raise RuntimeError(
            f"6S binary package resource represented as non-path resource: {_SIXS_BIN}"
        )

    return _SIXS_BIN


def _import_wrapper() -> type[SixS]:
    try:
        from Py6S import SixS
    except ImportError as ex:
        raise ImportError(
            f"Unable to import Py6S. Make sure it's installed. "
            f"Install 6s-bin with the [wrapper] extra enabled to install "
            f"Py6S automatically."
        ) from ex
    return SixS  # type: ignore


def make_wrapper() -> SixS:
    """
    Create ``Py6s.SixS`` wrapper instance using this package's 6S executable.

    Requires ``Py6S`` to be installed.
    """
    wrapper_class = _import_wrapper()
    return wrapper_class(sixs_bin())


def test_wrapper() -> None:
    """
    Run ``Py6s.SixS.text`` using this package's 6S executable.

    Requires ``Py6S`` to be installed.
    """
    wrapper_class = _import_wrapper()
    wrapper_class.test(sixs_bin())
