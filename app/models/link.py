from pydantic import BaseModel


class Link(BaseModel):
    id: str
    text: str
    url: str
    sort_order: int
