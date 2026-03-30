import uuid

from fastapi import APIRouter, Form, Request
from fastapi.responses import Response
from pydantic import BaseModel

import app.config
from app.models.link import Link
from app.storage.link_store import LinkStore

router = APIRouter(prefix="/links", tags=["links"])


class LinkOrderRequest(BaseModel):
    ordered_ids: list[str]


@router.get("")
async def links_page(request: Request):
    templates = request.app.state.templates
    store = LinkStore(app.config.MEMORY_DIR)
    links = store.list_all()
    return templates.TemplateResponse(request, "links.html", {"links": links})


@router.post("")
async def add_link(
    request: Request,
    text: str = Form(...),
    url: str = Form(...),
):
    templates = request.app.state.templates
    store = LinkStore(app.config.MEMORY_DIR)

    text = text.strip()
    url = url.strip()

    link = Link(id=str(uuid.uuid4()), text=text, url=url, sort_order=0)
    store.add(link)

    links = store.list_all()
    return templates.TemplateResponse(request, "partials/link_list.html", {"links": links})


@router.get("/{link_id}/row")
async def link_row(link_id: str, request: Request):
    templates = request.app.state.templates
    store = LinkStore(app.config.MEMORY_DIR)
    link = store.get(link_id)
    if link is None:
        return Response(status_code=404)
    return templates.TemplateResponse(request, "partials/link_row.html", {"link": link})


@router.get("/{link_id}/edit")
async def link_edit_row(link_id: str, request: Request):
    templates = request.app.state.templates
    store = LinkStore(app.config.MEMORY_DIR)
    link = store.get(link_id)
    if link is None:
        return Response(status_code=404)
    return templates.TemplateResponse(request, "partials/link_edit_row.html", {"link": link})


@router.patch("/{link_id}")
async def update_link(
    link_id: str,
    request: Request,
    text: str = Form(...),
    url: str = Form(...),
):
    templates = request.app.state.templates
    store = LinkStore(app.config.MEMORY_DIR)
    updated = store.update(link_id, text=text.strip(), url=url.strip())
    if updated is None:
        return Response(status_code=404)
    return templates.TemplateResponse(request, "partials/link_row.html", {"link": updated})


@router.delete("/{link_id}")
async def delete_link(link_id: str, request: Request):
    templates = request.app.state.templates
    store = LinkStore(app.config.MEMORY_DIR)
    store.remove(link_id)
    links = store.list_all()
    return templates.TemplateResponse(request, "partials/link_list.html", {"links": links})


@router.put("/order")
async def update_order(body: LinkOrderRequest) -> Response:
    store = LinkStore(app.config.MEMORY_DIR)
    store.update_order(body.ordered_ids)
    return Response(status_code=204)
