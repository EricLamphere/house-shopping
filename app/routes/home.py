from fastapi import APIRouter, Request

import app.config
from app.storage.house_store import HouseStore

router = APIRouter()


@router.get("/")
async def homepage(request: Request):
    templates = request.app.state.templates
    store = HouseStore(app.config.MEMORY_DIR)

    favorites = store.list_favorites()
    houses = store.list_all()

    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "favorites": favorites,
            "houses": houses,
        },
    )
