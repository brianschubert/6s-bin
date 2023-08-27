import re
import subprocess
from typing import Final

import pytest

import sixs_bin

# Taken from "6S User Guide Version 3, November 2006, APPENDIX II: EXAMPLES OF INPUTS
# AND OUTPUTS", available at https://salsa.umd.edu/6spage.html.
INPUT_FILE: Final = """\
0                           (User-defined geometric conditions)
40.0 100.0 45.0 50.0 7 23   (SZA, SAZ, VZA, VAZ, month, day)
8                           (User-defined molecular atmosphere model)
3.0 3.5                     (Contents of H2O-vapor (g/cm^2) & 0 3 (cm-atm))
4                           (Aerosol model)
0.25 0.25 0.25 0.25         (% of dust-like, water-soluble, oceanic, & soot)
0                           (Input of aerosol opt. thickness instead of visibility)
0.5                         (Aerosol optical thickness at 550 nm)
-0.2                        (Target at 0.2 km above the sea level)
-3.3                        (Aircraft at 3.3 km above the ground level)
-1.5 -3.5                   (H2O-vapor & O3 under the aircraft are not available)
0.25                        (Aerosol opt. thickness under the aircraft at 550 nm)
11                          (AVHRR 1 (NOAA 9) Band)
1                           (Non-uniform ground surface)
2 1 0.5                     (Target reflect., environ. reflect., target radius (km))
1                           (Request for atmospheric correction)
-0.1                        (Parameter of the atmospheric correction)
4                           (Ground surface is not polarized)
"""


def test_get_path() -> None:
    for version in sixs_bin._SIXS_BINARIES.keys():
        binary = sixs_bin.get_path(version)
        assert binary.is_file()


def test_basic_run() -> None:
    for version in sixs_bin._SIXS_BINARIES.keys():
        binary = sixs_bin.get_path(version)

        result = subprocess.run(
            [binary],
            input=INPUT_FILE,
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
        assert version_match.group(1) == binary.name[5:]

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
    Py6S = pytest.importorskip("Py6S")

    wrapper = sixs_bin.make_wrapper()
    Py6S.SixS.test(wrapper.sixs_path)
