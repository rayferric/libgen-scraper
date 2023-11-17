import pandas as pd
import pytest
from unittest.mock import patch

from libgen_scraper import ArticlesColumns, ArticlesResults, search_articles


@pytest.fixture
def sample_articles_data():
    # Create a sample DataFrame for testing
    data = {
        ArticlesColumns.AUTHORS.value: ["Author1", "Author2", "Author3"],
        ArticlesColumns.ARTICLE.value: ["Article1", "Article2", "Article3"],
        ArticlesColumns.JOURNAL.value: ["Journal1", "Journal2", "Journal3"],
        ArticlesColumns.FILE.value: ["pdf/1.2 MB", "epub/800 kB", "mobi/2 GB"],
        ArticlesColumns.MIRRORS.value: ["[https://mirror1]", "[http://mirror2]", ""],
    }
    return pd.DataFrame(data)


def test_articles_results(sample_articles_data):
    results = ArticlesResults(sample_articles_data)

    assert len(results) == 3

    # Test individual attribute retrieval
    assert results.authors(0) == "Author1"
    assert results.article(1) == "Article2"
    assert results.journal(2) == "Journal3"
    assert results.size(0) == "pdf"
    assert results.edit_link(1) is None
    assert results.mirrors(2) == []

    # Test download links
    with patch(
        "libgen_scraper.articles.find_download_links"
    ) as mock_find_download_links:
        mock_find_download_links.return_value = ["link1", "link2"]
        assert results.download_links(0, limit_mirrors=2) == [
            "link1",
            "link2",
        ]
        mock_find_download_links.assert_called_with("https://mirror1")


def test_search_articles_with_mock(sample_articles_data):
    with patch("libgen_scraper.articles.multi_page_search") as mock_multi_page_search:
        mock_multi_page_search.return_value = sample_articles_data
        results = search_articles(query="Science", limit=5)
        mock_multi_page_search.assert_called_once()

    assert isinstance(results, ArticlesResults)
    assert len(results) == 3  # the length of the sample data
