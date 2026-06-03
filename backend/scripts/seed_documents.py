from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings
from app.infrastructure.repositories.memory import InMemoryRepository
from app.infrastructure.vector.qdrant import HybridRetriever, QdrantConfig, QdrantVectorStore


def main() -> None:
    settings = get_settings()
    repository = InMemoryRepository()
    repository.seed_default_documents()

    retriever = HybridRetriever(
        repository,
        QdrantVectorStore(
            QdrantConfig(url=settings.qdrant_url, collection=settings.qdrant_collection)
        ),
    )
    documents, chunks, mode = retriever.index_documents()

    print(f"Documentos ingeridos: {documents}")
    print(f"Chunks indexados: {chunks}")
    print(f"Indice utilizado: {mode}")
    if mode == "local":
        print("Qdrant indisponivel ou dependencia ausente; fallback local validado.")


if __name__ == "__main__":
    main()
