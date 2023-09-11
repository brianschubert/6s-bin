import pathlib
from typing import Final

import pytest

import sixs_bin

TEST_DATA_DIR: Final = pathlib.Path(__file__).resolve().parent.joinpath("data")


@pytest.fixture
def manual_input_file() -> str:
    # Content taken from "6S User Guide Version 3, November 2006, APPENDIX II: EXAMPLES
    # OF INPUTS AND OUTPUTS", available at https://salsa.umd.edu/6spage.html.
    return TEST_DATA_DIR.joinpath("manual_input.txt").read_text()


@pytest.fixture(params=sixs_bin._SIXS_BINARIES.keys())
def sixs_version(request) -> sixs_bin.SixSVersion:
    return request.param  # type: ignore


@pytest.fixture
def sixs_binary(sixs_version) -> pathlib.Path:
    return sixs_bin.get_path(sixs_version)
