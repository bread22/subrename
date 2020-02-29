import parse_media
import tvdb_api


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


def main():
    languages = ['en', 'ja', 'zh']

    db_client = tvdb_api.TVDBClient()
    media_files = parse_media.scan_media()
    series_table = get_series_ids(media_files, db_client)

    # Query all series espisode data
    data_cache = {}
    for language in languages:
        for series, tvdb_id in series_table.items():
            data = data_cache.setdefault(series, [])
            data += db_client.get_episodes_by_series_id(tvdb_id, language=language)



    print(series_table)
    print(data_cache)


if __name__ == '__main__':
    main()
