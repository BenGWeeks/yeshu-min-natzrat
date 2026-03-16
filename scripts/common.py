"""Shared utilities for fetch scripts."""

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "identity",
}


def fetch_html(url: str) -> BeautifulSoup:
    """Fetch a URL with browser-like headers and return parsed HTML."""
    print(f"  Fetching {url}...")
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def get_gnosis_content(soup: BeautifulSoup) -> BeautifulSoup:
    """Extract the content column from gnosis.org table layout.

    gnosis.org pages use a two-column table: navigation (first <td>)
    and content (second <td>). This returns just the content <td>.
    """
    tds = soup.find_all("td")
    if len(tds) >= 2:
        # The second <td> contains the actual text content
        return tds[1]
    # Fallback to body
    return soup.find("body") or soup
