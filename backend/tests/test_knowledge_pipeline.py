from pathlib import Path

from app.domain.contracts import DocumentCreateRequest
from app.domain.enums import DocumentStatus
from app.infrastructure.knowledge.chunking import chunk_document, chunk_text
from app.infrastructure.knowledge.loader import load_documents
from app.infrastructure.repositories.memory import InMemoryRepository
from app.infrastructure.vector.embeddings import HashEmbeddingGenerator, cosine_similarity


def test_load_markdown_splits_sections_into_documents(tmp_path: Path) -> None:
    knowledge_file = tmp_path / "suporte.md"
    knowledge_file.write_text(
        "\n".join(
            [
                "# Suporte Interno",
                "",
                "## Abertura de chamado",
                "",
                "Abra pelo portal de suporte e acompanhe pelo protocolo.",
                "",
                "## Reset de senha",
                "",
                "Use a recuperacao de senha do portal corporativo.",
            ]
        ),
        encoding="utf-8",
    )

    documents = load_documents(tmp_path)

    assert [document.title for document in documents] == [
        "Abertura de chamado",
        "Reset de senha",
    ]
    assert all(document.category == "suporte-interno" for document in documents)
    assert all(document.source.endswith("suporte.md") for document in documents)


def test_load_json_accepts_document_collection(tmp_path: Path) -> None:
    knowledge_file = tmp_path / "base.json"
    knowledge_file.write_text(
        """
        {
          "documents": [
            {
              "title": "Horario de atendimento",
              "category": "suporte",
              "content": "O suporte atende em dias uteis das 8h as 18h."
            }
          ]
        }
        """,
        encoding="utf-8",
    )

    documents = load_documents(knowledge_file)

    assert len(documents) == 1
    assert documents[0].title == "Horario de atendimento"
    assert documents[0].status == DocumentStatus.ACTIVE


def test_chunk_text_uses_overlap_between_chunks() -> None:
    words = [f"palavra{index}" for index in range(1, 11)]

    chunks = chunk_text(" ".join(words), max_words=4, overlap_words=1)

    assert chunks == [
        "palavra1 palavra2 palavra3 palavra4",
        "palavra4 palavra5 palavra6 palavra7",
        "palavra7 palavra8 palavra9 palavra10",
    ]


def test_chunk_document_generates_embeddings_and_metadata() -> None:
    repository = InMemoryRepository()
    document = repository.create_document(
        DocumentCreateRequest(
            title="Reset de senha",
            category="acesso",
            content="Para resetar senha, use o portal corporativo.",
            tags=["senha", "acesso"],
        )
    )

    chunks = chunk_document(document)

    assert len(chunks) == 1
    assert chunks[0].metadata["title"] == "Reset de senha"
    assert chunks[0].embedding


def test_hash_embedding_is_stable_for_similar_support_texts() -> None:
    generator = HashEmbeddingGenerator()

    first = generator.embed("abrir chamado no portal de suporte")
    second = generator.embed("chamado suporte portal")

    assert cosine_similarity(first, second) > 0.0
