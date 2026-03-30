from pydantic import BaseModel
from datetime import datetime
from typing import Optional


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
    added_at: datetime
    updated_at: datetime
