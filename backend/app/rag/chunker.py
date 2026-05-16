import re
from typing import Iterable


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def chunk_text(text: str, max_words: int = 120, overlap: int = 20) -> list[str]:
    """Quebra um texto em chunks de tamanho aproximado em palavras.

    A sobreposição ajuda a preservar o contexto entre pedaços consecutivos.
    """
    normalized = normalize_text(text)
    if not normalized:
        return []

    words = normalized.split(" ")
    if max_words <= 0:
        raise ValueError("max_words deve ser maior que zero")
    if overlap < 0:
        raise ValueError("overlap não pode ser negativo")

    chunks: list[str] = []
    step = max(1, max_words - overlap)
    for start in range(0, len(words), step):
        chunk = words[start : start + max_words]
        if not chunk:
            break
        chunks.append(" ".join(chunk))
        if start + max_words >= len(words):
            break

    return chunks


def chunk_documents(documents: Iterable[dict], max_words: int = 120, overlap: int = 20) -> list[dict]:
    """Gera chunks para uma coleção de documentos.

    Cada item devolvido inclui metadados suficientes para indexação.
    """
    result: list[dict] = []
    for document in documents:
        for index, chunk in enumerate(chunk_text(document["content"], max_words=max_words, overlap=overlap), start=1):
            result.append(
                {
                    "document_id": document["id"],
                    "chunk_id": f"{document['id']}-{index}",
                    "title": document.get("title"),
                    "category": document.get("category"),
                    "version": document.get("version"),
                    "content": chunk,
                    "source": document.get("source"),
                    "start_word": (index - 1) * (max_words - overlap) + 1,
                    "end_word": min(len(normalize_text(document["content"]).split(" ")), (index - 1) * (max_words - overlap) + max_words),
                }
            )
    return result
