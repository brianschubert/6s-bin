import subprocess
import sys
from typing import Any

import pytest

import sixs_bin
import sixs_bin._cli as sixs_cli


def _run_self_subprocess(
    cli_args: list[str], **kwargs: Any
) -> subprocess.CompletedProcess:
    """
    Run the command line interface in a subprocess.

    Needed instead of calling the CLI entrypoint directly when more advanced control
    over the process running the command line interface is required.
    """
    return subprocess.run(
        [sys.executable, "-m", sixs_bin.__name__, *cli_args], **kwargs
    )


def test_version(capsys) -> None:
    sixs_cli.main(["--version"])

    captured = capsys.readouterr()
    assert captured.out.strip() == sixs_cli._make_version()
    assert captured.err == ""


@pytest.mark.parametrize("version", sixs_bin._SIXS_BINARIES.keys())
def test_good_path(version, capsys) -> None:
    sixs_cli.main(["--path", version])

    captured = capsys.readouterr()
    assert captured.out.strip() == str(sixs_bin.get_path(version))
    assert captured.err == ""


def test_bad_path() -> None:
    with pytest.raises(SystemExit):
        sixs_cli.main(["--path", "does-not-exist"])

    with pytest.raises(SystemExit):
        sixs_cli.main(["--path"])


@pytest.mark.parametrize("version", sixs_bin._SIXS_BINARIES.keys())
def test_exec_eof(version) -> None:
    with pytest.raises(subprocess.CalledProcessError) as exec_info:
        # Run in subprocess to reliably control stdin.
        _run_self_subprocess(
            ["--exec", version],
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
    with pytest.raises(SystemExit):
        sixs_cli.main(["--exec", "does-not-exist"])

    with pytest.raises(SystemExit):
        sixs_cli.main(["--exec"])


def test_test_wrapper() -> None:
    sixs_cli.main(["--test-wrapper"])
