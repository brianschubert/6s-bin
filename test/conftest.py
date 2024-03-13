from __future__ import annotations

import math
import pathlib
import re
from typing import Any, Final

import pytest

import sixs_bin

TEST_DATA_DIR: Final = pathlib.Path(__file__).resolve().parent.joinpath("data")


NUMBER_PATTERN: Final = re.compile(r"-?[0-9]+(?:\.[0-9+]+)?")


@pytest.fixture()
def manual_input_file() -> str:
    # Content taken from "6S User Guide Version 3, November 2006, APPENDIX II: EXAMPLES
    # OF INPUTS AND OUTPUTS", available at https://salsa.umd.edu/6spage.html.
    return TEST_DATA_DIR.joinpath("manual_input.txt").read_text()


@pytest.fixture(params=sixs_bin._SIXS_BINARIES.keys())
def sixs_version(request) -> sixs_bin.SixSVersion:
    return request.param  # type: ignore


@pytest.fixture()
def sixs_binary(sixs_version) -> pathlib.Path:
    return sixs_bin.get_path(sixs_version)


@pytest.fixture()
def helpers() -> type[Helpers]:
    return Helpers


class Helpers:
    """
    Hack to make helper functions available to tests without fiddling with the
    import path.
    """

    @staticmethod
    def assert_embedded_isclose(s1: str, s2: str, **kwargs: Any) -> None:
        """
        Asserts than all embedded numbers between the two given strings are close
        in value.

        Does not consider the formatting of the two strings outside the number of
        embedded numbers they contain. So, for example, this function considers the
        strings "1 2" and "foo1 and2bar" to match.
        """
        if s1 == s2:
            return

        embedded_s1 = [float(num) for num in NUMBER_PATTERN.findall(s1)]
        embedded_s2 = [float(num) for num in NUMBER_PATTERN.findall(s2)]

        assert len(embedded_s1) == len(embedded_s2), (
            f"strings {s1=!r} and {s2=!r} contain a different number of embedded"
            f" numbers ({len(embedded_s1)} vs {len(embedded_s2)})"
        )

        for left_num, right_num in zip(embedded_s1, embedded_s2):
            assert math.isclose(left_num, right_num, **kwargs), (
                "embedded numbers do not agree within tolerance between"
                f" strings {s1=!r} and {s2=!r}"
            )
