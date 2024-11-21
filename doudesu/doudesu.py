"""
Doujindesu API Wrapper

This module provides a Python interface for interacting with doujindesu.tv,
allowing users to search, download, and convert manga chapters to PDF format.
"""

import re
from typing import List, Optional

from bs4 import BeautifulSoup as Bs
from rich import print
from tls_client import Session

from .constants import (
    BASE_URL,
    CHAPTER_API_ENDPOINT,
    CHAPTER_ID_PATTERN,
    HEADERS,
    IMAGE_SRC_PATTERN,
    TLS_CLIENT_CONFIG,
)
from .converter import ImageToPDFConverter
from .models import DetailsResult, Result, SearchResult


class Doujindesu(ImageToPDFConverter):
    """
    Main class for interacting with doujindesu.tv. Provides methods for searching,
    retrieving manga details, and downloading chapters.

    Inherits from ImageToPDFConverter to provide PDF conversion capabilities.

    Args:
        url (str): The URL to the manga page or search results
        proxy (Optional[str]): Proxy server URL if needed

    Attributes:
        url (str): Current URL being processed
        proxy (Optional[str]): Proxy server configuration
        soup (Optional[Bs]): BeautifulSoup object for parsing HTML
    """

    def __init__(self, url: str, proxy: Optional[str] = None):
        super().__init__()
        self.url: str = url
        self.proxy: Optional[str] = proxy
        self.soup: Optional[Bs] = None

    @property
    def create_session(self) -> Session:
        """
        Creates and configures a TLS session for making requests.

        Returns:
            Session: Configured TLS session object
        """
        session = Session(**TLS_CLIENT_CONFIG)
        if self.proxy:
            session.proxies.update({"http": self.proxy})
        session.headers.update(HEADERS)
        return session

    def scrap(self) -> None:
        """
        Scrapes the current URL and updates the soup attribute with parsed HTML.
        """
        ses = self.create_session
        content = ses.get(self.url).text
        self.soup = Bs(content, "html.parser")
        ses.close()

    def get_id(self, text: str) -> Optional[int]:
        """
        Extracts the manga ID from the given text.

        Args:
            text (str): HTML text containing the manga ID

        Returns:
            Optional[int]: Extracted manga ID or None if not found

        Raises:
            ValueError: If ID cannot be extracted from the text
        """
        match = re.search(CHAPTER_ID_PATTERN, text)
        if match:
            return int(match.group(1))
        else:
            raise ValueError("ID could not be extracted from the text.")

    def get_all_chapters(self) -> List[str]:
        """
        Retrieves URLs for all chapters of the manga.

        Returns:
            list[str]: List of chapter URLs in reverse chronological order
        """
        self.scrap()
        urls = list(
            reversed([BASE_URL + x.a.get("href") for x in self.soup.select("span.eps")])
        )
        return urls

    def get_all_images(self) -> List[str]:
        """
        Retrieves all image URLs from the current chapter.

        Returns:
            List[str]: List of image URLs for the chapter
        """
        self.scrap()
        _id = self.get_id(self.soup.prettify())
        ses = self.create_session
        req = ses.post(CHAPTER_API_ENDPOINT, data={"id": _id})
        ses.close()
        return re.findall(IMAGE_SRC_PATTERN, req.text)

    def get_details(self) -> Optional[DetailsResult]:
        """
        Retrieves detailed information about the manga.

        Returns:
            Optional[DetailsResult]: Detailed manga information or None if not found
        """
        self.scrap()
        soup = self.soup.find("main", {"id": "archive"})
        if not soup:
            return None
        return DetailsResult(
            name="-".join(self.soup.title.text.split("-")[:-1]).strip(),
            url=self.url,
            thumbnail=self.soup.find("figure", {"class": "thumbnail"}).img.get("src"),
            genre=[
                x.text.strip()
                for x in soup.find("div", {"class": "tags"}).find_all("a")
            ],
            series=soup.find("tr", {"class": "parodies"}).a.text.strip(),
            author=soup.find("tr", {"class": "pages"}).a.text.strip(),
            type=soup.find("tr", {"class": "magazines"}).a.text.strip(),
            score=float(soup.find("div", {"class": "rating-prc"}).text.strip()),
            status=soup.find("tr", {"class": ""}).a.text.strip(),
            chapter_urls=list(
                reversed([BASE_URL + x.a.get("href") for x in soup.select("span.eps")])
            ),
        )

    def get_search(self) -> Optional[SearchResult]:
        """
        Retrieves search results from the current URL.

        Returns:
            Optional[SearchResult]: Search results with pagination or None if no results found
        """
        self.scrap()
        if "No result found" in self.soup.prettify():
            return None
        next_page = (
            BASE_URL + self.soup.find("a", {"title": "Next page"}).get("href", None)
            if self.soup.find("a", {"title": "Next page"})
            else None
        )
        previous_page = (
            BASE_URL + self.soup.find("a", {"title": "Previous page"}).get("href", None)
            if self.soup.find("a", {"title": "Previous page"})
            else None
        )
        return SearchResult(
            results=[
                Result(
                    name=y.h3.text.strip(),
                    url=BASE_URL + y.a.get("href"),
                    thumbnail=y.img.get("src"),
                    genre=y.get("data-tags").split("|"),
                    type=y.figure.span.text,
                    score=float(y.find("div", {"class": "score"}).text),
                    status=y.find("div", {"class": "status"}).text,
                )
                for y in self.soup.find("div", {"class": "entries"}).select("article")
            ],
            next_page_url=next_page,
            previous_page_url=previous_page,
        )

    @classmethod
    def search(cls, query: str) -> Optional[SearchResult]:
        """
        Searches for manga by keyword.

        Args:
            query (str): Search keyword

        Returns:
            Optional[SearchResult]: Search results or None if no results found
        """
        x = cls(f"{BASE_URL}/?s={query}")
        return x.get_search()

    @classmethod
    def get_search_by_url(cls, url: str) -> Optional[SearchResult]:
        """
        Retrieves search results from a specific URL.

        Args:
            url (str): URL to search results page

        Returns:
            Optional[SearchResult]: Search results or None if no results found
        """
        x = cls(url)
        return x.get_search()


def example_usage():
    # Example usage
    manga = Doujindesu(
        f"{BASE_URL}/manga/seiwayaki-kaasan-ni-doutei-made-sewa-shitemoraimasu/"
    )

    # Get manga details
    details = manga.get_details()
    if details:
        print(f"Title: {details.name}")
        print(f"Author: {details.author}")

        # Get all chapters
        chapters = manga.get_all_chapters()
        print(f"\nFound {len(chapters)} chapters:")
        for chapter in chapters:
            print(f"- {chapter['title']}: {chapter['url']}")

        # Download specific chapter
        if chapters:
            print("\nDownloading first chapter...")
            images, title = manga.download_chapter(chapters[0]["url"])
            print(f"Downloaded {title} with {len(images)} images")


if __name__ == "__main__":
    example_usage()
