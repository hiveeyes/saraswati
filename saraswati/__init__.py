# -*- coding: utf-8 -*-
__appname__ = __name__

# Single-sourcing the package version
# https://cjolowicz.github.io/posts/hypermodern-python-06-ci-cd/
try:
    from importlib.metadata import PackageNotFoundError, version  # noqa
except ImportError:  # pragma: no cover
    from importlib_metadata import PackageNotFoundError, version  # noqa

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
