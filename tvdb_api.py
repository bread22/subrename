"""
TheTVDB API
"""
import requests
import json
from typing import List, Union
from urllib.parse import urljoin
import logging

from providers import TVShowProvider
from utils import load_config


log = logging.getLogger('subrename.tvdb_api')


class TVDBClient(TVShowProvider):
    ID_KEY = 'id'
    SEASON_KEY = 'airedSeason'
    SEASONID_KEY = 'airedSeasonID'
    EPISODE_KEY = 'airedEpisodeNumber'
    EPISODE_NAME_KEY = 'episodeName'
    ABS_EPISODE_KEY = 'absoluteNumber'

    def __init__(self):
        config = load_config()
        self._auth_data = {
            "username": config.get('TVDB_USER'),
            "userkey": config.get('TVDB_USERKEY'),
            "apikey": config.get('TVDB_API'),
        }
        self.base_url = 'https://api.thetvdb.com'
        self._urls = self._generate_urls()
        self.__saved_token = self._generate_token()

    @property
    def _token(self):
        if self.__saved_token is None:
            self.__saved_token = self._generate_token()

        return self.__saved_token

    def _generate_urls(self):
        urls = {
            "login": "/login",
            "refresh_token": "/refresh_token",
            "search_series": "/search/series",
            "series": "/series/{id}",
            "series_episodes": "/series/{id}/episodes",
        }

        return {key: urljoin(self.base_url, url) for key, url in urls.items()}

    def _generate_token(self):
        url = self._urls["login"]
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        log.info("Generate TheTVDB token.")
        response = requests.post(url, headers=headers, data=json.dumps(self._auth_data))
        if response.status_code == 401:
            raise ConnectionRefusedError("Invalid credentials.")

        if response.status_code != 200:
            raise ConnectionError("Unexpected Response.")

        return response.json()["token"]

    def _get_with_token(self, url, query_params=None, language=None):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer {0}".format(self._token),
        }
        if language:
            headers['Accept-Language'] = language
        return requests.get(url, headers=headers, params=query_params)

    def _refresh_token(self):
        response = self._get_with_token(self._urls["refresh_token"])
        if response.status_code == 401:
            raise ConnectionRefusedError("Invalid token")
        if response.status_code != 200:
            raise ConnectionError("Unexpected Response.")

        self.__saved_token = response.json()["token"]

    def _get(self, url, query_params=None, *, allow_401=True, language=None):
        response = self._get_with_token(url, query_params, language=language)
        if response.status_code == 200:
            return response.json()

        elif response.status_code == 404:
            raise LookupError("There are no data for this term.")

        elif response.status_code == 401 and allow_401:
            try:
                self._refresh_token()
            except ConnectionError:
                self.__saved_token = self._generate_token()

            return self._get(url, allow_401=False)

        raise ConnectionError("Unexpected Response.")

    def get_series_by_id(self, tvdb_id: Union[str, int], language=None) -> dict:
        """
        Get the series info by its tvdb ib
        """
        url = self._urls["series"].format(id=tvdb_id)
        return self._get(url, language=language)["data"]

    def get_series_by_imdb_id(self, imdb_id: str) -> dict:
        """
        Get the series info by its imdb ib
        """
        url = self._urls["search_series"]
        query_params = {"imdbId": imdb_id}
        tvdb_id = self._get(url, query_params)["data"][0]["id"]
        return self.get_series_by_id(tvdb_id)

    def find_series_by_name(self, series_name: str) -> List[dict]:
        """
        Find all TV series that match a TV series name
        The info returned for each TV series are its name,
        the original air date (in "%Y-%m-%d" format) and the
        tvdb_id (as an integer).
        This information should be enough to identify the desired
        series and search by id afterwards.
        """
        url = self._urls["search_series"]
        query_params = {"name": series_name}
        info = self._get(url, query_params)["data"]

        return [
            {
                "name": series["seriesName"],
                "air_date": series["firstAired"],
                "tvdb_id": series["id"],
            }
            for series in info
        ]

    def get_episodes_by_series_id(self, tvdb_id: Union[str, int], language=None) -> List[dict]:
        """
        Get all the episodes for a TV series
        """
        log.info("Get episode metadata for '{0}', language '{1}'".format(tvdb_id, language))
        base_url = self._urls["series_episodes"].format(id=tvdb_id)
        full_data = self._get(base_url, language=language)

        return full_data['data']
