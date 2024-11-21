"""Dodesu - A Python wrapper for doujindesu.tv manga downloader"""

from .doudesu import Doujindesu
from .models import Result, SearchResult, DetailsResult

from importlib.metadata import version

__version__ = version("doudesu")

__all__ = ["Doujindesu", "Result", "SearchResult", "DetailsResult"]

print(__version__)
