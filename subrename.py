import parse_media
import tvdb_api


def main():
    media_files = parse_media.scan_media()
    series_names = set([i['series'] for i in media_files.values()])

    db_client = tvdb_api.TVDBClient()
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

    # Query all series espisode data
    data_cache = []
    for tvdb_id in series_table.values():
        data_cache += db_client.get_episodes_by_series_id(tvdb_id)

    print(series_names)


if __name__ == '__main__':
    main()
