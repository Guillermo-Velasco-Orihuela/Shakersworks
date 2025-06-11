from fastapi import FastAPI, Response
from app.db.session import engine, Base
from app.api.query import router as query_router
from app.api.recommend import router as rec_router
from app.api.admin import router as admin_router   # <— import it
from app.utils.metrics import metrics_response

# startup
Base.metadata.create_all(bind=engine)
from app.utils.ingest import ingest_corpus
ingest_corpus()

app = FastAPI(title="Shakers RAG + Recommender")

app.include_router(query_router,  prefix="/query",     tags=["query"])
app.include_router(rec_router,    prefix="/recommend", tags=["recommend"])
app.include_router(admin_router)                   # <— mount /reload-index

@app.get("/metrics")
def metrics():
    data, media_type = metrics_response()
    return Response(content=data, media_type=media_type)
