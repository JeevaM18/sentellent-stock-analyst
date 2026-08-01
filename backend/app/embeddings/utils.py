import math

from app.embeddings.constants import EMBEDDING_DIMENSIONS
from app.embeddings.types import EmbeddingResult


def validate_dimension(vector: list[float]) -> None:
    """Validate that vector matches the expected embedding dimensions."""
    if len(vector) != EMBEDDING_DIMENSIONS:
        raise ValueError(
            f"Expected {EMBEDDING_DIMENSIONS} dimensions but got {len(vector)}"
        )


def validate_batch(results: list[EmbeddingResult]) -> None:
    """Validate dimension across a batch of EmbeddingResult items."""
    for res in results:
        validate_dimension(res.vector)


def vector_norm(vector: list[float]) -> float:
    """Compute the Euclidean L2 norm of a vector."""
    return math.sqrt(sum(x * x for x in vector))


def normalize_vector(vector: list[float]) -> list[float]:
    """Return L2 normalized vector."""
    norm = vector_norm(vector)
    if norm == 0:
        return vector
    return [x / norm for x in vector]


def is_normalized(vector: list[float]) -> bool:
    """Check if vector is L2 normalized to unit length."""
    return abs(vector_norm(vector) - 1.0) < 1e-6


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two float vectors."""
    validate_dimension(a)
    validate_dimension(b)

    norm_a = vector_norm(a)
    norm_b = vector_norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    dot = sum(x * y for x, y in zip(a, b))
    return dot / (norm_a * norm_b)
