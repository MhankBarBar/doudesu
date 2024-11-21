"""Dodesu - A Python wrapper for doujindesu.tv manga downloader"""

from .doudesu import Doujindesu
from .models import Result, SearchResult, DetailsResult

__version__ = "0.1.0"

__all__ = ["Doujindesu", "Result", "SearchResult", "DetailsResult"]
