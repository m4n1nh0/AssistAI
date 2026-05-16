import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import NAMESPACE_URL, uuid5

from app.domain.models import DocumentChunk
from app.infrastructure.vector.embeddings import DEFAULT_VECTOR_SIZE, HashEmbeddingGenerator


@dataclass(frozen=True, slots=True)
class QdrantConfig:
    url: str
    collection: str
    vector_size: int = DEFAULT_VECTOR_SIZE
    timeout_seconds: float = 2.0


@dataclass(frozen=True, slots=True)
class VectorSearchResult:
    chunk_id: str
    score: float
    payload: dict[str, str]


class QdrantUnavailable(RuntimeError):
    pass


class QdrantVectorStore:
    def __init__(
        self,
        config: QdrantConfig,
        embedding_generator: HashEmbeddingGenerator | None = None,
    ) -> None:
        self.config = config
        self.embedding_generator = embedding_generator or HashEmbeddingGenerator(config.vector_size)
        self._indexed = False

    @property
    def indexed(self) -> bool:
        return self._indexed

    def upsert_chunks(self, chunks: list[DocumentChunk]) -> int:
        if not chunks:
            return 0

        self._ensure_collection()
        points = []
        for chunk in chunks:
            vector = chunk.embedding or self.embedding_generator.embed(chunk.content)
            points.append(
                {
                    "id": str(uuid5(NAMESPACE_URL, chunk.id)),
                    "vector": vector,
                    "payload": {
                        **chunk.metadata,
                        "chunk_id": chunk.id,
                        "content": chunk.content,
                    },
                }
            )

        self._request(
            "PUT",
            f"/collections/{self.config.collection}/points?wait=true",
            {"points": points},
        )
        self._indexed = True
        return len(points)

    def search(self, query: str, top_k: int = 3) -> list[VectorSearchResult]:
        if not self._indexed:
            return []

        response = self._request(
            "POST",
            f"/collections/{self.config.collection}/points/search",
            {
                "vector": self.embedding_generator.embed(query),
                "limit": top_k,
                "with_payload": True,
            },
        )
        results = response.get("result", [])
        return [
            VectorSearchResult(
                chunk_id=str(item.get("payload", {}).get("chunk_id", "")),
                score=round(max(0.0, min(1.0, float(item.get("score", 0.0)))), 4),
                payload=item.get("payload", {}),
            )
            for item in results
        ]

    def _ensure_collection(self) -> None:
        try:
            self._request("GET", f"/collections/{self.config.collection}")
            return
        except QdrantUnavailable as exc:
            if "404" not in str(exc):
                raise

        self._request(
            "PUT",
            f"/collections/{self.config.collection}",
            {
                "vectors": {
                    "size": self.config.vector_size,
                    "distance": "Cosine",
                }
            },
        )

    def _request(
        self,
        method: str,
        path: str,
        body: dict | None = None,
    ) -> dict:
        data = json.dumps(body).encode("utf-8") if body is not None else None
        request = Request(
            f"{self.config.url.rstrip('/')}{path}",
            data=data,
            method=method,
            headers={"Content-Type": "application/json"},
        )

        try:
            with urlopen(request, timeout=self.config.timeout_seconds) as response:
                response_body = response.read().decode("utf-8")
        except HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="ignore")
            raise QdrantUnavailable(f"Qdrant returned {exc.code}: {error_body}") from exc
        except URLError as exc:
            raise QdrantUnavailable(f"Qdrant unavailable: {exc.reason}") from exc

        return json.loads(response_body) if response_body else {}
