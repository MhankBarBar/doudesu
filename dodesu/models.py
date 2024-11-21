"""
Data models for the Doujindesu library.

This module contains all the Pydantic models used to represent
manga data throughout the application.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class Result(BaseModel):
    """
    Model representing a single manga search result.

    Attributes:
        name (str): The title of the manga
        url (str): The URL to the manga's page
        thumbnail (str): URL to the manga's cover image
        genre (list[str]): List of genres associated with the manga
        type (str): Type of manga (defaults to "Doujinshi")
        score (float): Rating score of the manga
        status (str): Publication status (defaults to "Finished")
    """

    name: str
    url: str
    thumbnail: str
    genre: List[str]
    type: str = Field(default="Doujinshi")
    score: float = Field(default=0)
    status: str = Field(default="Finished")

    class Config:
        """Pydantic model configuration"""

        frozen = True  # Makes the model immutable like a dataclass


class SearchResult(BaseModel):
    """
    Model representing search results with pagination information.

    Attributes:
        results (list[Result]): List of manga search results
        next_page_url (str | None): URL to the next page of results, if available
        previous_page_url (str | None): URL to the previous page of results, if available
    """

    results: List[Result]
    next_page_url: Optional[str] = None
    previous_page_url: Optional[str] = None

    class Config:
        """Pydantic model configuration"""

        frozen = True


class DetailsResult(BaseModel):
    """
    Model representing detailed manga information.

    Attributes:
        name (str): The title of the manga
        url (str): The URL to the manga's page
        thumbnail (str): URL to the manga's cover image
        genre (list[str]): List of genres associated with the manga
        series (str): The series name
        author (str): The author's name
        type (str): Type of manga (defaults to "Doujinshi")
        score (float): Rating score of the manga
        status (str): Publication status (defaults to "Finished")
        chapter_urls (list[str]): List of URLs to individual chapters
    """

    name: str
    url: str
    thumbnail: str
    genre: List[str]
    series: str
    author: str
    type: str = Field(default="Doujinshi")
    score: float = Field(default=0)
    status: str = Field(default="Finished")
    chapter_urls: List[str] = Field(default_factory=list)

    class Config:
        """Pydantic model configuration"""

        frozen = True
