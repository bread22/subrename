from unittest import TestCase
from subrename import main


class TestMain(TestCase):
    @staticmethod
    def test_find_episode_metadata_for_media():
        data_cache = {
            'show_A': [
                {'airedSeason': 1, 'airedEpisodeNumber': 1, 'episodeName': 'EP1'},
                {'airedSeason': 1, 'airedEpisodeNumber': 2, 'episodeName': 'EP2'},
                {'airedSeason': 1, 'airedEpisodeNumber': 3, 'episodeName': 'EP3'},
                {'airedSeason': 1, 'airedEpisodeNumber': 4, 'episodeName': 'EP4'},
                {'airedSeason': 1, 'airedEpisodeNumber': 1, 'episodeName': 'ABC'},
            ]
        }
        metadata = {'series': 'show_A', 'season': 1, 'episode': 1}
        main.find_episode_metadata_for_media(metadata, data_cache) == {'series': 'show_A',
                                                                            'season': 1,
                                                                            'episode': 1,
                                                                            'names': {'EP1', 'ABC'}}
        metadata = {'series': 'show_A', 'season': 1, 'episode': 2}
        main.find_episode_metadata_for_media(metadata, data_cache) == {'series': 'show_A',
                                                                            'season': 1,
                                                                            'episode': 1,
                                                                            'names': {'EP2'}}

        metadata = {'series': 'show_A', 'season': 2, 'episode': 1}
        main.find_episode_metadata_for_media(metadata, data_cache) == {'series': 'show_A',
                                                                            'season': 1,
                                                                            'episode': 1,
                                                                            'names': set()}

