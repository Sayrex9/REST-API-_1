from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

app = FastAPI(title="API Объявлений Купли/Продажи")


# --- МОДЕЛИ ДАННЫХ (Pydantic) ---
class AdCreate(BaseModel):
    title: str
    description: str
    price: float
    author: str


class AdUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    author: Optional[str] = None


class AdResponse(AdCreate):
    id: int
    created_at: str


# --- НАША "БАЗА ДАННЫХ" (в памяти) ---
ads_db = {}
ad_id_counter = 1

# --- РОУТЫ ---


# 1. Создание: POST /advertisement
@app.post("/advertisement", response_model=AdResponse, status_code=201)
async def create_ad(ad: AdCreate):
    global ad_id_counter
    new_ad = {
        "id": ad_id_counter,
        "title": ad.title,
        "description": ad.description,
        "price": ad.price,
        "author": ad.author,
        "created_at": datetime.now().isoformat()
    }
    ads_db[ad_id_counter] = new_ad
    ad_id_counter += 1
    return new_ad


# 2. Получение по id: GET /advertisement/{id}
@app.get("/advertisement/{advertisement_id}", response_model=AdResponse)
async def get_ad(advertisement_id: int):
    ad = ads_db.get(advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    return ad


# 3. Обновление: PATCH /advertisement/{id}
@app.patch("/advertisement/{advertisement_id}", response_model=AdResponse)
async def update_ad(advertisement_id: int, ad_update: AdUpdate):
    ad = ads_db.get(advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Объявление не найдено")

    # Обновляем только те поля, которые пришли в запросе (не None)
    update_data = ad_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        ad[key] = value

    return ad


# 4. Удаление: DELETE /advertisement/{id}
@app.delete("/advertisement/{advertisement_id}", status_code=204)
async def delete_ad(advertisement_id: int):
    if advertisement_id not in ads_db:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    del ads_db[advertisement_id]
    return None  # При 204 No Content ничего не возвращаем


# 5. Поиск по полям: GET /advertisement?{query_string}
@app.get("/advertisement", response_model=List[AdResponse])
async def search_advertisements(
    title: Optional[str] = None,
    author: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    results = list(ads_db.values())

    # Фильтруем по очереди
    if title:
        results = [ad for ad in results if title.lower() in ad['title'].lower()]
    if author:
        results = [ad for ad in results if author.lower() == ad['author'].lower()]
    if min_price is not None:
        results = [ad for ad in results if ad['price'] >= min_price]
    if max_price is not None:
        results = [ad for ad in results if ad['price'] <= max_price]

    return results
