from enum import Enum

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class HouseStatus(str, Enum):
    IN_THE_RUNNING = "in_the_running"
    LOVE = "love"
    NO = "no"
    OFFER_SUBMITTED = "offer_submitted"


STATUS_LABELS: dict[HouseStatus, str] = {
    HouseStatus.IN_THE_RUNNING: "In the Running",
    HouseStatus.LOVE: "Love",
    HouseStatus.NO: "No",
    HouseStatus.OFFER_SUBMITTED: "Offer Submitted",
}

STATUS_COLORS: dict[HouseStatus, str] = {
    HouseStatus.IN_THE_RUNNING: "blue",
    HouseStatus.LOVE: "pink",
    HouseStatus.NO: "red",
    HouseStatus.OFFER_SUBMITTED: "green",
}


class ZillowData(BaseModel):
    address: str = ""
    price: Optional[int] = None
    beds: Optional[int] = None
    baths: Optional[float] = None
    sqft: Optional[int] = None
    image_url: Optional[str] = None


class House(BaseModel):
    id: str
    zillow_url: str
    zillow_data: ZillowData
    notes: str = ""
    annual_property_tax: Optional[int] = None
    annual_insurance: Optional[int] = None
    monthly_pmi_override: Optional[int] = None
    monthly_heat: Optional[int] = None
    monthly_water: Optional[int] = None
    monthly_electric: Optional[int] = None
    monthly_internet: Optional[int] = None
    is_favorite: bool = False
    favorite_sort_order: Optional[int] = None
    status: Optional[HouseStatus] = None
    added_at: datetime
    updated_at: datetime
