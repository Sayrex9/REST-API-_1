from fastapi import APIRouter, HTTPException, Depends
from schemas import UserCreate, UserUpdate, UserResponse, LoginRequest
from auth import hash_password, verify_password, create_access_token, require_auth
from database import users_db
import routers
import database

router = APIRouter(tags=["Users"])


@router.post("/login")
async def login(data: LoginRequest):
    for user in users_db.values():
        if user["username"] == data.username and verify_password(data.password, user["password_hash"]):
            token = create_access_token({"user_id": user["id"], "role": user["role"]})
            return {"token": token}
    raise HTTPException(status_code=401, detail="Неверный логин или пароль")


@router.post("/user", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate):
    for u in users_db.values():
        if u["username"] == user.username:
            raise HTTPException(status_code=400, detail="Пользователь уже существует")

    new_user = {
        "id": database.user_id_counter,
        "username": user.username,
        "password_hash": hash_password(user.password),
        "role": user.role if user.role in ["user", "admin"] else "user"
    }
    users_db[database.user_id_counter] = new_user
    database.user_id_counter += 1
    return new_user


@router.get("/user/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@router.patch("/user/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, current_user: dict = Depends(require_auth)):
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if current_user["role"] != "admin" and current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["password_hash"] = hash_password(update_data.pop("password"))
    if "role" in update_data and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Только админ может менять роли")

    for key, value in update_data.items():
        user[key] = value
    return user


@router.delete("/user/{user_id}", status_code=204)
async def delete_user(user_id: int, current_user: dict = Depends(require_auth)):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if current_user["role"] != "admin" and current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Недостаточно прав для удаления")
    del users_db[user_id]
    return None
