# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_utils.ipynb.

# %% auto 0
__all__ = ['timestamp', 'copytree_agnostic', 'clean_filename']

# %% ../nbs/01_utils.ipynb 2
import sys
import os
from shutil import copytree
from pathlib import Path
import datetime

from urllib.parse import unquote


# %% ../nbs/01_utils.ipynb 4
def timestamp():
    """Return a string for printing the current time"""
    return str(datetime.datetime.now()) + ":"

# %% ../nbs/01_utils.ipynb 6
def copytree_agnostic(a,b):
    if sys.version_info.major >=3 and sys.version_info.minor >=8: copytree(a, b, dirs_exist_ok=True)
    else:
        from distutils.dir_util import copy_tree
        copy_tree(a, b)

# %% ../nbs/01_utils.ipynb 9
def clean_filename(s, **kwargs):
    """Given a string that points to a filename, return a clean filename
    
    Args:
        s (str): filename path

    Returns:
        s (str): clean file name

    Notes:
        kwargs is not used at all
    
    """
    s = unquote(os.path.basename(s))
    invalid_chars = '<>:;,"/\\|?*[]'
    for i in invalid_chars:
        s = s.replace(i, "")
    return s
