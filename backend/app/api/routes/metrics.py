from fastapi import APIRouter, Depends

from app.application.services.metrics_service import MetricsService, get_metrics_service
from app.schemas.metrics import MetricsResponse

router = APIRouter()


@router.get("/metrics", response_model=MetricsResponse)
def get_metrics(
    service: MetricsService = Depends(get_metrics_service),
) -> MetricsResponse:
    return service.get_summary()
