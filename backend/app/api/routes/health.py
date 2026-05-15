from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness(request: Request) -> dict[str, object]:
    settings = request.app.state.settings
    integrations = request.app.state.integrations
    return {
        "status": "ready",
        "app": settings.app_name,
        "version": settings.api_version,
        "environment": settings.environment,
        "integrations": [
            {
                "name": integration.name,
                "adapter": integration.adapter,
                "configured": integration.configured,
            }
            for integration in integrations
        ],
    }
