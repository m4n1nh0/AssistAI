from app.application.services.assistant_service import AssistantService as ModernAssistantService
from app.core.config import get_settings
from app.domain.contracts import AskRequest
from app.domain.enums import Channel
from app.infrastructure.llm.fake_llm import FakeLLMGateway
from app.infrastructure.mcp.simulated_tools import SimulatedToolRegistry
from app.infrastructure.repositories.memory import InMemoryRepository
from app.infrastructure.vector.qdrant import HybridRetriever, QdrantConfig, QdrantVectorStore


class AssistantService:
    def __init__(self) -> None:
        settings = get_settings()
        repository = InMemoryRepository()
        repository.seed_default_documents()
        retriever = HybridRetriever(
            repository,
            QdrantVectorStore(
                QdrantConfig(url=settings.qdrant_url, collection=settings.qdrant_collection)
            ),
        )
        retriever.index_documents()
        self._service = ModernAssistantService(
            repository=repository,
            retriever=retriever,
            llm_gateway=FakeLLMGateway(),
            tools=SimulatedToolRegistry(),
            settings=settings,
        )

    def ask(self, user_id: str, channel: Channel, message: str) -> dict:
        response = self._service.ask(
            AskRequest(user_id=user_id, channel=channel, message=message)
        )
        body = response.model_dump(mode="json")
        body["needs_human"] = body["fallback"] or body["intent"] == "solicitacao_humana"
        body["suggested_actions"] = (
            ["acionar humano", "registrar lacuna da base"]
            if body["needs_human"]
            else ["avaliar resposta", "consultar fontes"]
        )
        return body


assistant_service = AssistantService()
