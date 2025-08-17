import re
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter, HTMLHeaderTextSplitter

HEADERS_TO_SPLIT = [("h1", "H1"), ("h2", "H2"), ("h3", "H3")]
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Remove junk
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
        tag.decompose()
    for el in soup.find_all(attrs={"class": re.compile(r".*(ad|ads|advert).*", re.I)}):
        el.decompose()
    for el in soup.find_all(attrs={"id": re.compile(r".*(ad|ads|advert).*", re.I)}):
        el.decompose()

    return str(soup)

def split_html_into_chunks(html: str) -> list[str]:
    """
    Heading-aware splitting first, then token-safe chunking with overlap.
    Falls back to plain text splitting when no headers.
    """
    header_splitter = HTMLHeaderTextSplitter(headers_to_split_on=HEADERS_TO_SPLIT)
    header_docs = header_splitter.split_text(html)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " "],
    )

    if not header_docs:
        text = BeautifulSoup(html, "html.parser").get_text(separator="\n")
        chunks = splitter.split_text(text)
    else:
        chunks = []
        for doc in header_docs:
            chunks.extend(splitter.split_text(doc.page_content))

    # Deduplicate + strip empties
    seen = set()
    final = []
    for c in (c.strip() for c in chunks):
        if c and c not in seen:
            seen.add(c)
            final.append(c)
    return final
