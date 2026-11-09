from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db.database import close_pool, init_pool
from app.routers import championships, health, rounds, simulate


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_pool()
    yield
    close_pool()


settings = get_settings()
app = FastAPI(
    title="Coffee Bean Optimization API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(rounds.router)
app.include_router(simulate.router)
app.include_router(championships.router)


@app.get("/")
def root() -> dict:
    return {
        "service": "Coffee Bean Optimization API",
        "status": "ok",
        "docs": "/docs",
        "health": "/health",
        "game": "https://coffee-bean-optimization.netlify.app",
        "rounds": "/rounds",
    }
