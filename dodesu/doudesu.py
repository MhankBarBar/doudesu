import re
from base64 import b64decode
from dataclasses import dataclass
from typing import Optional

from bs4 import BeautifulSoup as Bs
from rich import print
from tls_client import Session

from .converter import ImageToPDFConverter


@dataclass
class Result:
    name: str
    url: str
    thumbnail: str
    genre: list[str]
    type: str = "Doujinshi"
    score: float = 0
    status: str = "Finished"


@dataclass
class SearchResult:
    results: list[Result]
    next_page_url: str | None = ""
    previous_page_url: str | None = ""


@dataclass
class DetailsResult:
    name: str
    url: str
    thumbnail: str
    genre: list[str]
    series: str
    author: str
    type: str = "Doujinshi"
    score: float = 0
    status: str = "Finished"
    chapter_urls: list[str | None] = list


class Doujindesu(ImageToPDFConverter):
    def __init__(self, url: str, proxy: Optional[str] = None):
        super().__init__()
        self.baseUrl: str = "https://doujindesu.tv"
        self.url: str = url
        self.proxy: Optional[str] = proxy
        self.soup: Optional[Bs] = None

    @property
    def create_session(self) -> Session:
        session = Session(
            client_identifier="chrome_120",
            random_tls_extension_order=True,
        )
        if self.proxy:
            session.proxies.update({"http": self.proxy})
        session.headers.update(
            {
                # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)
                # Chrome/89.0.142.86 Safari/537.36",
                "Referer": "https://doujindesu.tv",
                "X-Requested-With": "XMLHttpRequest",
            }
        )
        return session

    def scrap(self) -> None:
        ses = self.create_session
        content = ses.get(self.url).text
        self.soup = Bs(content, "html.parser")
        ses.close()

    def get_id(self, text: str) -> Optional[int]:
        """
        Extract and return the ID from the given text.

        Args:
            text (str): Input text.

        Returns:
            int | None: Extracted ID or None if not found.
        """
        match = re.search(r"load_data\((\d+)\)", text)
        if match:
            return int(match.group(1))
        else:
            raise ValueError("ID could not be extracted from the text.")

    def get_all_chapters(self) -> list[str]:
        self.scrap()
        urls = list(
            reversed(
                [self.baseUrl + x.a.get("href") for x in self.soup.select("span.eps")]
            )
        )
        return urls

    def get_all_images(self) -> list[str]:
        self.scrap()
        _id = self.get_id(self.soup.prettify())
        ses = self.create_session
        req = ses.post("https://doujindesu.tv/themes/ajax/ch.php", data={"id": _id})
        ses.close()
        imgs = re.findall(r"src=\"(.*?)\"", req.text)
        return imgs

    def get_details(self) -> DetailsResult | None:
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
                reversed(
                    [self.baseUrl + x.a.get("href") for x in soup.select("span.eps")]
                )
            ),
        )

    def get_search(self) -> SearchResult | None:
        self.scrap()
        if "No result found" in self.soup.prettify():
            return None
        next_page = (
            self.baseUrl + self.soup.find("a", {"title": "Next page"}).get("href", None)
            if self.soup.find("a", {"title": "Next page"})
            else None
        )
        previous_page = (
            self.baseUrl
            + self.soup.find("a", {"title": "Previous page"}).get("href", None)
            if self.soup.find("a", {"title": "Previous page"})
            else None
        )
        return SearchResult(
            results=[
                Result(
                    name=y.h3.text.strip(),
                    url=self.baseUrl + y.a.get("href"),
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
    def search(cls, query: str) -> SearchResult | None:
        x = cls(f"https://doujindesu.tv/?s={query}")
        return x.get_search()

    @classmethod
    def get_search_by_url(cls, url: str) -> SearchResult | None:
        x = cls(url)
        return x.get_search()


def main():
    res = Doujindesu(
        "https://doujindesu.tv/manga/seiwayaki-kaasan-ni-doutei-made-sewa-shitemoraimasu/"
    ).get_details()
    print(res)


if __name__ == "__main__":
    main()
