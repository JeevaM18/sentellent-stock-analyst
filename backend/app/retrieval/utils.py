from app.retrieval.constants import MAX_TOP_K


def validate_query(query: str) -> str:
    """Validate and clean user search query string."""
    if not query or not query.strip():
        raise ValueError("Search query cannot be empty")
    return query.strip()


def clamp_top_k(top_k: int) -> int:
    """Clamp top_k between 1 and MAX_TOP_K."""
    if top_k < 1:
        return 1
    if top_k > MAX_TOP_K:
        return MAX_TOP_K
    return top_k


def cosine_distance_to_similarity(distance: float) -> float:
    """Convert pgvector cosine distance (0..2) to similarity score (0..1)."""
    similarity = 1.0 - distance
    return round(max(0.0, min(1.0, similarity)), 4)
