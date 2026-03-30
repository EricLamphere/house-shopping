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
    is_favorite: bool = False
    favorite_sort_order: Optional[int] = None
    added_at: datetime
    updated_at: datetime
