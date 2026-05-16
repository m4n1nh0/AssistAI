from app.domain.models import DocumentChunk, KnowledgeDocument, new_id
from app.infrastructure.vector.embeddings import HashEmbeddingGenerator

DEFAULT_CHUNK_WORDS = 90
DEFAULT_CHUNK_OVERLAP = 18


def chunk_document(
    document: KnowledgeDocument,
    embedding_generator: HashEmbeddingGenerator | None = None,
    max_words: int = DEFAULT_CHUNK_WORDS,
    overlap_words: int = DEFAULT_CHUNK_OVERLAP,
) -> list[DocumentChunk]:
    generator = embedding_generator or HashEmbeddingGenerator()
    chunks: list[DocumentChunk] = []

    chunks_text = chunk_text(document.content, max_words, overlap_words)
    for index, content in enumerate(chunks_text, start=1):
        metadata = {
            "document_id": document.id,
            "title": document.title,
            "category": document.category,
            "version": document.version,
            "status": document.status.value,
            "source": document.source,
            "tags": ",".join(document.tags),
            "chunk_index": str(index),
        }
        embedded_text = " ".join(
            [
                document.title,
                document.category,
                " ".join(document.tags),
                content,
            ]
        )
        chunks.append(
            DocumentChunk(
                id=new_id("chk"),
                document_id=document.id,
                content=content,
                metadata=metadata,
                embedding=generator.embed(embedded_text),
            )
        )

    return chunks


def chunk_text(
    text: str,
    max_words: int = DEFAULT_CHUNK_WORDS,
    overlap_words: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    if max_words <= 0:
        raise ValueError("max_words must be greater than zero.")
    if overlap_words < 0 or overlap_words >= max_words:
        raise ValueError("overlap_words must be between zero and max_words - 1.")

    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    step = max_words - overlap_words
    for start in range(0, len(words), step):
        chunk_words = words[start : start + max_words]
        if not chunk_words:
            break
        chunks.append(" ".join(chunk_words))
        if start + max_words >= len(words):
            break

    return chunks
