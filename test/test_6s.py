import pytest

import sixs_bin


def test_get_path() -> None:
    for version in sixs_bin._SIXS_BINARIES.keys():
        binary = sixs_bin.get_path(version)
        assert binary.is_file()


def test_wrapper() -> None:
    Py6S = pytest.importorskip("Py6S")

    wrapper = sixs_bin.make_wrapper()
    Py6S.SixS.test(wrapper.sixs_path)
