from app.domain.contracts import MetricSummaryResponse
from app.infrastructure.repositories.memory import InMemoryRepository


class MetricsService:
    def __init__(self, repository: InMemoryRepository) -> None:
        self.repository = repository

    def summary(self) -> MetricSummaryResponse:
        return MetricSummaryResponse(**self.repository.metrics_snapshot())

