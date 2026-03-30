import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Form, Request, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

import app.config
from app.models.house import House, HouseStatus, ZillowData
from app.storage.house_store import HouseStore
from app.services.zillow_scraper import extract_address_from_url

router = APIRouter(prefix="/houses", tags=["houses"])


def _int(val: str) -> int | None:
    return int(val) if val.strip() else None


def _float(val: str) -> float | None:
    return float(val) if val.strip() else None


class FavoritesOrderRequest(BaseModel):
    ordered_ids: list[str]


@router.post("")
async def add_house(
    request: Request,
    zillow_url: str = Form(default=""),
    address: str = Form(default=""),
    price: str = Form(default=""),
    beds: str = Form(default=""),
    baths: str = Form(default=""),
    sqft: str = Form(default=""),
    image_url: str = Form(default=""),
):
    templates = request.app.state.templates
    store = HouseStore(app.config.MEMORY_DIR)
    now = datetime.now(timezone.utc)

    address = address.strip()
    if not address:
        return templates.TemplateResponse(
            request,
            "partials/add_house_form_body.html",
            {
                "validation_error": "Address is required.",
                "zillow_url_value": zillow_url.strip(),
                "address_value": "",
                "price_value": price.strip(),
                "sqft_value": sqft.strip(),
                "beds_value": beds.strip(),
                "baths_value": baths.strip(),
                "image_url_value": image_url.strip(),
            },
        )

    zillow_data = ZillowData(
        address=address,
        price=_int(price),
        beds=_int(beds),
        baths=_float(baths),
        sqft=_int(sqft),
        image_url=image_url.strip() or None,
    )

    house = House(
        id=str(uuid.uuid4()),
        zillow_url=zillow_url.strip(),
        zillow_data=zillow_data,
        added_at=now,
        updated_at=now,
    )

    store.add(house)

    # X-House-Added header signals JS to close modal and reload
    return HTMLResponse(
        '<div class="text-green-600 text-sm p-2">House added successfully!</div>',
        status_code=200,
        headers={"X-House-Added": "true"},
    )


@router.get("/{house_id}/edit")
async def edit_house_form(house_id: str, request: Request):
    templates = request.app.state.templates
    store = HouseStore(app.config.MEMORY_DIR)
    house = store.get(house_id)
    if house is None:
        return Response(status_code=404)
    d = house.zillow_data
    return templates.TemplateResponse(
        request,
        "partials/edit_house_modal.html",
        {
            "house": house,
            "address_value": d.address,
            "price_value": str(d.price) if d.price is not None else "",
            "beds_value": str(d.beds) if d.beds is not None else "",
            "baths_value": str(d.baths) if d.baths is not None else "",
            "sqft_value": str(d.sqft) if d.sqft is not None else "",
            "image_url_value": d.image_url or "",
            "zillow_url_value": house.zillow_url,
            "notes_value": house.notes,
            "annual_property_tax_value": str(house.annual_property_tax) if house.annual_property_tax is not None else "",
            "annual_insurance_value": str(house.annual_insurance) if house.annual_insurance is not None else "",
            "monthly_pmi_override_value": str(house.monthly_pmi_override) if house.monthly_pmi_override is not None else "",
            "monthly_heat_value": str(house.monthly_heat) if house.monthly_heat is not None else "",
            "monthly_water_value": str(house.monthly_water) if house.monthly_water is not None else "",
            "monthly_electric_value": str(house.monthly_electric) if house.monthly_electric is not None else "",
            "monthly_internet_value": str(house.monthly_internet) if house.monthly_internet is not None else "",
        },
    )


@router.patch("/{house_id}")
async def update_house(
    house_id: str,
    zillow_url: str = Form(default=""),
    address: str = Form(default=""),
    price: str = Form(default=""),
    beds: str = Form(default=""),
    baths: str = Form(default=""),
    sqft: str = Form(default=""),
    image_url: str = Form(default=""),
    notes: str = Form(default=""),
    annual_property_tax: str = Form(default=""),
    annual_insurance: str = Form(default=""),
    monthly_pmi_override: str = Form(default=""),
    monthly_heat: str = Form(default=""),
    monthly_water: str = Form(default=""),
    monthly_electric: str = Form(default=""),
    monthly_internet: str = Form(default=""),
):
    store = HouseStore(app.config.MEMORY_DIR)

    address = address.strip()
    if not address:
        return Response(status_code=422)

    new_zillow_data = ZillowData(
        address=address,
        price=_int(price),
        beds=_int(beds),
        baths=_float(baths),
        sqft=_int(sqft),
        image_url=image_url.strip() or None,
    )

    store.update(house_id, {
        "zillow_url": zillow_url.strip(),
        "zillow_data": new_zillow_data,
        "notes": notes,
        "annual_property_tax": _int(annual_property_tax),
        "annual_insurance": _int(annual_insurance),
        "monthly_pmi_override": _int(monthly_pmi_override),
        "monthly_heat": _int(monthly_heat),
        "monthly_water": _int(monthly_water),
        "monthly_electric": _int(monthly_electric),
        "monthly_internet": _int(monthly_internet),
        "updated_at": datetime.now(timezone.utc),
    })

    return Response(status_code=204)


@router.delete("/{house_id}")
async def remove_house(house_id: str) -> Response:
    store = HouseStore(app.config.MEMORY_DIR)
    store.remove(house_id)
    return Response(status_code=200)


@router.patch("/{house_id}/status")
async def update_status(
    house_id: str,
    status: str = Form(default=""),
) -> Response:
    store = HouseStore(app.config.MEMORY_DIR)
    new_status = HouseStatus(status) if status else None
    store.update(house_id, {
        "status": new_status,
        "updated_at": datetime.now(timezone.utc),
    })
    return Response(status_code=200)


@router.patch("/{house_id}/favorite")
async def toggle_favorite(house_id: str) -> Response:
    store = HouseStore(app.config.MEMORY_DIR)
    store.toggle_favorite(house_id)
    return Response(status_code=200)


@router.put("/favorites/order")
async def update_favorites_order(body: FavoritesOrderRequest) -> Response:
    store = HouseStore(app.config.MEMORY_DIR)
    store.update_favorites_order(body.ordered_ids)
    return Response(status_code=204)
