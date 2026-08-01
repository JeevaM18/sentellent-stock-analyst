import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest  # pyrefly: ignore [missing-import]

from app.embeddings.constants import EMBEDDING_DIMENSIONS
from app.embeddings.types import EmbeddingResult
from app.embeddings.utils import (
    validate_dimension,
    validate_batch,
    vector_norm,
    normalize_vector,
    is_normalized,
    cosine_similarity,
)


def test_validate_dimension():
    valid_vec = [0.1] * EMBEDDING_DIMENSIONS
    validate_dimension(valid_vec)  # Should not raise exception

    invalid_vec = [0.1] * 500
    with pytest.raises(ValueError, match=f"Expected {EMBEDDING_DIMENSIONS} dimensions but got 500"):
        validate_dimension(invalid_vec)


def test_validate_batch():
    res1 = EmbeddingResult(vector=[0.1] * EMBEDDING_DIMENSIONS, model="text-embedding-004", dimensions=768)
    res2 = EmbeddingResult(vector=[0.2] * EMBEDDING_DIMENSIONS, model="text-embedding-004", dimensions=768)
    validate_batch([res1, res2])  # Should pass

    res_invalid = EmbeddingResult(vector=[0.1] * 100, model="text-embedding-004", dimensions=768)
    with pytest.raises(ValueError, match="Expected 768 dimensions but got 100"):
        validate_batch([res1, res_invalid])


def test_normalize_vector():
    vec = [3.0, 4.0] + [0.0] * (EMBEDDING_DIMENSIONS - 2)
    norm_vec = normalize_vector(vec)

    assert abs(vector_norm(norm_vec) - 1.0) < 1e-6
    assert abs(norm_vec[0] - 0.6) < 1e-6
    assert abs(norm_vec[1] - 0.8) < 1e-6


def test_is_normalized():
    unit_vec = [1.0 / (EMBEDDING_DIMENSIONS ** 0.5)] * EMBEDDING_DIMENSIONS
    assert is_normalized(unit_vec) is True

    non_unit_vec = [2.0] * EMBEDDING_DIMENSIONS
    assert is_normalized(non_unit_vec) is False


def test_cosine_similarity_symmetry():
    v1 = [1.0] * EMBEDDING_DIMENSIONS
    v2 = [2.0 if i % 2 == 0 else -1.0 for i in range(EMBEDDING_DIMENSIONS)]

    sim_1_2 = cosine_similarity(v1, v2)
    sim_2_1 = cosine_similarity(v2, v1)

    assert abs(sim_1_2 - sim_2_1) < 1e-9
    assert -1.0 <= sim_1_2 <= 1.0


def test_zero_vector():
    zero_vec = [0.0] * EMBEDDING_DIMENSIONS
    v1 = [1.0] * EMBEDDING_DIMENSIONS

    assert vector_norm(zero_vec) == 0.0
    assert normalize_vector(zero_vec) == zero_vec
    assert cosine_similarity(zero_vec, v1) == 0.0
