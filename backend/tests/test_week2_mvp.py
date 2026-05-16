from app.application.services.assistant_service import AssistantService
from app.application.services.feedback_service import FeedbackService
from app.core.config import Settings
from app.domain.contracts import AskRequest, FeedbackRequest
from app.domain.enums import Channel
from app.infrastructure.llm.fake_llm import ContextOnlyLLMGateway
from app.infrastructure.llm.prompt import BASE_SYSTEM_PROMPT, FALLBACK_ANSWER, render_user_prompt
from app.infrastructure.mcp.simulated_tools import SimulatedToolRegistry
from app.infrastructure.rag.simple_retriever import SimpleRetriever
from app.infrastructure.repositories.memory import InMemoryRepository


class AuditSpy:
    def __init__(self) -> None:
        self.interactions: list[dict] = []
        self.feedbacks: list[object] = []

    def persist_interaction(self, **kwargs) -> None:
        self.interactions.append(kwargs)

    def persist_feedback(self, feedback) -> None:
        self.feedbacks.append(feedback)


def build_service(
    min_relevance_score: float = 0.15,
    audit_store: AuditSpy | None = None,
) -> tuple[AssistantService, InMemoryRepository]:
    repository = InMemoryRepository()
    repository.seed_default_documents()
    service = AssistantService(
        repository=repository,
        retriever=SimpleRetriever(repository),
        llm_gateway=ContextOnlyLLMGateway(),
        tools=SimulatedToolRegistry(enabled=True),
        settings=Settings(
            min_relevance_score=min_relevance_score,
            mysql_persistence_enabled=False,
        ),
        audit_store=audit_store,
    )
    return service, repository


def test_base_prompt_explicitly_restricts_answer_to_context() -> None:
    service, _repository = build_service()
    contexts = service.retriever.search("Como abrir chamado no suporte?", top_k=1)

    prompt = render_user_prompt("Como abrir chamado no suporte?", contexts)

    assert "Use exclusivamente as informacoes em CONTEXTO_RECUPERADO" in BASE_SYSTEM_PROMPT
    assert FALLBACK_ANSWER in BASE_SYSTEM_PROMPT
    assert "CONTEXTO_RECUPERADO" in prompt
    assert "PERGUNTA_DO_USUARIO" in prompt
    assert "Procedimento de abertura de chamado" in prompt


def test_context_only_llm_uses_retrieved_context_and_fallbacks_without_context() -> None:
    service, _repository = build_service()
    contexts = service.retriever.search("Como abrir chamado no suporte?", top_k=1)
    llm = ContextOnlyLLMGateway()

    answer = llm.generate("Como abrir chamado no suporte?", contexts)
    fallback = llm.generate("Qual e a capital da Islandia?", [])

    assert answer.safe_to_answer is True
    assert "Com base em Procedimento de abertura de chamado" in answer.answer
    assert fallback.safe_to_answer is False
    assert fallback.answer == FALLBACK_ANSWER


def test_relevance_threshold_blocks_low_confidence_context() -> None:
    service, _repository = build_service(min_relevance_score=0.99)

    response = service.ask(
        AskRequest(
            user_id="web-user-001",
            channel=Channel.WEB,
            message="Como abrir chamado no suporte?",
        )
    )

    assert response.fallback is True
    assert response.confidence == 0.0
    assert response.sources == []
    assert response.answer == FALLBACK_ANSWER


def test_assistant_persists_interaction_to_audit_store() -> None:
    audit = AuditSpy()
    service, _repository = build_service(audit_store=audit)

    response = service.ask(
        AskRequest(
            user_id="web-user-001",
            channel=Channel.WEB,
            message="Como abrir chamado no suporte?",
        )
    )

    assert response.fallback is False
    assert len(audit.interactions) == 1
    persisted = audit.interactions[0]
    assert persisted["user"].external_id == "web-user-001"
    assert persisted["message"].id == response.message_id
    assert persisted["message"].sources
    assert persisted["ai_log"].relevance_score == response.confidence


def test_feedback_persists_linked_to_message_in_audit_store() -> None:
    audit = AuditSpy()
    service, repository = build_service(audit_store=audit)
    response = service.ask(
        AskRequest(
            user_id="web-user-001",
            channel=Channel.WEB,
            message="Como abrir chamado no suporte?",
        )
    )
    feedback_service = FeedbackService(repository=repository, audit_store=audit)

    feedback = feedback_service.register(
        FeedbackRequest(message_id=response.message_id, useful=True)
    )

    assert feedback.message_id == response.message_id
    assert len(audit.feedbacks) == 1
    assert audit.feedbacks[0].message_id == response.message_id
