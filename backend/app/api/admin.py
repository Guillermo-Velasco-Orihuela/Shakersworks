from fastapi import APIRouter, HTTPException
from app.utils.ingest import ingest_corpus

router = APIRouter(tags=["admin"])

@router.post("/reload-index")
def reload_index():
    """
    Re-ingest all Markdown files into the vector store at runtime.
    """
    try:
        ingest_corpus()
        return {"status": "index refreshed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")
