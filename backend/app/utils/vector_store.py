# backend/app/utils/vector_store.py

import chromadb
from chromadb.config import Settings as ChromaSettings

class VectorStoreClient:
    def __init__(self, url: str = None):
        self.client     = chromadb.Client(ChromaSettings())
        self.collection = self.client.get_or_create_collection("shakers")

    def upsert(self, records: list):
        ids        = [r["id"]        for r in records]
        embeddings = [r["embedding"] for r in records]
        metadatas  = [r["metadata"]  for r in records]
        documents  = [r["metadata"].get("text", "") for r in records]

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents,
        )

    def query(self, embedding, top_k: int = 5) -> list:
        """
        Returns a list of dicts each containing:
          title, text, url, score (distance), embedding (vector)
        """
        res = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
            include=["metadatas","documents","distances","embeddings"]
        )
        metadatas  = res["metadatas"][0]
        documents  = res["documents"][0]
        distances  = res["distances"][0]
        embs       = res["embeddings"][0]

        docs = []
        for meta, text, dist, emb in zip(metadatas, documents, distances, embs):
            docs.append({
                "title":     meta.get("title",""),
                "text":      text,
                "url":       meta.get("url",""),
                "score":     dist,
                "embedding": emb,
            })
        return docs
