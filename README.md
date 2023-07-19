# 6S Binary Wrapper

Convenience distribution for building and installing a local [6S](https://salsa.umd.edu/6spage.html) v1.1 executable.

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

Call `sixs_bin.sixs_bin` to get the path to the installed 6S binary.

If you also have `Py6S` installed, you can call `sixs_bin.make_wrapper` to get a `Py6S.SixS` instance that's configured to use the installed 6S binary.


## Test

The installed 6S binary can be tested using Robin Wilson's [Py6S](https://www.py6s.rtwilson.com/) wrapper. Enable the `wrapper` extra to automatically install it.

From the command line:
```shell
$ pytest
```

From Python:
```pycon
>>> import sixs_bin
>>> sixs_bin.test_wrapper()
```
