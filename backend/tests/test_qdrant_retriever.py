from app.core.config import Settings
from app.infrastructure.repositories.memory import InMemoryRepository
from app.infrastructure.vector.qdrant import _chunk_embedding_text, _embed


def test_known_question_is_above_qdrant_relevance_threshold() -> None:
    repository = InMemoryRepository()
    repository.seed_default_documents()
    chunk = next(
        item
        for item in repository.list_active_chunks()
        if item.metadata["title"] == "Procedimento de abertura de chamado"
    )

    question_vector = _embed("Como abrir chamado no suporte?")
    chunk_vector = _embed(_chunk_embedding_text(chunk))
    score = sum(
        question_value * chunk_value
        for question_value, chunk_value in zip(question_vector, chunk_vector, strict=True)
    )

    assert score >= Settings().min_relevance_score
