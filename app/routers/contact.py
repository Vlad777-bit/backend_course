from fastapi import APIRouter
from datetime import datetime
import json
import os

from app.models.contact_models import (
    Contact,
    ExtendedContact,
    ExtendedContactMultiple
)

router = APIRouter()

@router.post("/basic")
async def create_contact(contact: Contact):
    os.makedirs("./app/storage", exist_ok=True)

    data = contact.model_dump(mode='json')
    filename = f"./app/storage/contact_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return {"message": "Данные успешно сохранены", "filename": filename}


@router.post("/extended")
async def create_extended_contact(contact: ExtendedContact):
    os.makedirs("./app/storage", exist_ok=True)

    data = contact.model_dump(mode='json')
    filename = f"./app/storage/contact_extended_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return {"message": "Данные успешно сохранены", "filename": filename}


@router.post("/multiple")
async def create_contact_multiple(contact: ExtendedContactMultiple):
    os.makedirs("./app/storage", exist_ok=True)

    data = contact.model_dump(mode='json')
    filename = f"./app/storage/contact_multiple_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return {"message": "Данные успешно сохранены", "filename": filename}
