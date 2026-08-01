import sys
import os
from unittest.mock import patch

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.ingestion.news import GoogleNewsRSSProvider


@patch("app.ingestion.news.provider.requests.get")
def test_provider_success(mock_get):
    class DummyResponse:
        status_code = 200
        content = b"""
        <rss version="2.0">
            <channel>
                <title>Google News</title>
                <item>
                    <title>Reliance Industries Announces Q1 Results</title>
                    <link>https://news.google.com/rss/articles/12345?utm_source=rss</link>
                    <description>&lt;b&gt;Reliance&lt;/b&gt; reported strong quarterly profit growth.</description>
                    <pubDate>Sat, 01 Aug 2026 05:00:00 GMT</pubDate>
                    <source url="https://moneycontrol.com">Moneycontrol</source>
                </item>
            </channel>
        </rss>
        """

        def raise_for_status(self):
            return

    mock_get.return_value = DummyResponse()

    result = GoogleNewsRSSProvider().fetch("Reliance Industries", "RELIANCE")

    assert result["success"] is True
    assert result["ticker"] == "RELIANCE"
    assert result["company"] == "Reliance Industries"
    assert len(result["articles"]) == 1

    article = result["articles"][0]
    assert article["title"] == "Reliance Industries Announces Q1 Results"
    assert article["article_url"] == "https://news.google.com/rss/articles/12345"
    assert "content_hash" in article
    assert article["language"] == "en-IN"
    assert "reported strong quarterly profit growth" in article["summary"]
    assert article["published_at"] is not None


@patch("app.ingestion.news.provider.requests.get")
def test_provider_failure(mock_get):
    mock_get.side_effect = Exception("Network Connection Error")

    result = GoogleNewsRSSProvider().fetch("Reliance Industries", "RELIANCE")

    assert result["success"] is False
    assert result["ticker"] == "RELIANCE"
    assert result["articles"] == []
    assert result["error"] == "Network Connection Error"


@patch("app.ingestion.news.provider.requests.get")
def test_empty_feed(mock_get):
    class DummyEmptyResponse:
        status_code = 200
        content = b"""
        <rss version="2.0">
            <channel>
                <title>Google News - Empty</title>
            </channel>
        </rss>
        """

        def raise_for_status(self):
            return

    mock_get.return_value = DummyEmptyResponse()

    result = GoogleNewsRSSProvider().fetch("Empty Company", "EMPTY")

    assert result["success"] is True
    assert result["ticker"] == "EMPTY"
    assert result["articles"] == []
