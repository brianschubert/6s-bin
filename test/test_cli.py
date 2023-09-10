import pytest

import sixs_bin
import sixs_bin._cli as sixs_cli


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


def test_test_wrapper() -> None:
    sixs_cli.main(["--test-wrapper"])
