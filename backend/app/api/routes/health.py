from fastapi import APIRouter

from app.infrastructure.qdrant_client import QdrantGateway

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/qdrant")
def qdrant_health_check() -> dict[str, bool | str]:
    return QdrantGateway().ping()
