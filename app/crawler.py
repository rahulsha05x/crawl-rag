import time
import requests
import tldextract
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree as ET
from bs4 import BeautifulSoup
from typing import Iterable, Set, List, Tuple
import logging
from .config import USER_AGENT, CRAWL_MAX_PAGES, CRAWL_DELAY_SECONDS
from .chunker import clean_html, split_html_into_chunks
from .vectorstore import add_documents_to_chroma


logging.basicConfig(level=logging.INFO)

def _fetch(url: str) -> tuple[str | None, str | None]:
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
        r.raise_for_status()
        ctype = r.headers.get("Content-Type", "")
        if "text/html" not in ctype:
            return None, ctype
        return r.text, ctype
    except Exception:
        return None, None

def _discover_sitemaps(root_url: str) -> List[str]:
    parsed = urlparse(root_url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    robots = urljoin(base, "/robots.txt")
    sitemaps = []

    try:
        r = requests.get(robots, headers={"User-Agent": USER_AGENT}, timeout=10)
        if r.status_code == 200:
            for line in r.text.splitlines():
                if line.lower().startswith("sitemap:"):
                    sitemaps.append(line.split(":", 1)[1].strip())
    except Exception:
        pass

    if not sitemaps:
        sitemaps.append(urljoin(base, "/sitemap.xml"))
    return sitemaps

def _parse_sitemap_urls(sitemap_url: str) -> List[str]:
    try:
        r = requests.get(sitemap_url, headers={"User-Agent": USER_AGENT}, timeout=15)
        if r.status_code != 200:
            return []
        tree = ET.fromstring(r.content)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        # handle both sitemap index and urlset
        urls = [n.text.strip() for n in tree.findall(".//sm:loc", ns) if n.text]
        return urls
    except Exception:
        return []

def _same_domain(url: str, domain: str) -> bool:
    parsed = urlparse(url)
    return parsed.netloc.endswith(domain)

def _extract_links(html: str, base_url: str, domain: str) -> Set[str]:
    soup = BeautifulSoup(html, "html.parser")
    out = set()
    for a in soup.find_all("a", href=True):
        href = urljoin(base_url, a["href"])
        href = href.split("#")[0]
        p = urlparse(href)
        if p.scheme in ("http", "https") and _same_domain(href, domain):
            out.add(href)
    return out

def crawl_and_index(root_url: str, max_pages: int | None = None) -> dict:
    """
    Crawl a site (sitemap-first, fallback to link crawling) and index to Chroma.
    Returns summary dict: pages_processed, chunks_indexed, skipped_non_html
    """
    max_pages = max_pages or CRAWL_MAX_PAGES
    ext = tldextract.extract(root_url)
    domain = f"{ext.domain}.{ext.suffix}"

    visited: Set[str] = set()
    to_visit: Set[str] = set()

    # Try sitemap(s)
    sitemap_urls = _discover_sitemaps(root_url)
    candidate_urls: Set[str] = set()
    for sm in sitemap_urls:
        candidate_urls.update(_parse_sitemap_urls(sm))

    # If sitemap failed, start from root
    if not candidate_urls:
        to_visit.add(root_url)
    else:
        to_visit.update(u for u in candidate_urls if _same_domain(u, domain))

    pages_processed = 0
    chunks_indexed = 0
    skipped_non_html = 0

    while to_visit and pages_processed < max_pages:
        url = to_visit.pop()
        if url in visited:
            continue
        visited.add(url)

        html, ctype = _fetch(url)
        if html is None:
            if ctype is not None and "text/html" not in ctype:
                skipped_non_html += 1
            continue
        logging.info(f"Crawled: {url}")  # <--- Log the crawled page
        cleaned = clean_html(html)
        chunks = split_html_into_chunks(cleaned)
        count = add_documents_to_chroma(chunks, url)
        chunks_indexed += count
        pages_processed += 1

        # Fallback link discovery (always allow—even if sitemap exists—to improve coverage)
        discovered = _extract_links(html, url, domain)
        to_visit.update(discovered - visited)

        time.sleep(CRAWL_DELAY_SECONDS)

    return {
        "pages_processed": pages_processed,
        "chunks_indexed": chunks_indexed,
        "skipped_non_html": skipped_non_html,
        "visited_count": len(visited),
    }
