"""
This file provides utilities manipulating files in various ways.
"""


import os
import os.path
import shutil
import tempfile
import zipfile


def zip_folder(path: str, dirname: str='', prefix: str='', delete_dir: bool=False) -> str:
    """
    Zips all files in a given folder and returns a path to the archive.

    :param path: The path to the directory to compress.
    :param dirname: Optionally, the name of a directory to place all files in the zip file. When
    the archive is extracted, all files will be in this directory.
    :param prefix: Optionally, a prefix to prepend to the archive.
    :param delete_dir: Determines if the directory is deleted after the archive is created. Defaults
    to False.
    :return str: The path to the zip file.
    :raises FileNotFoundError: If the given path doesn't exist.
    :raises NotADirectoryError: If the given path isn't a directory.
    """
    # Handle cases where the directory doesn't exist or isn't actually directory
    if not os.path.exists(path):
        raise FileNotFoundError
    if not os.path.isdir(path):
        raise NotADirectoryError

    # Get the files in the directory
    files = walk_dir(path, dirname)

    # Write the files as a zip archive
    fd, zip_loc = tempfile.mkstemp(prefix=prefix, suffix='.zip')
    with os.fdopen(fd, 'wb') as zipfd:
        with zipfile.ZipFile(zipfd, 'w', zipfile.ZIP_DEFLATED) as zip:
            for abs_path, rel_path in files:
                zip.write(abs_path, rel_path)

    # If delete_dir is True, delete the directory
    if delete_dir:
        shutil.rmtree(path)

    # Return a path to the archive
    return zip_loc


def walk_dir(path: str, dirname: str='') -> list[tuple[str, str]]:
    """
    Walks the directory structure starting at path. Returns a list of files as absolute and relative
    paths.

    :param path: The directory to start at.
    :param dirname: Optionally, a directory to place all files inside.
    :return list[str, str]: A list of tuples representing absolute and relative paths for each file.
    :raises FileNotFoundError: If the given path doesn't exist.
    :raises NotADirectoryError: If the given path isn't a directory.
    """
    # Handle cases where the directory doesn't exist or isn't actually directory
    if not os.path.exists(path):
        raise FileNotFoundError
    if not os.path.isdir(path):
        raise NotADirectoryError

    rel_files = []

    # Based on https://stackoverflow.com/a/1855118
    for root, _, files in os.walk(path):
        for file in files:
            abs_path = os.path.join(root, file)
            rel_path = os.path.join(dirname, os.path.relpath(abs_path, path))
            rel_files.append((abs_path, rel_path))

    return rel_files
