from dataclasses import dataclass

from app.application.services.assistant_service import AssistantService
from app.application.services.document_service import DocumentService
from app.application.services.feedback_service import FeedbackService
from app.application.services.metrics_service import MetricsService
from app.application.services.telegram_service import TelegramService
from app.core.config import Settings
from app.infrastructure.database.mysql import MySqlConfig, MySqlUnitOfWork
from app.infrastructure.llm.fake_llm import FakeLLMGateway
from app.infrastructure.mcp.simulated_tools import SimulatedToolRegistry
from app.infrastructure.rag.simple_retriever import SimpleRetriever
from app.infrastructure.repositories.memory import InMemoryRepository
from app.infrastructure.vector.qdrant import QdrantConfig, QdrantVectorStore


@dataclass(frozen=True, slots=True)
class IntegrationStatus:
    name: str
    adapter: str
    configured: bool


@dataclass(slots=True)
class BackendContainer:
    repository: InMemoryRepository
    assistant_service: AssistantService
    document_service: DocumentService
    feedback_service: FeedbackService
    metrics_service: MetricsService
    telegram_service: TelegramService
    mysql_uow: MySqlUnitOfWork
    vector_store: QdrantVectorStore
    integrations: list[IntegrationStatus]


def build_container(settings: Settings) -> BackendContainer:
    repository = InMemoryRepository()
    repository.seed_default_documents()

    retriever = SimpleRetriever(repository)
    llm_gateway = FakeLLMGateway()
    tools = SimulatedToolRegistry(enabled=settings.mcp_simulated_enabled)
    mysql_uow = MySqlUnitOfWork(MySqlConfig(url=settings.mysql_url))
    vector_store = QdrantVectorStore(
        QdrantConfig(
            url=settings.qdrant_url,
            collection=settings.qdrant_collection,
        )
    )

    assistant_service = AssistantService(
        repository=repository,
        retriever=retriever,
        llm_gateway=llm_gateway,
        tools=tools,
        settings=settings,
    )

    return BackendContainer(
        repository=repository,
        assistant_service=assistant_service,
        document_service=DocumentService(repository),
        feedback_service=FeedbackService(repository),
        metrics_service=MetricsService(repository),
        telegram_service=TelegramService(assistant_service),
        mysql_uow=mysql_uow,
        vector_store=vector_store,
        integrations=[
            IntegrationStatus(
                name="llm",
                adapter=settings.llm_provider,
                configured=settings.llm_provider == "mock" or bool(settings.llm_api_key),
            ),
            IntegrationStatus(
                name="relational_database",
                adapter="mysql",
                configured=bool(settings.mysql_url),
            ),
            IntegrationStatus(
                name="vector_database",
                adapter="qdrant",
                configured=bool(settings.qdrant_url and settings.qdrant_collection),
            ),
            IntegrationStatus(
                name="telegram",
                adapter="webhook",
                configured=bool(settings.telegram_bot_token),
            ),
            IntegrationStatus(
                name="mcp",
                adapter="simulated",
                configured=settings.mcp_simulated_enabled,
            ),
        ],
    )
