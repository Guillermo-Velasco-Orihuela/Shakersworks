import chromadb
from chromadb.config import Settings as ChromaSettings


class VectorStoreClient:
    """
    Client for interacting with a Chroma vector store collection.

    Provides methods to upsert embedding records and query similar documents.
    """

    def __init__(self, url: str = None):  # pragma: no cover
        """
        Initialize the Chroma client and get (or create) the 'shakers' collection.

        Args:
            url: Optional Chroma server URL (not used when running embedded).
        """
        # Instantiate the Chroma client with default settings
        self.client = chromadb.Client(ChromaSettings())
        # Retrieve or create the named collection for vector operations
        self.collection = self.client.get_or_create_collection("shakers")

    def upsert(self, records: list[dict]):
        """
        Upsert a batch of embedding records into the vector store.

        Each record should include 'id', 'embedding', and 'metadata' keys.

        Args:
            records: List of dicts containing embedding data and metadata.
        """
        # Extract parallel lists for IDs, embeddings, metadata, and document text
        ids = [r["id"] for r in records]
        embeddings = [r["embedding"] for r in records]
        metadatas = [r["metadata"] for r in records]
        documents = [r["metadata"].get("text", "") for r in records]

        # Perform batch add to the Chroma collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents,
        )

    def query(self, embedding: list[float], top_k: int = 5) -> list[dict]:
        """
        Query the vector store for the most similar documents to an embedding.

        Args:
            embedding: A single embedding vector to query.
            top_k: Number of top results to return.

        Returns:
            A list of dicts containing 'title', 'text', 'url', 'score', and 'embedding'.
        """
        # Execute the similarity search on the collection
        res = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
            include=["metadatas", "documents", "distances", "embeddings"],
        )
        # Extract returned lists for the first (and only) query
        metadatas = res["metadatas"][0]
        documents = res["documents"][0]
        distances = res["distances"][0]
        embs = res["embeddings"][0]

        # Combine parallel lists into the expected output format
        results = []
        for meta, text, dist, emb in zip(metadatas, documents, distances, embs):
            results.append({
                "title": meta.get("title", ""),
                "text": text,
                "url": meta.get("url", ""),
                "score": dist,
                "embedding": emb,
            })
        return results
