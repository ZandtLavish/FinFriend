import logging
import requests
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import datetime
from bs4 import BeautifulSoup
from langchain_ollama import OllamaEmbeddings

from app.constants import EDGAR_HEADERS
from app.config import settings
from app.chroma_client import get_vector_store
from app.config_logging import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

embeddings = OllamaEmbeddings(model="nomic-embed-text")

def _filing_to_document(
    filing: dict,
    cik: str,
    company_name: str,
    ticker: str
) -> Document | None:
    """
    Fetch text of a single SEC filing and wrap it in a LangChain Document.
    """
    accession_clean = filing["accession"].replace("-", "")
    filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_clean}/{filing['primary_doc']}"
    logger.debug(f"Fetching SEC Filing: {filing_url}")
    
    try:
        r = requests.get(filing_url, headers=EDGAR_HEADERS, timeout=15)
        r.raise_for_status()
        
        # Extract text
        content_type = r.headers.get("Content-Type", "")
        if "html" in content_type:
            soup = BeautifulSoup(r.text, "html.parser")
            for tag in soup(["script", "style", "table"]):
                tag.decompose()
            text = soup.get_text(separator="\n", strip=True)
        else:
            text = r.text
    except Exception as e:
        logger.error(f"Failed to fetch {filing_url}: {e}")
        return None
    
    doc = Document(
        page_content=text,
        metadata={
            "ticker":        ticker,
            "company_name":  company_name,
            "cik":           cik,
            
            "form_type":     filing["form"],
            "filing_date":   filing["date"],
            "accession":     filing["accession"],
            "items":         filing["items"],       # For 8-Ks
            
            "source":        filing_url,
            "source_type":   "sec_filing",
            "ingested_at":   datetime.datetime.now(tz=datetime.UTC).isoformat(),
        }
    )
    return doc
        

def fetch_sec_filings(
    ticker: str,
    cik: str,
    form_types: list[str] = ["10-K", "10-Q", "8-K"],
    days_back: int = 90
    ) -> list[Document]:
    """
    Fetch recent SEC filings from a company and return as LangChain Documents.
    
    cik: sero-padded 10-digit CIK
    """
    
    # Request SEC fillings by CIK
    r = requests.get(
        f"https://data.sec.gov/submissions/CIK{cik}.json",
        headers=EDGAR_HEADERS
    ).json()
    
    company_name = r.get("name", ticker)
    recent = r["filings"]["recent"]

    filings = [
        {
            "accession":  recent["accessionNumber"][i],
            "form":        recent["form"][i],
            "date":        recent["filingDate"][i],
            "primary_doc": recent["primaryDocument"][i],
            "items":       recent.get("items", [""] * len(recent["form"]))[i],
        }
        for i in range(len(recent["form"]))
    ]
    
    cutoff = (datetime.datetime.now(tz=datetime.UTC) - datetime.timedelta(days=days_back)).strftime("%Y-%m-%d")
    filings = [
        f for f in filings
        if f["form"] in form_types and
        datetime.datetime.fromisoformat(f["date"]) >= datetime.datetime.fromisoformat(cutoff)
    ]
    
    docs = []
    for filing in filings:
        doc = _filing_to_document(filing, cik, company_name, ticker)
        if doc: docs.append(doc)
        
    return docs


def ingest():
    """
    1. Fetch and chunk docs
    2. Ingest into local Chroma DB
    """
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n","\n", ".", " "]
    )
    
    # Collect Document objs and chunk
    raw_docs = []
    for entity in settings.sec_filing_track_list:
        raw_docs_part = fetch_sec_filings(**entity)
        raw_docs += raw_docs_part
    
    chunks = splitter.split_documents(raw_docs)

    # Upsert to Chroma store
    db = get_vector_store()
    db.add_documents(chunks)
    logger.info(f"Ingested {len(chunks)} chunks from {len(raw_docs)} filings")
    
    
if __name__ == "__main__": 
    ingest()