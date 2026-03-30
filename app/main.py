import logging
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import Response, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.config import MEMORY_DIR
from app.services.image_proxy import fetch_image

logger = logging.getLogger("uvicorn.error")


def create_app() -> FastAPI:
    app = FastAPI(title="House Shopping App")

    app_dir = Path(__file__).parent
    app.mount("/static", StaticFiles(directory=app_dir / "static"), name="static")

    templates = Jinja2Templates(directory=app_dir / "templates")
    app.state.templates = templates
    app.state.memory_dir = MEMORY_DIR

    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    from app.routes import home, houses, cost_estimator, assets
    app.include_router(home.router)
    app.include_router(houses.router)
    app.include_router(cost_estimator.router)
    app.include_router(assets.router)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        body = await request.body()
        logger.error(
            "422 on %s %s | content-type: %s | body: %s | errors: %s",
            request.method, request.url.path,
            request.headers.get("content-type", "none"),
            body[:500],
            exc.errors(),
        )
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/proxy/image")
    async def proxy_image(url: str):
        try:
            content, content_type = await fetch_image(url)
            return Response(content=content, media_type=content_type)
        except Exception:
            return Response(status_code=404)

    return app
