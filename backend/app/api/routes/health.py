from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def ready(request: Request) -> dict[str, object]:
    vector_store = request.app.state.vector_store
    settings = request.app.state.settings
    return {
        "status": "ok",
        "mysql": {
            "configured": bool(settings.mysql_url),
            "url": settings.mysql_url,
        },
        "qdrant": {
            "configured": bool(settings.qdrant_url),
            "url": settings.qdrant_url,
            "collection": settings.qdrant_collection,
            "available": vector_store.available,
        },
        "documents": len(request.app.state.repository.list_documents()),
        "chunks": len(request.app.state.repository.list_active_chunks()),
    }

