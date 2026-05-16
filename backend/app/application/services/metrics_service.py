from app.domain.contracts import MetricSummaryResponse
from app.domain.protocols import Repository


class MetricsService:
    def __init__(self, repository: Repository) -> None:
        self.repository = repository

    def summary(self) -> MetricSummaryResponse:
        return MetricSummaryResponse(**self.repository.metrics_snapshot())

