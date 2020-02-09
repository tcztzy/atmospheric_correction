import os
import logging
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version(__package__)
except PackageNotFoundError:
    # package is not installed
    __version__ = 'unknown'



def create_logger(fname = None):
    logger = logging.getLogger('zac-%s' % __version__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    if fname is not None:
        fh = logging.FileHandler(fname)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)    
        logger.addHandler(fh)
    return logger
