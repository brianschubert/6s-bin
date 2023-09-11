import re
import subprocess

import pytest

import sixs_bin


def test_get_path(sixs_binary) -> None:
    """Verify that 6S binary file exists."""
    assert sixs_binary.is_file()


def test_basic_run(sixs_binary, manual_input_file) -> None:
    """Perform a basic 6S simulation and check that the output format looks correct."""
    result = subprocess.run(
        [sixs_binary],
        input=manual_input_file,
        capture_output=True,
        check=True,
        text=True,
        encoding="ascii",
    )
    output_lines = result.stdout.strip().splitlines()

    # Verify that 6S version indicated in output matches the expected binary version.
    version_match = re.match(
        r"^\*+ 6SV version ([\w.]+) \*+$", output_lines[0], flags=re.ASCII
    )
    if version_match is None:
        pytest.fail(
            f"6S malformed output - could not find version in first"
            f" non-whitespace output line: '{output_lines[0]}'"
        )
    assert version_match.group(1) == sixs_binary.name[5:]

    # Check a single line in the output.

    gas_marker = "global gas. trans."
    for line in result.stdout.strip().splitlines():
        if gas_marker in line:
            gas_line = line
            break
    else:
        pytest.fail(
            f"6S output malformed - could not find line containing {gas_marker} line"
        )

    # Extract global gas transmittance values.
    gas_match = re.match(
        r"^\*[^:]+:\s+(\d+.\d+)\s+(\d+.\d+)\s+(\d+.\d+)\s+\*$",
        gas_line,
        flags=re.ASCII,
    )
    if gas_match is None:
        pytest.fail(f"6S output malformed - line has bad format: '{gas_line}'")
    downward, upward, total = gas_match.groups()

    # Expected output values for sample input from 6S user guide.
    assert downward == "0.68965"
    assert upward == "0.97248"
    assert total == "0.67513"


def test_wrapper() -> None:
    """Verify that ``Py6S.SixS.test`` run successfully if ``Py6S`` is available."""
    Py6S = pytest.importorskip("Py6S")

    wrapper = sixs_bin.make_wrapper()
    assert Py6S.SixS.test(wrapper.sixs_path) == 0
