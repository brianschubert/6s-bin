# 6S Binaries

[![release workflow](https://github.com/brianschubert/6s-bin/actions/workflows/release.yaml/badge.svg?event=push)](https://github.com/brianschubert/6s-bin/actions/workflows/release.yaml)
[![tests workflow](https://github.com/brianschubert/6s-bin/actions/workflows/test.yaml/badge.svg)](https://github.com/brianschubert/6s-bin/actions/workflows/test.yaml)
[![PyPI - Version](https://img.shields.io/pypi/v/6s-bin)](https://pypi.org/project/6s-bin)
[![GitHub last commit (branch)](https://img.shields.io/github/last-commit/brianschubert/6s-bin/develop)](https://github.com/brianschubert/6s-bin/commits/develop)
[![License](https://img.shields.io/github/license/brianschubert/6s-bin)](./LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/psf/black)

This distribution provides access to compiled binaries of the [6S Radiative Transfer Model](https://salsa.umd.edu/6spage.html) as [package resources](https://docs.python.org/3/library/importlib.resources.html#module-importlib.resources).

It *does not* provide a Python interface to 6S. For a Python interface, see  Robin Wilson's [Py6S].

Currently, this project includes binaries for 6SV1.1 and 6SV2.1. It requires Python 3.9+ and supports Linux, macOS, and Windows.

## Install

Pre-compiled wheels can be installed from [PyPI](https://pypi.org/project/6s-bin/):
```shell
$ pip install 6s-bin
```
If you are using [poetry](https://python-poetry.org/), you can add this distribution as a dependency using 
`poetry add`:
```shell
$ poetry add 6s-bin
```

### Installing from source

Building this distribution involves downloading, validating, and compiling the 6S source code. See [`build.py`](./build.py) for details about the build process. A Fortran 77 compiler is required to compile 6S.

Build and install from source distribution:
```shell
$ pip install --no-binary=6s-bin 6s-bin
```

Build and install from git:
```shell
$ pip install '6s-bin @ git+https://github.com/brianschubert/6s-bin'
```

Build and install from local source tree:
```shell
$ pip install .
```

## Python Usage

Call `sixs_bin.get_path(version)` to get the path to an installed 6S binary. The parameter `version` is required, and must be either the string `"1.1"` or `"2.1"`.
```pycon
>>> import sixs_bin

>>> sixs_bin.get_path("1.1")
PosixPath('<path to virtual environment>/lib/python3.X/site-packages/sixs_bin/sixsV1.1')

>>> sixs_bin.get_path("2.1")
PosixPath('<path to virtual environment>/lib/python3.X/site-packages/sixs_bin/sixsV2.1')
```

If you also have [Py6S][Py6S] installed, you can call `sixs_bin.make_wrapper()` to get a `Py6S.SixS` instance that's configured to use the installed 6SV1.1 binary.

```pycon
>>> wrapper = sixs_bin.make_wrapper()

>>> wrapper
<Py6S.sixs.SixS object at 0x...>

>>> wrapper.sixs_path
PosixPath('<path to virtual environment>/lib/python3.X/site-packages/sixs_bin/sixsV1.1')

>>> wrapper.run()
>>> wrapper.outputs.apparent_radiance
134.632
```

## Command Line Usage

Run `python3 -m sixs_bin --help` to see all available command line options.
```none
$ python3 -m sixs_bin --help
usage: python3 -m sixs_bin [-h] [--version]
                           [--path {1.1,2.1} | --exec {1.1,2.1} | --test-wrapper]

6S v1.1 and 6S v2.1 binaries provided as package resources.

optional arguments:
  -h, --help        show this help message and exit
  --version         show program's version number and exit

command:
  --path {1.1,2.1}  Print the path to the specified 6S executable from this package's
                    resources.
  --exec {1.1,2.1}  Execute specified 6S executable in a subprocess, inheriting stdin and
                    stdout. This option is provided as a convenience, but its not
                    generally recommended. Running 6S using this option is around 5%
                    slower than executing the binary directly, due the overhead of
                    starting the Python interpreter and subprocess.
  --test-wrapper    Run Py6S.SixS.test on this package's 6SV1.1 executable.
```

To get the path to an installed 6S binary, run `sixs_bin` as an executable module with the `--path` flag specified. The `--path` flag takes one required argument, which must be either the string `1.1` or `2.1`:
```shell
$ python3 -m sixs_bin --path 2.1
<path to virtual environment>/lib/python3.X/site-packages/sixs_bin/sixsV2.1
```

If you need the path to the containing directory, use `dirname`. For example:
```shell
$ SIXS_DIR=$(dirname $(python3 -m sixs_bin --path 2.1))
$ echo $SIXS_DIR
<path to virtual environment>/lib/python3.X/site-packages/sixs_bin
```

## Test

Tests can be run using pytest:
```shell
$ pytest
```

Some tests are included to check compatibility with Robin Wilson's [Py6S][Py6S] wrapper. These tests will be ignored if `Py6S` is not available.

[Py6S]: https://www.py6s.rtwilson.com/
