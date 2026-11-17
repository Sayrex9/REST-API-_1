from fastapi import FastAPI
from routers import users, ads

app = FastAPI(title="API Объявлений (Clean Architecture)")

app.include_router(users.router)
app.include_router(ads.router)
