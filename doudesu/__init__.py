"""Dodesu - A Python wrapper for doujindesu.tv manga downloader"""

from importlib.metadata import version

from .core.doudesu import Doujindesu
from .models.manga import DetailsResult, Result, SearchResult

__version__ = version("doudesu")
__all__ = ["Doujindesu", "Result", "DetailsResult", "SearchResult"]
