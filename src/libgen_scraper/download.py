from bs4 import BeautifulSoup
import requests
import re

# Ordered from most preferred to least preferred.
MIRROR_SOURCES = ["Cloudflare", "GET", "IPFS.io", "Infura"]


def find_links_in_mirror(url: str):
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a", string=MIRROR_SOURCES)
    return [link["href"] for link in links]


def find_link_in_scihub_mirror(url: str):
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    # CSS Selector: #buttons > button:nth-child(1)
    # URL is encoded in the button's JS code:
    # <button onclick="location.href='//moscow.sci-hub.ru/1/{ARTICLE PATH}.pdf?download=true'">↓ save</button>
    link = soup.select_one("#buttons > button:nth-child(1)")["onclick"]
    link = re.findall(r"location.href='(.*?)'", link)[0]
    return ["https:" + link]


def find_download_links(url: str):
    # Detect if the mirror points to "sci-hub.?".
    # If it does, we need to handle the mirror webpage differently.
    sci_hub = not not re.search(r"^https?:\/\/sci-hub\.", url)

    if sci_hub:
        return find_link_in_scihub_mirror(url)
    else:
        return find_links_in_mirror(url)
