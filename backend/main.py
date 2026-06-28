from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text
from db import get_db, get_redis, init_db
from routers import auth
from core.config import settings

app = FastAPI(
    title="GEO Platform API",
    docs_url=None if settings.production else "/docs",
    redoc_url=None if settings.production else "/redoc",
)

app.include_router(auth.router)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    db_status = "ok"
    redis_status = "ok"

    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    try:
        r = get_redis()
        r.ping()
    except Exception:
        redis_status = "error"

    overall = "ok" if db_status == "ok" and redis_status == "ok" else "degraded"
    return JSONResponse({"status": overall, "db": db_status, "redis": redis_status})
