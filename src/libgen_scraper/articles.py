from enum import Enum
from typing import Callable, Pattern, Optional
import pandas as pd
import re

from .search import multi_page_search
from .download import find_download_links


class ArticlesColumns(Enum):
    AUTHORS = "Author(s)"
    ARTICLE = "Article"
    JOURNAL = "Journal"
    FILE = "File"
    MIRRORS = "Mirrors"


class ArticlesResults:
    """
    A wrapper around a pandas DataFrame containing the results of a search in Scientific Articles category.

    Attributes
    ----------
    data : pd.DataFrame
        a pandas DataFrame containing the results; Columns within the frame are declared in ArticlesColumns.
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
        return self.data.iloc[i][ArticlesColumns.AUTHORS.value] or None

    def article(self, i: int) -> Optional[str]:
        return self.data.iloc[i][ArticlesColumns.ARTICLE.value] or None

    def journal(self, i: int) -> Optional[str]:
        return self.data.iloc[i][ArticlesColumns.JOURNAL.value] or None

    def size(self, i: int) -> Optional[str]:
        file = self.data.iloc[i][ArticlesColumns.FILE.value]
        if file:
            return file.split("/")[0].strip().lower()

    def edit_link(self, i: int) -> Optional[str]:
        file = self.data.iloc[i][ArticlesColumns.FILE.value]
        if file:
            URL_REGEX = r"\[(.*?)\]"
            matches = re.findall(URL_REGEX, file)
            if matches:
                return matches[0]

    def mirrors(self, i: int) -> list[str]:
        mirrors = []

        row = self.data.iloc[i]
        mirrors_str = row[ArticlesColumns.MIRRORS.value]
        if mirrors_str:
            # Find all mirrors in the string.
            URL_REGEX = r"\[(.*?)\]"
            mirrors = re.findall(URL_REGEX, mirrors_str)

        return mirrors

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


def search_articles(
    query: str,
    filter: dict[ArticlesColumns, Pattern] = {},
    limit: int = 100,
    chunk_callback: Optional[Callable[[ArticlesResults], None]] = None,
    libgen_mirror: str = "http://libgen.is",
) -> ArticlesResults:
    """
    Search in Scientific Articles category.

    Parameters
    ----------
    query : str
        search query; Its minimum length is 3 characters.
    filter : dict[FictionColumns, Pattern], optional
        regex to search for in each column of the results; Filtered-out items do not count towards the limit.
    limit : int, optional
        maximum number of items to return; Set to enormous number to get all results.
    chunk_callback : Callable[[pd.DataFrame], None], optional
        function to be called on each new chunk of results; Useful for saving results to a file.
    libgen_mirror : str, optional
        the URL of the Libgen mirror to use without the trailing slash; Defaults to "http://libgen.is".

    Returns
    -------
    ArticlesResults
        a wrapper around a pandas DataFrame containing the results
    """

    def chunk_callback_wrapper(df: pd.DataFrame):
        if chunk_callback:
            chunk_callback(ArticlesResults(df))

    return ArticlesResults(
        multi_page_search(
            lambda i: libgen_mirror + f"/scimag/?q={query}&page={i}",
            columns=[column.value for column in ArticlesColumns],
            hyperlink_columns=[
                list(ArticlesColumns).index(column)
                for column in [
                    ArticlesColumns.FILE,
                    ArticlesColumns.MIRRORS,
                ]
            ],
            filter=filter,
            limit=limit,
            chunk_callback=chunk_callback_wrapper,
        )
    )
