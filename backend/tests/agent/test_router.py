import sys
import os

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.agent.router import IntentRouter, IntentType


def test_classify_fundamentals():
    q = "What is Reliance PE Ratio?"
    assert IntentRouter.classify(q) == IntentType.FUNDAMENTALS
    assert IntentRouter.route(q) == "fundamentals"


def test_classify_watchlist():
    q = "Show my watchlist"
    assert IntentRouter.classify(q) == IntentType.WATCHLIST
    assert IntentRouter.route(q) == "watchlist"


def test_classify_retrieval():
    q = "Latest Infosys News"
    assert IntentRouter.classify(q) == IntentType.RETRIEVAL
    assert IntentRouter.route(q) == "retrieve"


def test_classify_combined():
    q = "Compare Reliance fundamentals and summarize today's news"
    assert IntentRouter.classify(q) == IntentType.COMBINED
