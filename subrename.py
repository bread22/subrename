from copy import deepcopy
from os import rename
import logging
import re

import parse_media
import tvdb_api
from utils import load_config

log = logging.getLogger('subrename')
log.setLevel(logging.DEBUG)
fh = logging.FileHandler('subrename.log', mode='w')
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)


def get_series_ids(media_files, db_client):
    """ Get series db id for existing media files

    Arguments:
        media_files {list} -- list of dicts

    Raises:
        ValueError: if not exact name is found
        ValueError: if more than one exact name is found

    Returns:
        [dict] -- {'series_name': tvbd_id}
    """
    series_names = set([i['series'] for i in media_files.values()])

    series_table = {}
    for series in series_names:
        possible_series = db_client.find_series_by_name(series)
        matching_series = [i for i in possible_series if i['name'] == series]
        if not matching_series:
            raise ValueError("Cannot find exact series name '{0}'".format(series))
        elif len(matching_series) > 1:
            raise ValueError("More than one match are found with name '{0}', \
                need more information (maybe year)".format(series))
        series_table[series] = {'id': matching_series[0]['tvdb_id'],
                                'names': [series]}

    return series_table


def update_series_alt_names(series_table, db_client):
    """ Update names in other languages for series

    Arguments:
        series_table {dict} -- series table with name(en) to id mapping
                                ex: {'Planetes': {'id':75796, 'names': ['Planetes']}}

    Returns:
        series_table -- updated series_table with other names
                                ex: {'Planetes': {'id':75796, 'names': ['Planetes', 'プラネテス', '星空之旅']}}
    """
    config = load_config()
    search_languages = set(config.get('SEARCH_LANGS', ['en']))
    search_languages.remove('en')

    for series in series_table:
        for language in search_languages:
            metadata = db_client.get_series_by_id(series_table[series]['id'], language=language)
            series_name = metadata.get('seriesName')
            if series_name:
                series_table[series]['names'].append(series_name)
        series_table[series]['names'] = set(series_table[series]['names'])

    return series_table


def find_episode_metadata_for_media(media_info, data_cache):
    """ For given episode season/number, find all names in all languages

    Arguments:
        media_info {dict} -- return of parse_media.parse_file_name()
        data_cache {dict} -- cached data fetched from online database (TheTVDB, etc)

    Returns:
        [dict] -- media_info plus names
    """
    episode = deepcopy(media_info)
    episode['names'] = set(i.get('episodeName') for i in data_cache[episode['series']]
                           if i['airedSeason'] == episode['season'] and i['airedEpisodeNumber'] == episode['episode']
                           and i.get('episodeName'))
    return episode


def find_matching_subs(media_info, sub_files):

    config = load_config()
    season_episode_fmts = config['SEASON_EPISODE_FORMATS']

    series = media_info['series']
    season = media_info['season']
    episode = media_info['episode']
    names = media_info['names']
    log.info('Searching for series {0}, season {1}, episode {2}'.format(series, season, episode))

    # 1, episode name matching
    match = _match_sub_by_name(names, sub_files=sub_files)
    if match:
        return match

    # 2, season/episode number matching
    match = _match_sub_by_season_episode(season, episode, names, sub_files=sub_files, formats=season_episode_fmts)
    if match:
        return match

    # 3, episode only matching


def _match_sub_by_name(names, sub_files):
    """Match by exact name

    Use possible episode names to match subtitle files

    Arguments:
        names {list} -- possible episode names in different languages
        sub_files {list} -- existing subtitle files

    Returns:
        [str] -- if match is found, return matching file name, otherwise None
    """
    for name in names:
        for sub_file in sub_files:
            if name.lower() in sub_file.lower():
                log.info('Name match FOUND: {0} in {1}'.format(name, sub_file))
                return sub_file


def _match_sub_by_season_episode(season, episode, names, sub_files, formats):
    """ Match by season/episode number

    Requires series name in subtitle file name

    Arguments:
        season {[type]} -- [description]
        episode {[type]} -- [description]
        names {[type]} -- [description]
        sub_files {[type]} -- [description]
        formats {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    for sub_file in sub_files:
        sub_file_tmp = sub_file.lower().replace('.', ' ').replace('_', ' ')
        for fmt in formats:
            pattern = fmt.replace('{season}', '([0-9]{1,3})').replace('{episode}', '([0-9]{1,3})')
            match = re.findall(pattern.lower(), sub_file_tmp)
            if match:
                sub_season, sub_episode = match[0]
                if int(sub_season) == season and int(sub_episode) == episode:
                    log.info("S/E match is found '{0}'".format(sub_file))
                    return sub_file


def _match_sub_by_episode():
    pass


def main():
    config = load_config()
    subtitles_exts = config.get('SUBTITLES_EXTS', ['.srt', '.ssa', '.ass'])
    search_languages = config.get('SEARCH_LANGS', ['en'])

    db_client = tvdb_api.TVDBClient()
    media_files = parse_media.scan_media()
    series_table = get_series_ids(media_files, db_client)

    # Query all series espisode data
    data_cache = {}
    for series, tvdb_id in series_table.items():
        for language in search_languages:
            data = data_cache.setdefault(series, [])
            data += db_client.get_episodes_by_series_id(tvdb_id, language=language)
        data_cache[series] = data

    sub_files = parse_media.get_file_names(path='.', exts=subtitles_exts)

    matching_subs = []
    for media_file, metadata in media_files.items():
        episode_meta = find_episode_metadata_for_media(metadata, data_cache)
        sub_file = find_matching_subs(episode_meta, sub_files)
        if sub_file:
            matching_subs.append((media_file, sub_file))

    # Rename matching subtitles
    # for media_file, sub_file in matching_subs:
    #     file_name = media_file[:-(len(media_file.split('.')[-1] + 1))]
    #     rename(sub_file, '{0}.{1}.{2}'.format(file_name, config['SUBTITLE_LANG'], sub_file.split('.')[-1]))

    print(series_table)
    # print(data_cache)
    print(matching_subs)


if __name__ == '__main__':
    main()
