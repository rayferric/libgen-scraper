import pandas as pd
import pytest
from unittest.mock import patch

from libgen_scraper import (
    NonFictionColumns,
    NonFictionResults,
    search_non_fiction,
)


@pytest.fixture
def sample_data():
    # Create a sample DataFrame for testing
    data = {
        NonFictionColumns.ID.value: [1, 2, 3],
        NonFictionColumns.AUTHORS.value: ["Author1", "Author2", "Author3"],
        NonFictionColumns.TITLE.value: ["Book1", "Book2", "Book3"],
        NonFictionColumns.PUBLISHER.value: ["Publisher1", "Publisher2", "Publisher3"],
        NonFictionColumns.YEAR.value: ["2020", "2021", "2022"],
        NonFictionColumns.PAGES.value: ["100", "[200]", "150"],
        NonFictionColumns.LANGUAGE.value: ["English", "German", "French"],
        NonFictionColumns.SIZE.value: ["1.2 MB", "800 kB", "2 GB"],
        NonFictionColumns.EXTENSION.value: ["pdf", "epub", "mobi"],
        NonFictionColumns.MIRROR_1.value: ["[https://mirror1]", "[http://mirror2]", ""],
        NonFictionColumns.MIRROR_2.value: ["[http://mirror3]", "", ""],
        NonFictionColumns.EDIT.value: [
            "[http://edit1]",
            "[https://edit2]",
            "(2) EditLink",
        ],
    }
    return pd.DataFrame(data)


def test_non_fiction_results(sample_data):
    results = NonFictionResults(sample_data)

    assert len(results) == 3

    # Test individual attribute retrieval
    assert results.id(0) == 1
    assert results.authors(1) == "Author2"
    assert results.title(2) == "Book3"
    assert results.publisher(0) == "Publisher1"
    assert results.year(1) == 2021
    assert results.pages(2) == 150
    assert results.language(0) == "English"
    assert results.size(1) == 800 * 1000  # 800 kB to bytes
    assert results.extension(2) == "mobi"
    assert results.mirrors(0) == ["https://mirror1", "http://mirror3"]
    assert results.edit_link(1) == "https://edit2"

    # Test download links
    with patch(
        "libgen_scraper.non_fiction.find_download_links"
    ) as mock_find_download_links:
        mock_find_download_links.return_value = ["link1", "link2"]
        assert results.download_links(0, limit_mirrors=2) == [
            "link1",
            "link2",
            "link1",
            "link2",
        ]
        mock_find_download_links.assert_called_with("http://mirror3")


def test_search_non_fiction_with_mock(sample_data):
    with patch(
        "libgen_scraper.non_fiction.multi_page_search"
    ) as mock_multi_page_search:
        mock_multi_page_search.return_value = sample_data
        results = search_non_fiction(query="Python", limit=5)
        mock_multi_page_search.assert_called_once()

    assert isinstance(results, NonFictionResults)
    assert len(results) == 3  # the length of the sample data
