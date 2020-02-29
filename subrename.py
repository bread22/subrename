import parse_media
import tvdb_api
from copy import deepcopy
from os import environ, rename
import logging
import json
import re


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
        series_table[series] = matching_series[0]['tvdb_id']

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


def find_matching_subs(media_info, files):

    config = load_config()
    season_episode_fmts = config['SEASON_EPISODE_FORMATS']

    series = media_info['series']
    season = media_info['season']
    episode = media_info['episode']
    log.info('Searching for series {0}, season {1}, episode {2}'.format(series, season, episode))

    # 1, episode name matching
    for name in media_info['names']:
        for sub_file in files:
            if name.lower() in sub_file.lower():
                log.info('Name match FOUND: {0} in {1}'.format(name, sub_file))
                return sub_file

    # 2, season/episode number matching
    for sub_file in files:
        sub_file_tmp = sub_file.lower().replace('.', ' ').replace('_', ' ')
        for fmt in season_episode_fmts:
            pattern = fmt.replace('{season}', '([0-9]{1,3})').replace('{episode}', '([0-9]{1,3})')
            match = re.findall(pattern.lower(), sub_file_tmp)
            if match:
                sub_season, sub_episode = match[0]
                if int(sub_season) == season and int(sub_episode) == episode:
                    log.info("S/E match is found '{0}'".format(sub_file))
                    return sub_file

    # 3, episode only matching
    


def load_config():
    with open('config.json') as fn:
        config = fn.read()
    return json.loads(config)


def main():
    config = load_config()
    subtitles_exts = environ.get('SUBTITLES_EXTS', ['.srt', '.ssa', '.ass'])

    db_client = tvdb_api.TVDBClient()
    media_files = parse_media.scan_media()
    series_table = get_series_ids(media_files, db_client)

    # Query all series espisode data
    data_cache = {}
    for series, tvdb_id in series_table.items():
        for language in config['SEARCH_LANGS']:
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
