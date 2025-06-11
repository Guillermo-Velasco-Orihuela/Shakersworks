from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import get_db
from app.models.schemas import QueryRequest, QueryResponse
from app.services.rag_service import RagService
from app.utils.embeddings import EmbeddingClient
from app.utils.vector_store import VectorStoreClient
from app.utils.llm import LLMClient
from app.utils.cache import get_cache, cache_get, cache_set

router = APIRouter()

emb_client   = EmbeddingClient(api_key=settings.OPENAI_API_KEY)
vector_store = VectorStoreClient(url=settings.VECTOR_STORE_URL)
llm_client   = LLMClient(api_key=settings.OPENAI_API_KEY)

cache      = get_cache()
CACHE_TTL  = 300  # seconds

@router.post("", response_model=QueryResponse)
def query_endpoint(
    body: QueryRequest,
    db: Session = Depends(get_db),
):
    # Normalize question and build cache key
    q = body.question.strip()
    cache_key = f"query:{q}"

    # 1) Try to return cached response
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    # 2) Otherwise compute via RAG
    service = RagService(
        db_session=db,
        embedding_client=emb_client,
        vector_store=vector_store,
        llm_client=llm_client,
    )
    result = service.ask(body.question)

    # 3) Cache and return
    cache_set(cache_key, result, ttl=CACHE_TTL)
    return result
