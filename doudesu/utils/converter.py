import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO

import requests
from PIL import Image
from reportlab.pdfgen import canvas
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class ImageDownloader:
    def __init__(self, max_retries: int = 3, timeout: int = 10):
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504, 429],
        )
        self.session.mount("http://", HTTPAdapter(max_retries=retry_strategy))
        self.session.mount("https://", HTTPAdapter(max_retries=retry_strategy))
        self.timeout = timeout
        self.headers = {
            "Referer": "https://doujindesu.tv/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",  # noqa: E501
        }

    def download_single_image(self, url_data: tuple[int, str]) -> tuple[int, Image.Image | None]:
        index, url = url_data
        try:
            response = self.session.get(url, stream=True, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()

            img_data = BytesIO(response.content)
            img = Image.open(img_data)

            if img.mode == "RGBA":
                img = img.convert("RGB")

            return index, img

        except requests.exceptions.RequestException:
            return index, None
        except Exception:
            return index, None


class ImageToPDFConverter:
    def __init__(
        self,
        image_urls: list[str] | None = None,
        output_pdf_file: str = "output.pdf",
        num_threads: int = 10,
        chunk_size: int = 5,
    ):
        self.image_urls = image_urls or []
        self.result_dir = "result"
        os.makedirs(self.result_dir, exist_ok=True)
        self.output_pdf_file = self._add_pdf_extension(os.path.join(self.result_dir, output_pdf_file))
        self.num_threads = min(num_threads, len(image_urls) if image_urls else 10)
        self.chunk_size = chunk_size
        self.downloader = ImageDownloader()

    @staticmethod
    def _add_pdf_extension(filename: str) -> str:
        return filename if filename.lower().endswith(".pdf") else f"{filename}.pdf"

    def download_images_threaded(self, urls: list[str]) -> list[Image.Image | None]:
        total_images = len(urls)
        downloaded_images = [None] * total_images
        failed_downloads = []

        for chunk_start in range(0, total_images, self.chunk_size):
            chunk_end = min(chunk_start + self.chunk_size, total_images)
            chunk_urls = list(enumerate(urls[chunk_start:chunk_end], start=chunk_start))

            with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
                future_to_url = {
                    executor.submit(self.downloader.download_single_image, url_data): url_data
                    for url_data in chunk_urls
                }

                for future in as_completed(future_to_url):
                    index, img = future.result()
                    if img:
                        downloaded_images[index] = img
                    else:
                        failed_downloads.append(index)

        return downloaded_images

    def convert_images_to_pdf(self, images: list[str], output_pdf_file: str, progress_callback=None):
        output_pdf_file = self._add_pdf_extension(output_pdf_file)
        downloaded_images = self.download_images_threaded(images)

        try:
            with open(output_pdf_file, "wb") as pdf_file:
                pdf_canvas = canvas.Canvas(pdf_file)

                for idx, image in enumerate(downloaded_images, 1):
                    if image:
                        try:
                            pdf_canvas.setPageSize((image.width, image.height))
                            pdf_canvas.drawInlineImage(image, 0, 0, image.width, image.height)
                            pdf_canvas.showPage()
                        except Exception:
                            continue
                    if progress_callback:
                        progress_callback(idx, len(downloaded_images))

                pdf_canvas.save()

        except Exception:
            raise
