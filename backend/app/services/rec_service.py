from app.utils.embeddings import EmbeddingClient
from app.utils.vector_store import VectorStoreClient

class RecService:
    """
    Recommend talents by embedding the user request and doing
    a nearest‐neighbor search on the talent_profiles collection.
    """

    def __init__(self, api_key: str, persist_directory: str):
        """
        Args:
          api_key:            OpenAI API key for embeddings.
          persist_directory:  Filesystem path where your Chroma DB lives.
        """
        self.embedding_client = EmbeddingClient(api_key=api_key)
        self.vector_store     = VectorStoreClient(
            persist_directory=persist_directory,
            collection_name="talent_profiles",
        )

    def recommend(self, request: str, top_k: int = 5) -> list[dict]:
        """
        Embed the incoming request and return the top_k matching talents.
        """
        # 1) Embed the user’s request
        req_emb = self.embedding_client.embed(request)

        # 2) Perform a vector lookup
        docs = self.vector_store.query(req_emb, top_k=top_k)

        # 3) Build the output list
        recs = []
        for record in docs:
            recs.append({
                "name":        record["name"],
                "role":        record["role"],
                "experience":  record["experience"],
                "explanation": f"{record['name']} is a {record['role']} "
                               f"with {record['experience']} years of experience."
            })
        return recs
