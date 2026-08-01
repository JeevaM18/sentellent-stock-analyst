import sys
import os
import uuid
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.recommendation.candidate_builder import RecommendationCandidateBuilder


def test_candidate_builder():
    mock_db = MagicMock()
    mock_comp = MagicMock()
    mock_comp.id = uuid.uuid4()
    mock_comp.company_name = "Reliance Industries"
    mock_comp.ticker = "RELIANCE"
    mock_comp.sector = "Energy"
    mock_comp.fundamentals = None

    mock_db.query.return_value.options.return_value.limit.return_value.all.return_value = [mock_comp]

    mock_retriever = MagicMock()
    mock_retriever.retrieve.return_value.results = []

    candidates, memory = RecommendationCandidateBuilder.build_candidates(
        db=mock_db,
        user_id=None,
        retriever_service=mock_retriever,
    )

    assert len(candidates) == 1
    assert candidates[0].ticker == "RELIANCE"
    assert candidates[0].company.company_name == "Reliance Industries"
