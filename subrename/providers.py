"""ABC class for providers"""
from abc import ABC, abstractmethod


class TVShowProvider(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_series_by_id(self):
        pass

    @abstractmethod
    def get_series_by_imdb_id(self):
        pass

    @abstractmethod
    def find_series_by_name(self):
        pass

    @abstractmethod
    def get_episodes_by_series_id(self):
        pass
