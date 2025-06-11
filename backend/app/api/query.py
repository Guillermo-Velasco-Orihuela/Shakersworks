from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import time

from app.core.config import settings
from app.db.session import get_db
from app.models.schemas import QueryRequest, QueryResponse
from app.services.rag_service import RagService
from app.utils.embeddings import EmbeddingClient
from app.utils.vector_store import VectorStoreClient
from app.utils.llm import LLMClient
from app.utils.cache import get_cache, cache_get, cache_set
from app.utils.metrics import CACHE_HITS, CACHE_MISSES, LLM_CALLS

router = APIRouter()

# Initialize clients with API keys and configurations
emb_client = EmbeddingClient(api_key=settings.OPENAI_API_KEY)
vector_store = VectorStoreClient()
llm_client = LLMClient(api_key=settings.OPENAI_API_KEY)

# Simple in-memory cache and TTL configuration
cache = get_cache()
CACHE_TTL = 300  # seconds


@router.post("", response_model=QueryResponse)
def query_endpoint(
    body: QueryRequest,
    db: Session = Depends(get_db),
):
    """
    Handle a question by running a RAG lookup with caching, metrics, and latency tracking.
    """
    endpoint = "query"
    start = time.time()  # Record start time for latency metrics

    # Prepare cache key based on the stripped question
    q = body.question.strip()
    key = f"query:{q}"

    # Attempt to retrieve a cached response
    cached = cache_get(key)
    if cached is not None:
        # Cache hit: increment metric and return the cached result
        CACHE_HITS.labels(endpoint=endpoint).inc()
        duration = time.time() - start
        return cached

    # Cache miss: record miss and that we'll call the LLM
    CACHE_MISSES.labels(endpoint=endpoint).inc()
    LLM_CALLS.labels(endpoint=endpoint).inc()

    # Instantiate the RAG service and get the answer
    service = RagService(
        db_session=db,
        embedding_client=emb_client,
        vector_store=vector_store,
        llm_client=llm_client,
    )
    result = service.ask(body.question)

    # Cache the new result for future calls
    cache_set(key, result, ttl=CACHE_TTL)

    return result
