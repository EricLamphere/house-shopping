from fastapi import APIRouter
from fastapi.responses import JSONResponse

import app.config
from app.models.assets import UserAssets
from app.storage.assets_store import AssetsStore

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("")
async def get_assets():
    store = AssetsStore(app.config.MEMORY_DIR)
    assets = store.read()
    return JSONResponse(content=assets.model_dump())


@router.put("")
async def update_assets(assets: UserAssets):
    store = AssetsStore(app.config.MEMORY_DIR)
    store.write(assets)
    return JSONResponse(content=assets.model_dump())
