# Libgen Scraper

A set of utilities for searching and retrieving information from the Library Genesis service. It includes functionality for searching, filtering, and accessing details about the available literature.

Enjoy open and automated access to knowledge!

## Table of Contents

- [Installation](#installation)
- [General Usage](#usage)
   - [Search](#search)
   - [Accessing Results](#accessing-results)
   - [Downloading](#downloading)
   - [Saving Results](#saving-results)
- [About](#about)

## Installation

To install the library, run the following command:
```bash
pip install libgen-scraper
```

## Usage

### Search

To perform a search, use the `search_` family of functions:

```python
import libgen_scraper as lg

non_fiction = lg.search_non_fiction("Geology of Mars")
```

Search results can also be filtered using the `filter` parameter, which accepts a dictionary of `...Columns` and corresponding regex patterns.
Here's some more examples including more advanced parameters:

```python
import libgen_scraper as lg

# Find at most 2 non-fiction books published by Helion.
# Books shall be in Polish and about Java.
# Print the title of the first book in each chunk of results as they are received.
non_fiction = lg.search_non_fiction(
    "Helion",
    search_in_fields=lg.NonFictionSearchField.PUBLISHER,
    filter={
        lg.NonFictionColumns.LANGUAGE: r'Polish',
        lg.NonFictionColumns.TITLE: r'[Jj]ava',
    },
    limit=2,
    chunk_callback=lambda results: print(results.title(0)),
    libgen_mirror="http://libgen.rs",
)
# non_fiction is at this point a NonFictionResults object that contains all the results of the search.
# non_fiction.data is a Pandas DataFrame containing the results in a tabular, unstructured format.

# Find at most 10 fiction books with "Harry Potter" in the title.
# Books shall be in English, in PDF format. Wildcards are not allowed in the query.
fiction = lg.search_fiction(
    "Harry Potter",
    search_criteria=lg.FictionSearchCriteria.TITLE,
    wildcards=False,
    language='English',
    format=lg.FictionSearchFormat.PDF,
    # Filters are also supported.
    limit=10,
    # Chunk callback is also supported.
)

# Find at most 10 scientific articles about social media.
articles = lg.search_articles(
    "Social Media",
    # Filters are also supported.
    limit=10,
    # Chunk callback is also supported.
)
```

### Accessing Results

The search results are encapsulated in `...Results` objects that provide methods to access information about each book.
Each kind of search has its own `...Results` class with custom methods matching the available information.
For example, some of the functionality of `NonFictionResults` is:

```python
# Accessing book details:
print(non_fiction.title(0))  # Print the title of the first book.
print(non_fiction.authors(0))
print(non_fiction.mirrors(0))
```

### Downloading

Every `...Results` object has a `download_links` method that can fetch download links for a specific book.
Multiple mirrors can be used to download the book, and the mirrors are scraped in order as returned by `.mirrors(i)`.
By default only the first mirror is used, but you can specify the number of mirrors to use with the `limit_mirrors` parameter.
This will however increase the time it takes to fetch the download links.

```python
from urllib.request import urlretrieve

# Download the first book from the first 2 mirrors.
# Mirrors at the beginning of the list are preferred.
download_links = non_fiction.download_links(0, limit_mirrors=2)
urlretrieve(download_links[0], non_fiction.id(0) + ".pdf")
```

### Saving Results

Each `...Results` object encapsulates a Pandas DataFrame with the results in a tabular, unstructured format.
You can save this DataFrame to a CSV file using Pandas.
Saved data can be loaded back by manually constructing a `...Results` object with DataFrame as the argument.

```python
import pandas as pd

# Save NonFictionResults to a CSV file
non_fiction.data.to_csv("results.csv", index=False)

# Load the results from a CSV file
data = pd.read_csv("results.csv")
non_fiction = NonFictionResults(data)
```

## About

This library is not affiliated with the Library Genesis service in any way.
It is a community project, and is not officially supported by Library Genesis nor does it promote the use of the service.

The library is licensed under the MIT license.
