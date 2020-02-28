"""Parse directory to analyze media files
"""
import os


MEDIA_EXTS = ['.mkv', '.avi', '.mp4']


def get_series_name(path=None):
    """ Scan existing media file names to get series name

    Keyword Arguments:
        path {str} -- directory, default to CWD
    """
    if path is None:
        path = os.getcwd()

    file_names = os.listdir(path)
    file_names = [file_name.lower() for file_name in file_names]
    file_names = [file_name for file_name in file_names if any(file_name.endswith(ext) for ext in MEDIA_EXTS)]
