"""Parse directory to analyze media files
"""
import os
import logging
from parse import parse
from pprint import pformat

from subrename.utils import load_config

log = logging.getLogger('subrename.parse_media')


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


def parse_file_name(file_name, fformat='{series} - S{season}E{episode} - {quality}'):
    """ Parse file name to get series/season/episode info

    Arguments:
        file_name {str} -- file name

    Keyword Arguments:
        fformat {str} -- file name format (default: {'{series} - S{season}E{episode} - {quality}'})

    Returns:
        [dict] -- a dict including series/season/episode info
    """
    p = parse(fformat, file_name)
    if p:
        return {'series': p['series'],
                'season': int(p['season']),
                'episode': int(p['episode'])}


def scan_media(path=None):
    """
    Scan given path to get a filenames <--> series/season/episode mapping

    Returns:
        [dict] -- filenames <--> series/season/episode mapping
    """
    config = load_config()
    media_file_name_format = config.get('MEDIA_FILE_NAME_FORMAT')
    media_file_exts = config.get('MEDIA_EXTS')

    if path is None:
        path = os.getcwd()
    if not media_file_name_format:
        raise ValueError("Missing media file format, define it in config.json FILE_NAME_FORMAT")
    log.info("Scanning '{0}' with format {1}".format(path, media_file_name_format))
    medias = {}

    file_names = get_file_names(path, exts=media_file_exts)
    for file_name in file_names:
        info = parse_file_name(file_name, fformat=media_file_name_format)
        if info:
            medias[file_name] = info

    return medias
