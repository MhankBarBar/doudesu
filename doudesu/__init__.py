"""Dodesu - A Python wrapper for doujindesu.tv manga downloader"""

from .core.doudesu import Doujindesu
from .models.manga import Result, DetailsResult

from importlib.metadata import version

__version__ = version("doudesu")
__all__ = ["Doujindesu", "Result", "DetailsResult"]
