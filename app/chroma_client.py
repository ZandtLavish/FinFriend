import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
import logging
logger = logging.getLogger(__name__)

from app.config import settings

def get_chroma_client() -> chromadb.HttpClient:
    return chromadb.HttpClient(
        host=settings.CHROMA_HOST,
        port=int(settings.CHROMA_PORT),
        settings=Settings(
            chroma_client_auth_provider="chromadb.auth.token_authn.TokenAuthClientProvider",
            chroma_client_auth_credentials=settings.CHROMA_TOKEN,
        )
    )

def get_vector_store(collection: str = "financial_docs") -> Chroma:
    return Chroma(
        client=get_chroma_client(),
        collection_name=collection,
        embedding_function=OllamaEmbeddings(model="nomic-embed-text")
    )