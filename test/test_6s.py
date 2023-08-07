import pytest

import sixs_bin


def test_wrapper() -> None:
    _ = pytest.importorskip("Py6S")
    sixs_bin.test_wrappers()
