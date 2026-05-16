from __future__ import annotations

import logging
from dataclasses import dataclass

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from qdrant_client.http.exceptions import ResponseHandlingException, UnexpectedResponse

from app.domain.models import DocumentChunk
from app.infrastructure.embeddings.service import EmbeddingService

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class QdrantConfig:
    url: str
    collection: str


@dataclass(frozen=True, slots=True)
class QdrantSearchResult:
    chunk: DocumentChunk
    score: float


_QDRANT_ERRORS = (UnexpectedResponse, ResponseHandlingException, ConnectionError, TimeoutError)


class QdrantVectorStore:
    def __init__(
        self,
        config: QdrantConfig,
        embedding_service: EmbeddingService,
    ) -> None:
        self.config = config
        self.embedding_service = embedding_service
        self.client = QdrantClient(url=config.url, timeout=30)
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        try:
            collections = self.client.get_collections().collections
            exists = any(
                c.name == self.config.collection for c in collections
            )
            if not exists:
                self.client.create_collection(
                    collection_name=self.config.collection,
                    vectors_config=qmodels.VectorParams(
                        size=self._probe_vector_size(),
                        distance=qmodels.Distance.COSINE,
                    ),
                )
                logger.info(
                    "Colecao Qdrant criada: %s",
                    self.config.collection,
                )
        except _QDRANT_ERRORS as exc:
            logger.warning(
                "Nao foi possivel verificar/criar colecao Qdrant: %s", exc
            )

    def _probe_vector_size(self) -> int:
        sample = self.embedding_service.embed("probe")
        return len(sample)

    def upsert_chunks(self, chunks: list[DocumentChunk]) -> int:
        if not chunks:
            return 0

        texts = [chunk.content for chunk in chunks]
        vectors = self.embedding_service.embed_batch(texts)

        points: list[qmodels.PointStruct] = []
        for chunk, vector in zip(chunks, vectors, strict=False):
            points.append(
                qmodels.PointStruct(
                    id=hash(chunk.id) % (2**63),
                    vector=vector,
                    payload={
                        "chunk_id": chunk.id,
                        "document_id": chunk.document_id,
                        "content": chunk.content,
                        **chunk.metadata,
                    },
                )
            )

        try:
            self.client.upsert(
                collection_name=self.config.collection,
                points=points,
                wait=True,
            )
            logger.info("Indexados %d chunks no Qdrant", len(chunks))
            return len(chunks)
        except _QDRANT_ERRORS as exc:
            logger.warning("Erro ao indexar no Qdrant: %s", exc)
            return 0

    def search(
        self, query: str, top_k: int = 5
    ) -> list[QdrantSearchResult]:
        query_vector = self.embedding_service.embed(query)

        try:
            results = self.client.search(
                collection_name=self.config.collection,
                query_vector=query_vector,
                limit=top_k,
                score_threshold=0.0,
            )
        except _QDRANT_ERRORS as exc:
            logger.warning("Erro ao buscar no Qdrant: %s", exc)
            return []

        output: list[QdrantSearchResult] = []
        for result in results:
            payload = result.payload or {}
            chunk = DocumentChunk(
                id=payload.get("chunk_id", ""),
                document_id=payload.get("document_id", ""),
                content=payload.get("content", ""),
                metadata={
                    k: str(v)
                    for k, v in payload.items()
                    if k
                    not in (
                        "chunk_id",
                        "document_id",
                        "content",
                    )
                },
            )
            output.append(
                QdrantSearchResult(chunk=chunk, score=round(result.score, 4))
            )

        return output

    def delete_document_chunks(self, document_id: str) -> int:
        try:
            result = self.client.delete(
                collection_name=self.config.collection,
                points_selector=qmodels.FilterSelector(
                    filter=qmodels.Filter(
                        must=[
                            qmodels.FieldCondition(
                                key="document_id",
                                match=qmodels.MatchValue(value=document_id),
                            )
                        ]
                    )
                ),
            )
            logger.info(
                "Chunks deletados do Qdrant para doc %s", document_id
            )
            return result.status  # type: ignore[return-value]
        except _QDRANT_ERRORS as exc:
            logger.warning("Erro ao deletar chunks do Qdrant: %s", exc)
            return 0

    def collection_size(self) -> int:
        try:
            info = self.client.get_collection(self.config.collection)
            return info.points_count or 0
        except _QDRANT_ERRORS:
            return 0
