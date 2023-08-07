# 6S Binary Wrapper

[![Code style: black](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/psf/black)


Convenience distribution for building and installing local [6S](https://salsa.umd.edu/6spage.html) executables.

Provides binaries for 6S v1.1 and 6S v2.1 as package resources.

## Install

From git:
```
$ pip install '6s-bin @ git+https://github.com/brianschubert/6s-bin'
```

From local source tree:
```shell
$ pip install .
```

## Usage

Call `sixs_bin.get_path(version)` to get the path to an installed 6S binary. The parameter `version` is required, and must be either the string `"1.1"` or `"2.1"`.

If you also have [Py6S][Py6S] installed, you can call `sixs_bin.make_wrapper()` to get a `Py6S.SixS` instance that's configured to use the installed 6S v1.1 binary.


## Test

Tests can be run using pytest:
```shell
$ pytest
```

Some tests require Robin Wilson's [Py6S][Py6S] wrapper to be installed. These tests will be ignored if `Py6S` is not available. Enable the `wrapper` extra to install `Py6S` automatically.

[Py6S]: https://www.py6s.rtwilson.com/
