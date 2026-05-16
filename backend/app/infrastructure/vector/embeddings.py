import hashlib
import math
import re
import unicodedata

DEFAULT_VECTOR_SIZE = 64

STOPWORDS = {
    "a",
    "ao",
    "aos",
    "as",
    "como",
    "da",
    "das",
    "de",
    "do",
    "dos",
    "e",
    "em",
    "eu",
    "me",
    "na",
    "nas",
    "no",
    "nos",
    "o",
    "os",
    "para",
    "por",
    "qual",
    "que",
    "um",
    "uma",
}


class HashEmbeddingGenerator:
    def __init__(self, vector_size: int = DEFAULT_VECTOR_SIZE) -> None:
        self.vector_size = vector_size

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.vector_size
        tokens = tokenize(text)
        if not tokens:
            return vector

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], byteorder="big") % self.vector_size
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0.0:
            return vector
        return [round(value / norm, 6) for value in vector]


def tokenize(text: str) -> set[str]:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    tokens = re.findall(r"[a-z0-9]+", ascii_text)
    return {token for token in tokens if token not in STOPWORDS and len(token) > 2}


def cosine_similarity(first: list[float], second: list[float]) -> float:
    if not first or not second or len(first) != len(second):
        return 0.0

    score = sum(left * right for left, right in zip(first, second, strict=True))
    return round(max(0.0, min(1.0, score)), 4)
