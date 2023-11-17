from enum import Enum
import pandas as pd
import re
import humanfriendly as hf
from typing import Callable, Pattern, Optional

from .search import multi_page_search
from .download import find_download_links


class FictionColumns(Enum):
    AUTHORS = "Author(s)"
    SERIES = "Series"
    TITLE = "Title"
    LANGUAGE = "Language"
    FILE = "File"
    MIRRORS = "Mirrors"
    EDIT = "Edit"


class FictionSearchCriteria(Enum):
    """
    Search criteria for fiction books.
    """

    ANY = ""
    TITLE = "title"
    AUTHORS = "authors"
    SERIES = "series"


class FictionSearchFormat(Enum):
    """
    File format for fiction books.
    """

    ANY = ""
    EPUB = "epub"
    MOBI = "mobi"
    AZW = "azw"
    AZW3 = "azw3"
    FB2 = "fb2"
    PDF = "pdf"
    RTF = "rtf"
    TXT = "txt"


class FictionResults:
    """
    A wrapper around a pandas DataFrame containing the results of a search in fiction category.

    Attributes
    ----------
    data : pd.DataFrame
        a pandas DataFrame containing the results; Columns within the frame are declared in FictionColumns.
    """

    def __init__(self, df: pd.DataFrame):
        self.data = df

    def __repr__(self):
        return repr(self.data)

    def __str__(self):
        return str(self.data)

    def __len__(self):
        return len(self.data)

    def authors(self, i: int) -> Optional[str]:
        return self.data.iloc[i][FictionColumns.AUTHORS.value] or None

    def series(self, i: int) -> Optional[str]:
        return self.data.iloc[i][FictionColumns.SERIES.value] or None

    def title(self, i: int) -> Optional[str]:
        return self.data.iloc[i][FictionColumns.TITLE.value] or None

    def language(self, i: int) -> Optional[str]:
        return self.data.iloc[i][FictionColumns.LANGUAGE.value] or None

    def extension(self, i: int) -> Optional[str]:
        file = self.data.iloc[i][FictionColumns.FILE.value]
        if file:
            return file.split("/")[0].strip().lower()

    def size(self, i: int) -> Optional[int]:
        file = self.data.iloc[i][FictionColumns.FILE.value]
        if file:
            return hf.parse_size(file.split("/")[1].strip())

    def mirrors(self, i: int) -> list[str]:
        mirrors = []

        row = self.data.iloc[i]
        mirrors_str = row[FictionColumns.MIRRORS.value]
        if mirrors_str:
            # Find all mirrors in the string.
            URL_REGEX = r"\[(.*?)\]"
            mirrors = re.findall(URL_REGEX, mirrors_str)

        return mirrors

    def edit_link(self, i: int) -> Optional[str]:
        edit = self.data.iloc[i][FictionColumns.EDIT.value]
        if edit:
            return edit[1:-1]

    def download_links(self, i: int, limit_mirrors: int = 1) -> list[str]:
        """
        Fetches download links from a limited number of mirrors.

        Parameters
        ----------
        i : int
            index of the result
        limit_mirrors : int, optional
            maximum number of mirrors to fetch links from; Set to a large value to get links from all mirrors.

        Returns
        -------
        list[str]
            a list of download links
        """

        urls = []
        mirrors = self.mirrors(i)
        for mirror in mirrors[:limit_mirrors]:
            urls.extend(find_download_links(mirror))
        return urls


def search_fiction(
    query: str,
    search_criteria: FictionSearchCriteria = FictionSearchCriteria.ANY,
    wildcards: bool = False,
    language: str = "",
    format: FictionSearchFormat = FictionSearchFormat.ANY,
    filter: dict[FictionColumns, Pattern] = {},
    limit: int = 100,
    chunk_callback: Optional[Callable[[FictionResults], None]] = None,
    libgen_mirror: str = "http://libgen.is",
) -> FictionResults:
    """
    Search in Fiction category.

    Parameters
    ----------
    query : str
        search query; Its minimum length is 3 characters.
    search_criteria : FictionSearchCriteria, optional
        fields in which to search for the query values or just be a substring of them
    wildcards : bool, optional
        Each word in a query will be searched as a wildcard. Use it to search for more word forms.
    language : str, optional
        language of the book; Use the exact language names from the dropdown menu on the website.
    format : FictionSearchFormat, optional
        file format of the book, by default any
    filter : dict[FictionColumns, Pattern], optional
        regex to search for in each column of the results; Filtered-out items do not count towards the limit.
    limit : int, optional
        maximum number of items to return; Set to enormous number to get all results.
    chunk_callback : Callable[[FictionResults], None], optional
        function to be called on each new chunk of results; Useful for saving results to a file.
    libgen_mirror : str, optional
        the URL of the Libgen mirror to use without the trailing slash; Defaults to "http://libgen.is".

    Returns
    -------
    FictionResults
        a wrapper around a pandas DataFrame containing the results
    """

    def chunk_callback_wrapper(df: pd.DataFrame):
        if chunk_callback:
            chunk_callback(FictionResults(df))

    return FictionResults(
        multi_page_search(
            lambda i: libgen_mirror
            + f"/fiction/?q={query}&criteria={search_criteria.value}"
            + f"&wildcard={1 if wildcards else ''}&language={language}"
            + f"&format={format.value}&page={i}",
            columns=[column.value for column in FictionColumns],
            hyperlink_columns=[
                list(FictionColumns).index(column)
                for column in [
                    FictionColumns.MIRRORS,
                    FictionColumns.EDIT,
                ]
            ],
            filter=filter,
            limit=limit,
            chunk_callback=chunk_callback_wrapper,
        )
    )
