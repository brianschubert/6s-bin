"""
Command line interface.
"""
# Copyright (C) 2023 Brian Schubert.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import pathlib
import subprocess
import sys

import sixs_bin


def _make_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        # Override program name to something more meaningful than '__main__.py'.
        prog=f"{pathlib.PurePath(sys.executable).name} -m {sixs_bin.__name__}",
        description="6S v1.1 and 6S v2.1 binaries provided as package resources.",
    )

    parser.add_argument("--version", action="version", version=_make_version())

    command_group = parser.add_argument_group(
        title="command"
    ).add_mutually_exclusive_group()

    command_group.add_argument(
        "--path",
        choices=sixs_bin._SIXS_BINARIES.keys(),
        help="Print the path to the specified 6S executable from this package's resources.",
    )
    command_group.add_argument(
        "--exec",
        choices=sixs_bin._SIXS_BINARIES.keys(),
        help="Execute specified 6S executable in a subprocess, inheriting stdin and stdout. This option is provided"
        " as a convenience, but its not generally recommended. Running 6S using this option is around 5%% slower than"
        " executing the binary directly, due the overhead of starting the Python interpreter and subprocess.",
    )
    command_group.add_argument(
        "--test-wrapper",
        action="store_true",
        help="Run Py6S.SixS.test on this package's 6SV1.1 executable.",
    )

    return parser


def _make_version() -> str:
    """Create version summary."""
    return f"{sixs_bin.DISTRIBUTION_NAME} {sixs_bin.__version__} (6S {', '.join(sixs_bin._SIXS_BINARIES.keys())})"


def main(cli_args: list[str]) -> None:
    """CLI entrypoint."""
    parser = _make_parser()
    args = parser.parse_args(cli_args)

    if args.exec is not None:
        proc_args = (sixs_bin.get_path(args.exec),)
        ret_code = subprocess.Popen(proc_args).wait()
        if ret_code:
            raise subprocess.CalledProcessError(ret_code, proc_args)
        return

    if args.path is not None:
        print(sixs_bin.get_path(args.path))
        return

    if args.test_wrapper:
        wrapper = sixs_bin.make_wrapper("1.1")
        sys.exit(wrapper.test(wrapper.sixs_path))

    parser.print_help()


def cli() -> None:
    """Launch this package's CLI."""
    main(sys.argv[1:])
