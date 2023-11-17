import pandas as pd
import pytest
from unittest.mock import patch

from libgen_scraper import (
    FictionColumns,
    FictionResults,
    search_fiction,
)


@pytest.fixture
def sample_fiction_data():
    # Create a sample DataFrame for testing
    data = {
        FictionColumns.AUTHORS.value: ["Author1", "Author2", "Author3"],
        FictionColumns.SERIES.value: ["Series1", "Series2", ""],
        FictionColumns.TITLE.value: ["Book1", "Book2", "Book3"],
        FictionColumns.LANGUAGE.value: ["English", "German", "French"],
        FictionColumns.FILE.value: ["pdf/1.2 MB", "epub/800 kB", "mobi/2 GB"],
        FictionColumns.MIRRORS.value: ["[https://mirror1]", "[http://mirror2]", ""],
        FictionColumns.EDIT.value: [
            "[http://edit1]",
            "[https://edit2]",
            "(2) EditLink",
        ],
    }
    return pd.DataFrame(data)


def test_fiction_results(sample_fiction_data):
    results = FictionResults(sample_fiction_data)

    assert len(results) == 3

    # Test individual attribute retrieval
    assert results.authors(0) == "Author1"
    assert results.series(1) == "Series2"
    assert results.title(2) == "Book3"
    assert results.language(0) == "English"
    assert results.extension(1) == "epub"
    # assert results.size(0) == 2 * 1000 * 1000  # 2 MB to bytes
    assert results.mirrors(2) == []
    assert results.edit_link(1) == "https://edit2"

    # Test download links
    with patch(
        "libgen_scraper.fiction.find_download_links"
    ) as mock_find_download_links:
        mock_find_download_links.return_value = ["link1", "link2"]
        assert results.download_links(0, limit_mirrors=100) == [
            "link1",
            "link2",
        ]
        mock_find_download_links.assert_called_with("https://mirror1")


def test_search_fiction_with_mock(sample_fiction_data):
    with patch("libgen_scraper.fiction.multi_page_search") as mock_multi_page_search:
        mock_multi_page_search.return_value = sample_fiction_data
        results = search_fiction(query="Fantasy", limit=5)
        mock_multi_page_search.assert_called_once()

    assert isinstance(results, FictionResults)
    assert len(results) == 3  # the length of the sample data
