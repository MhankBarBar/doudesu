"""
API for the Doudesu.
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from ..core import Doujindesu
from ..models.manga import DetailsResult, SearchResult

app = FastAPI(title="Doudesu API", description="API for doudesu library", version="1.0.0")


@app.get("/search/{keyword}", response_model=SearchResult)
async def search(
    keyword: str,
    page: int = Query(default=1, ge=1, description="Page number"),
):
    """
    Search manga by keyword with pagination

    - page: Page number (starts from 1)
    """
    results = Doujindesu.search(keyword, page)
    if not results or not results.results:
        raise HTTPException(status_code=404, detail="No results found")

    return results


@app.get("/manga/{url:path}", response_model=DetailsResult)
async def get_manga_details(url: str):
    """Get manga details by URL"""
    try:
        manga = Doujindesu(url)
        details = manga.get_details()
        if not details:
            raise HTTPException(status_code=404, detail="Manga not found")
        return details
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/manga/{url:path}/chapters")
async def get_chapters(url: str):
    """Get all chapters for a manga"""
    try:
        manga = Doujindesu(url)
        chapters = manga.get_all_chapters()
        if not chapters:
            raise HTTPException(status_code=404, detail="No chapters found")
        return {"chapters": chapters}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chapter/{url:path}/images")
async def get_chapter_images(url: str):
    """Get all images from a chapter"""
    try:
        manga = Doujindesu(url)
        images = manga.get_all_images()
        if not images:
            raise HTTPException(status_code=404, detail="No images found")
        return {"images": images}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
