from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel

class ItemInput(BaseModel):
    name: str
    category: str
    price: int
    is_buffed: bool = False
    description: Optional[str] = None

app = FastAPI(
    title="Monochaco API"
    ,description="API do Amumu do monochaco"
    ,version="1.0.0",
)

items = [
    {"id": 1, "name": "Liandry", "category": "AP/DPS", "price": 3000, 'is_buffed': True}
    ,{"id": 2, "name": "Sunfire Cape", "category": "Tank/DPS", "price": 2750, 'is_buffed': True}
    ,{"id": 3, "name": "BlackFire Torch", "category": "AP/DPS", "price": 2800, 'is_buffed': True}
    ,{"id": 4, "name": "Bota de Pen", "category": "Move Speed/Pen", "price": 900, 'is_buffed': False}
    ,{"id": 5, "name": "Abyssal Mask", "category": "Reduce MR of Targeted Champion", "price": 2650, 'is_buffed': True}
    ,{"id": 6, "name": "Jak'Sho", "category": "Armour/MR", "price": 3200, 'is_buffed': True}
]

@app.post("/items")
async def add_item(items: ItemInput):
    new_id = max(p["id"] for p in items) + 1.=
    new_item = {"id": new_id, **items.model_dump()}
    items.append(new_item)
    return new_item

