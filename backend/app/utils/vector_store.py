import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb import PersistentClient
from pathlib import Path

class VectorStoreClient:
    """
    Client for interacting with a Chroma vector store collection,
    backed by an on-disk DuckDB+Parquet store so embeddings persist
    across processes.
    """

    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        collection_name: str = "shakers",
    ):
        """
        Args:
          persist_directory: path where Chroma will write its
              DuckDB+Parquet files.
          collection_name:   name of the collection to use
                             (e.g. "talent_profiles").
        """
        db_dir = Path(persist_directory)
        db_dir.mkdir(parents=True, exist_ok=True)

        # New PersistentClient API — no deprecated configs
        self.client = PersistentClient(path=str(db_dir))
        self.collection = self.client.get_or_create_collection(collection_name)

    def upsert(self, records: list[dict]):
        """
        Upsert a batch of embedding records into the vector store.

        Each record must include 'id', 'embedding', and 'metadata'.
        Supports both RAG (metadata.text) and talent (metadata.description).
        """
        ids        = [r["id"]        for r in records]
        embeddings = [r["embedding"] for r in records]
        metadatas  = [r["metadata"]  for r in records]
        documents  = [
            r["metadata"].get("description", "")
            or r["metadata"].get("text", "")
            for r in records
        ]

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents,
        )

    def query(self, embedding: list[float], top_k: int = 5) -> list[dict]:
        """
        Query the vector store for the most similar entries.

        Returns a list of dicts, each containing all metadata fields plus:
          - 'text': the stored document or description
          - 'score': the distance value
          - 'embedding': the original vector
        """
        res = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
            include=["metadatas","documents","distances","embeddings"],
        )
        metadatas = res["metadatas"][0]
        documents = res["documents"][0]
        distances = res["distances"][0]
        embs      = res["embeddings"][0]

        results = []
        for meta, doc, dist, emb in zip(metadatas, documents, distances, embs):
            record = {**meta}
            record["text"]      = doc
            record["score"]     = dist
            record["embedding"] = emb
            results.append(record)
        return results
