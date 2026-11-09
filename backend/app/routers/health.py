from fastapi import APIRouter

from app.db.database import db_available

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "database": "connected" if db_available() else "memory",
        "service": "coffee-bean-optimization",
    }
