import os.path
from importlib.metadata import PackageNotFoundError, version
from os.path import expanduser

try:
    __version__ = version(__package__)
except PackageNotFoundError:
    # package is not installed
    pass

HOME = expanduser("~")
DEFAULT_MCD43_DIR = os.path.join(HOME, "MCD43", "")
DEFAULT_MCD43_VRT_DIR = os.path.join(HOME, "MCD43_VRT", "")
