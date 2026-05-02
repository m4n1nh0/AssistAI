from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_metrics_service
from app.application.services.metrics_service import MetricsService
from app.domain.contracts import MetricSummaryResponse

router = APIRouter()
MetricsServiceDep = Annotated[MetricsService, Depends(get_metrics_service)]


@router.get("/metrics", response_model=MetricSummaryResponse)
def metrics(
    service: MetricsServiceDep,
) -> MetricSummaryResponse:
    return service.summary()
