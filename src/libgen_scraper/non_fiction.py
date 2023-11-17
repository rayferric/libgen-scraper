from enum import Enum
from typing import Pattern, Callable, Optional
import pandas as pd
import re
import humanfriendly as hf

from .search import multi_page_search
from .download import find_download_links


class NonFictionColumns(Enum):
    ID = "ID"
    AUTHORS = "Author(s)"
    TITLE = "Title"
    PUBLISHER = "Publisher"
    YEAR = "Year"
    PAGES = "Pages"
    LANGUAGE = "Language"
    SIZE = "Size"
    EXTENSION = "Extension"
    MIRROR_1 = "Mirror 1"
    MIRROR_2 = "Mirror 2"
    EDIT = "Edit"


class NonFictionSearchField(Enum):
    """
    Search fields for non-fiction books.

    Default scheme includes: Title,Author(s),Series,Periodical,Publisher,Year,VolumeInfo

    Language should be specified as a capitalized english name of the language, e.g. "English", "Russian", "German", etc.
    """

    DEFAULT = "def"
    TITLE = "title"
    AUTHORS = "author"
    SERIES = "series"
    PUBLISHER = "publisher"
    YEAR = "year"
    ISBN = "identifier"
    LANGUAGE = "language"
    MD5 = "md5"
    TAGS = "tags"


class NonFictionResults:
    """
    A wrapper around a pandas DataFrame containing the results of a search in non-fiction category.

    Attributes
    ----------
    data : pd.DataFrame
        a pandas DataFrame containing the results; Columns within the frame are declared in NonFictionColumns.
    """

    def __init__(self, df: pd.DataFrame):
        self.data = df

    def __repr__(self):
        return repr(self.data)

    def __str__(self):
        return str(self.data)

    def __len__(self):
        return len(self.data)

    def id(self, i: int) -> Optional[int]:
        return self.data.iloc[i][NonFictionColumns.ID.value] or None

    def authors(self, i: int) -> Optional[str]:
        return self.data.iloc[i][NonFictionColumns.AUTHORS.value] or None

    def title(self, i: int) -> Optional[str]:
        return self.data.iloc[i][NonFictionColumns.TITLE.value] or None

    def publisher(self, i: int) -> Optional[str]:
        return self.data.iloc[i][NonFictionColumns.PUBLISHER.value] or None

    def year(self, i: int) -> Optional[int]:
        year = self.data.iloc[i][NonFictionColumns.YEAR.value]

        # Find the first number and return it as an integer.
        year = re.search(r"\d+", year)
        if year:
            return int(year.group(0))

    def pages(self, i: int) -> Optional[int]:
        pages = self.data[NonFictionColumns.PAGES.value][i]

        # If pages string contains a number in [] brackets, return that number instead of the first one found.
        brackets = re.search(r"\[(\d+)\]", pages)
        if brackets:
            return int(brackets.group(1))
        else:
            # Find the first number and return it as an integer.
            pages = re.search(r"\d+", pages)
            if pages:
                return int(pages.group(0))

    def language(self, i: int) -> Optional[str]:
        return self.data.iloc[i][NonFictionColumns.LANGUAGE.value] or None

    # size is in bytes
    def size(self, i: int) -> Optional[int]:
        size = self.data.iloc[i][NonFictionColumns.SIZE.value]

        # Parse human-friendly size strings.
        if size:
            return hf.parse_size(size)

    # extension without the leading period
    def extension(self, i: int) -> Optional[str]:
        return self.data.iloc[i][NonFictionColumns.EXTENSION.value] or None

    def mirrors(self, i: int) -> list[str]:
        mirrors = []
        row = self.data.iloc[i]
        mirror1 = row[NonFictionColumns.MIRROR_1.value]
        mirror2 = row[NonFictionColumns.MIRROR_2.value]
        if mirror1:
            mirrors.append(mirror1[1:-1])
        if mirror2:
            mirrors.append(mirror2[1:-1])
        return mirrors

    def edit_link(self, i: int) -> Optional[str]:
        edit = self.data.iloc[i][NonFictionColumns.EDIT.value]
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


def search_non_fiction(
    query: str,
    search_in_fields: NonFictionSearchField = NonFictionSearchField.DEFAULT,
    filter: dict[NonFictionColumns, Pattern] = {},
    limit: int = 100,
    chunk_callback: Optional[Callable[[NonFictionResults], None]] = None,
    libgen_mirror: str = "http://libgen.is",
) -> NonFictionResults:
    """
    Search in Non-Fiction/Sci-Tech category.

    Parameters
    ----------
    query : str
        search query; Its minimum length is 3 characters.
    search_in_fields : NonFictionSearchField, optional
        fields in which to search for the query values or just be a substring of them
    filter : dict[NonFictionColumns, Pattern], optional
        regex to search for in each column of the results; Filtered-out items do not count towards the limit.
    limit : int, optional
        maximum number of items to return; Set to enormous number to get all results.
    chunk_callback : Callable[[NonFictionResults], None], optional
        function to be called on each new chunk of results; Useful for saving results to a file.
    libgen_mirror : str, optional
        the URL of the Libgen mirror to use without the trailing slash; Defaults to "http://libgen.is".

    Returns
    -------
    NonFictionResults
        a wrapper around a pandas DataFrame containing the results
    """

    def chunk_callback_wrapper(df: pd.DataFrame):
        if chunk_callback:
            chunk_callback(NonFictionResults(df))

    PAGE_SIZE = 100
    return NonFictionResults(
        multi_page_search(
            lambda i: libgen_mirror
            + f"/search.php?req={query}&column={search_in_fields.value}&res={PAGE_SIZE}&page={i}",
            columns=[column.value for column in NonFictionColumns],
            hyperlink_columns=[
                list(NonFictionColumns).index(column)
                for column in [
                    NonFictionColumns.MIRROR_1,
                    NonFictionColumns.MIRROR_2,
                    NonFictionColumns.EDIT,
                ]
            ],
            filter=filter,
            limit=limit,
            chunk_callback=chunk_callback_wrapper,
        )
    )
