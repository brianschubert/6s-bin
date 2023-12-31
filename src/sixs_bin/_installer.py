"""
Entrypoints for console scripts that replace themselves with 6S binaries when first run.
"""

import os
import pathlib
import subprocess
import sys

import sixs_bin


def _main_path() -> pathlib.Path:
    """Retrieve the absolute path to the current ``__main__`` module."""
    main = sys.modules["__main__"]
    if not hasattr(main, "__file__") or main.__file__ is None:
        raise RuntimeError(
            f"__main__ module {main} is missing __file__ - cannot retrieve path to __main__"
        )

    path = pathlib.Path(main.__file__).resolve()

    # Handle .exe console scripts on Windows, where __file__ will be 'some\path\file.exe\__main__.py'.
    if path.parent.name.endswith(".exe"):
        path = path.parent

    return path


def _install(src: pathlib.Path, target: pathlib.Path) -> None:
    """
    Install ``src`` to ``target``.

    Attempts to hardlink ``target`` to ``src`` if possible. Otherwise, falls
    back to writing the contents of ``src`` to ``target`` inplace.
    """
    temp_target = target.with_name(f"~{target.name}")

    try:
        os.link(src, temp_target)
    except OSError:
        # Failed to create new hardlink in bin directory.
        # Fall back to simply writing the contents of the source file inplace.
        target.write_bytes(src.read_bytes())
        return

    # Successfully created new hardlink in the bin directory.
    # Remove the old script, then move the hardlink to the old script's location.
    target.unlink()
    temp_target.rename(target)


def _inplace_install_11() -> None:
    """Replace the current ``__main__`` module with a 6S V1.1 binary."""
    _run_inplace_install(sixs_bin.get_path("1.1"), _main_path())


def _inplace_install_21() -> None:
    """Replace the current ``__main__`` module with a 6S V2.1 binary."""
    _run_inplace_install(sixs_bin.get_path("2.1"), _main_path())


def _run_inplace_install(src: pathlib.Path, target: pathlib.Path) -> None:
    print(
        f"Starting first-run installation for {target.name}.\n"
        f"This will install the 6S binary '{src}' to '{target}'.\n...",
        file=sys.stderr,
        flush=True,
    )
    try:
        _install(src, target)
    except OSError:
        print(
            "error: first-run installation failed! See accompanying exception traceback.",
            file=sys.stderr,
            flush=True,
        )
        raise

    print(
        "First-run installation succeeded! Launching 6S in a subprocess. All future runs will execute 6S directly.",
        file=sys.stderr,
        flush=True,
    )

    sys.exit(subprocess.run([target, *sys.argv[1:]]).returncode)
