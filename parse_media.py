"""Parse directory to analyze media files
"""
import os
from parse import parse


MEDIA_EXTS = ['.mkv', '.avi', '.mp4']


def get_media_file_names(path=None):
    """Scan existing media file names

    Keyword Arguments:
        path {str} -- directory, default to CWD

    Returns:
        [list] -- a list of media file names found
    """
    if path is None:
        path = os.getcwd()

    file_names = os.listdir(path)
    file_names = [file_name.lower() for file_name in file_names]
    file_names = [file_name for file_name in file_names if any(file_name.endswith(ext) for ext in MEDIA_EXTS)]

    return file_names


def parse_file_name(file_name, format='{series} - S{season}E{episode} - {quality}'):
    """ Parse file name to get series/season/episode info

    Arguments:
        file_name {str} -- file name

    Keyword Arguments:
        format {str} -- file name format (default: {'{series} - S{season}E{episode} - {quality}'})

    Returns:
        [dict] -- a dict including series/season/episode info
    """
    p = parse(format, file_name)
    return {'series': p['series'],
            'season': int(p['season']),
            'episode': int(p['episode'])}


def scan_media(path):
    if path is None:
        path = os.getcwd()

    medias = {}

    file_names = get_media_file_names(path)
    for file_name in file_names:
        info = parse_file_name(file_name)