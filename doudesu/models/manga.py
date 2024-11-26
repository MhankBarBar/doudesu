"""
Data models for the Doudesu library.
"""

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
    genre: list[str]
    type: str = Field(default="Doujinshi")
    score: float = Field(default=0)
    status: str = Field(default="Finished")

    class Config:
        frozen = True


class SearchResult(BaseModel):
    """
    Model representing search results with pagination information.

    Attributes:
        results (list[Result]): List of manga search results
        next_page_url (str | None): URL to the next page of results, if available
        previous_page_url (str | None): URL to the previous page of results, if available
    """

    results: list[Result]
    next_page_url: str | None = None
    previous_page_url: str | None = None

    class Config:
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
    genre: list[str]
    series: str
    author: str
    type: str = Field(default="Doujinshi")
    score: float = Field(default=0)
    status: str = Field(default="Finished")
    chapter_urls: list[str] = Field(default_factory=list)

    class Config:
        frozen = True
