from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from datetime import datetime
from schemas import AdCreate, AdUpdate, AdResponse
from auth import require_auth
from database import ads_db
import database

router = APIRouter(tags=["Advertisements"])


@router.post("/advertisement", response_model=AdResponse, status_code=201)
async def create_ad(ad: AdCreate, current_user: dict = Depends(require_auth)):
    new_ad = {
        "id": database.ad_id_counter,
        "title": ad.title,
        "description": ad.description,
        "price": ad.price,
        "author": ad.author,
        "created_at": datetime.now().isoformat(),
        "owner_id": current_user["id"]
    }
    ads_db[database.ad_id_counter] = new_ad
    database.ad_id_counter += 1
    return new_ad


@router.get("/advertisement/{advertisement_id}", response_model=AdResponse)
async def get_ad(advertisement_id: int):
    ad = ads_db.get(advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    return ad


@router.patch("/advertisement/{advertisement_id}", response_model=AdResponse)
async def update_ad(advertisement_id: int, ad_update: AdUpdate, current_user: dict = Depends(require_auth)):
    ad = ads_db.get(advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Объявление не найдено")

    if current_user["role"] != "admin" and ad["owner_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Вы не являетесь владельцем")

    update_data = ad_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        ad[key] = value
    return ad


@router.delete("/advertisement/{advertisement_id}", status_code=204)
async def delete_ad(advertisement_id: int, current_user: dict = Depends(require_auth)):
    ad = ads_db.get(advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Объявление не найдено")

    if current_user["role"] != "admin" and ad["owner_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Вы не являетесь владельцем")

    del ads_db[advertisement_id]
    return None


@router.get("/advertisement", response_model=List[AdResponse])
async def search_advertisements(
    title: Optional[str] = None,
    author: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    results = list(ads_db.values())
    if title:
        results = [ad for ad in results if title.lower() in ad['title'].lower()]
    if author:
        results = [ad for ad in results if author.lower() == ad['author'].lower()]
    if min_price is not None:
        results = [ad for ad in results if ad['price'] >= min_price]
    if max_price is not None:
        results = [ad for ad in results if ad['price'] <= max_price]
    return results
