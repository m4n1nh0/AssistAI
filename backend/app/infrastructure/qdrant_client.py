import importlib.util

from app.core.config import settings
from app.domain.entities import KnowledgeDocument
from app.infrastructure.embedding_client import EmbeddingClient
from app.rag.chunker import chunk_text

qdrant_spec = importlib.util.find_spec("qdrant_client")
if qdrant_spec is not None:
    qdrant_module = importlib.import_module("qdrant_client")
    QdrantClient = qdrant_module.QdrantClient
    Distance = qdrant_module.http.models.Distance
    PointStruct = qdrant_module.http.models.PointStruct
    VectorParams = qdrant_module.http.models.VectorParams
    _QDRANT_AVAILABLE = True
else:  # pragma: no cover
    QdrantClient = None
    Distance = None
    PointStruct = None
    VectorParams = None
    _QDRANT_AVAILABLE = False


class QdrantUnavailableError(RuntimeError):
    """Raised when Qdrant is unavailable or cannot be reached."""


class QdrantGateway:
    """Gateway para Qdrant com indexação vetorial e pesquisa semântica."""

    def __init__(self) -> None:
        self.collection_name = settings.qdrant_collection
        self.embedding_client = EmbeddingClient()
        self.vector_size = 1536
        self.client = None
        self.last_error: str | None = None

        if _QDRANT_AVAILABLE:
            try:
                self.client = QdrantClient(url=settings.qdrant_url)
                self._ensure_collection()
            except Exception as exc:
                self.client = None
                self.last_error = str(exc)

    def _ensure_collection(self) -> None:
        collections = [collection.name for collection in self.client.get_collections().collections]
        if self.collection_name not in collections:
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors=VectorParams(size=self.vector_size, distance=Distance.COSINE),
            )

    def _ensure_available(self) -> None:
        if not _QDRANT_AVAILABLE or self.client is None:
            error_message = self.last_error or "Qdrant não está disponível. Verifique se o serviço Qdrant está em execução em QDRANT_URL."
            raise QdrantUnavailableError(error_message)

    def index_documents(self, documents: list[KnowledgeDocument]) -> int:
        self._ensure_available()

        points = []

        for document in documents:
            for index, chunk in enumerate(chunk_text(document.content, max_words=120, overlap=20), start=1):
                vector = self.embedding_client.embed(chunk)
                point_id = f"{document.id}-{index}"
                payload = {
                    "document_id": document.id,
                    "title": document.title,
                    "category": document.category,
                    "version": document.version,
                    "source": document.source,
                    "chunk_index": index,
                    "chunk_text": chunk,
                }
                points.append(PointStruct(id=point_id, vector=vector, payload=payload))

        if points:
            self.client.upsert(collection_name=self.collection_name, points=points)

        return len(points)

    def search(self, query: str, limit: int = 3) -> list[dict]:
        self._ensure_available()

        query_vector = self.embedding_client.embed(query)
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            with_payload=True,
        )

        return [
            {
                "id": point.id,
                "score": point.score,
                "payload": point.payload or {},
            }
            for point in results
        ]

    def ping(self) -> dict[str, bool | str]:
        if not _QDRANT_AVAILABLE or self.client is None:
            return {
                "available": False,
                "detail": self.last_error or "Qdrant não está disponível. Verifique se o serviço está em execução em QDRANT_URL.",
            }

        try:
            self.client.get_collections()
            return {"available": True, "detail": "Qdrant conectado e respondendo."}
        except Exception as exc:
            return {"available": False, "detail": str(exc)}
