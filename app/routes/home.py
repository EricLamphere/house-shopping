from fastapi import APIRouter, Request

import app.config
from app.models.house import HouseStatus, STATUS_LABELS, STATUS_COLORS
from app.storage.house_store import HouseStore

router = APIRouter()

_STATUS_ORDER = [
    HouseStatus.OFFER_SUBMITTED,
    HouseStatus.LOVE,
    HouseStatus.IN_THE_RUNNING,
    HouseStatus.NO,
]


@router.get("/")
async def homepage(request: Request):
    templates = request.app.state.templates
    store = HouseStore(app.config.MEMORY_DIR)

    favorites = store.list_favorites()
    houses = store.list_all()

    # Build grouped view: ordered by _STATUS_ORDER, then ungrouped at end
    grouped: list[dict] = []
    for status in _STATUS_ORDER:
        group_houses = [h for h in houses if h.status == status]
        if group_houses:
            grouped.append({
                "label": STATUS_LABELS[status],
                "color": STATUS_COLORS[status],
                "houses": group_houses,
            })
    ungrouped = [h for h in houses if h.status is None]
    if ungrouped:
        grouped.append({
            "label": "Unsorted",
            "color": "gray",
            "houses": ungrouped,
        })

    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "favorites": favorites,
            "houses": houses,
            "grouped": grouped,
            "status_options": [
                {"value": s.value, "label": STATUS_LABELS[s], "color": STATUS_COLORS[s]}
                for s in HouseStatus
            ],
        },
    )
