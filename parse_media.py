"""Parse directory to analyze media files
"""
import os
import logging
from parse import parse
from pprint import pformat

log = logging.getLogger('subrename.parse_media')
MEDIA_EXTS = ['.mkv', '.avi', '.mp4']


def get_file_names(path, exts):
    """Scan existing media file names

    Keyword Arguments:
        path {str} -- directory, default to CWD

    Returns:
        [list] -- a list of media file names found
    """
    if path is None:
        path = os.getcwd()

    file_names = os.listdir(path)
    file_names = [file_name for file_name in file_names if any(file_name.lower().endswith(ext) for ext in exts)]
    log.debug("Found files:")
    log.debug(pformat(file_names))
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


def scan_media(path=None):
    """
    Scan given path to get a filenames <--> series/season/episode mapping

    Returns:
        [dict] -- filenames <--> series/season/episode mapping
    """
    if path is None:
        path = os.getcwd()
    format = os.environ.get('FILE_NAME_FORMAT', '{series} - S{season}E{episode} - {quality}')
    log.info("Scanning '{0}' with format {1}".format(path, format))
    medias = {}

    file_names = get_file_names(path, exts=MEDIA_EXTS)
    for file_name in file_names:
        info = parse_file_name(file_name, format=format)
        medias[file_name] = info

    return medias
