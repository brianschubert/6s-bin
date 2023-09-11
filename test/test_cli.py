import subprocess
import sys
from typing import Any

import pytest

import sixs_bin
import sixs_bin._cli as sixs_cli


def _run_self_subprocess(
    cli_args: list[str], **kwargs: Any
) -> subprocess.CompletedProcess[Any]:
    """
    Run the command line interface in a subprocess.

    Needed instead of calling the CLI entrypoint directly when more advanced control
    over the process running the command line interface is required.
    """
    return subprocess.run(
        [sys.executable, "-m", sixs_bin.__name__, *cli_args], **kwargs
    )


def test_version(capsys) -> None:
    """Verify that ``--version`` flag prints version information and exits."""
    sixs_cli.main(["--version"])

    captured = capsys.readouterr()
    assert captured.out.strip() == sixs_cli._make_version()
    assert captured.err == ""


def test_good_path(sixs_version, capsys) -> None:
    """Verify that ``--path`` output matches the request binaries path."""
    sixs_cli.main(["--path", sixs_version])

    captured = capsys.readouterr()
    assert captured.out == f"{sixs_bin.get_path(sixs_version)}\n"
    assert captured.err == ""


def test_bad_path() -> None:
    """Verify that the CLI exits with error on bad ``--path`` arguments."""
    with pytest.raises(SystemExit):
        sixs_cli.main(["--path", "does-not-exist"])

    with pytest.raises(SystemExit):
        sixs_cli.main(["--path"])


def test_exec_matches(sixs_version, manual_input_file, helpers) -> None:
    """
    Verify that output when using ``--exec`` exactly matches the output of directly
    calling the binary.
    """
    proc_args = {
        "input": manual_input_file,
        "capture_output": True,
        "check": True,
        "text": True,
        "encoding": "ascii",
    }

    direct_result = subprocess.run([sixs_bin.get_path(sixs_version)], **proc_args)

    cli_result = _run_self_subprocess(["--exec", sixs_version], **proc_args)

    assert direct_result.returncode == cli_result.returncode
    assert direct_result.stderr == cli_result.stderr

    direct_lines = direct_result.stdout.splitlines()
    cli_lines = cli_result.stdout.splitlines()
    assert len(direct_lines) == len(cli_lines)

    # Use more generous tolerance on macOS, where rounding differences between
    # runs have been observed.
    abs_tol = 1e-4 if sys.platform == "darwin" else 0.0

    for d_line, c_line in zip(direct_lines, cli_lines):
        helpers.assert_embedded_isclose(d_line, c_line, abs_tol=abs_tol)


def test_exec_eof(sixs_version) -> None:
    """Check error message on empty input file."""
    with pytest.raises(subprocess.CalledProcessError) as exec_info:
        # Run in subprocess to reliably control stdin.
        _run_self_subprocess(
            ["--exec", sixs_version],
            check=True,
            capture_output=True,
            text=True,
            input="",  # Empty stdin
        )

    assert exec_info.value.stdout == ""
    assert (
        exec_info.value.stderr.splitlines()[1] == "Fortran runtime error: End of file"
    )


def test_exec_bad() -> None:
    """Verify that the CLI exits with error on bad ``--exec`` arguments."""
    with pytest.raises(SystemExit):
        sixs_cli.main(["--exec", "does-not-exist"])

    with pytest.raises(SystemExit):
        sixs_cli.main(["--exec"])


def test_test_wrapper() -> None:
    """Verify that ``--test-wrapper`` runs without error when Py6S is installed."""
    # TODO: expand tests for when wrapper dependency is and is not available.
    pytest.importorskip("Py6S")
    sixs_cli.main(["--test-wrapper"])
