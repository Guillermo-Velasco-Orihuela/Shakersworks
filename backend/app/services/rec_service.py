import numpy as np
from app.db.models import UserProfile, UserQueryLog

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """
    Compute the cosine similarity between two embedding vectors.

    Returns a float between -1 and 1.
    """
    # Dot product divided by product of norms
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


class RecService:
    """
    Recommendation service that generates personalized content based
    on a user's query history and vector similarity.
    """

    def __init__(
        self,
        db,
        embedding_client,
        vector_store,
    ):
        # Initialize dependencies
        self.db = db
        self.embedding_client = embedding_client
        self.vector_store = vector_store

    def recommend(self, user_id: str, top_k: int = 3) -> list[dict]:
        """
        Generate up to top_k recommendations for a user based on past queries.

        Steps:
        1) Retrieve or create UserProfile for the given ID.
        2) Load and embed past query texts.
        3) Compute a combined profile embedding (mean of query embeddings).
        4) Retrieve candidate documents and explain recommendations.
        5) Deduplicate by title and return the top_k results.
        """
        # 1) Get or create profile
        profile = (
            self.db.query(UserProfile)
            .filter_by(user_id=user_id)
            .first()
        )
        if not profile:
            profile = UserProfile(user_id=user_id)
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)

        # 2) Load past queries and extract texts
        logs = (
            self.db.query(UserQueryLog)
            .filter_by(user_profile_id=profile.id)
            .order_by(UserQueryLog.timestamp.desc())
            .all()
        )
        texts = [log.query_text for log in logs]

        # 3) Embed each query and combine into a profile embedding
        query_embs = [
            np.array(self.embedding_client.embed(text))
            for text in texts
        ]
        if query_embs:
            profile_emb = np.mean(query_embs, axis=0).tolist()
        else:
            # Fallback embedding for new users
            profile_emb = self.embedding_client.embed("")

        # 4) Retrieve candidate docs (over-fetch for deduplication)
        raw_docs = self.vector_store.query(
            profile_emb,
            top_k=top_k * 3,
        )

        # Build explanations for each candidate based on highest similarity
        chunk_recs = []
        for doc in raw_docs:
            doc_emb = np.array(doc["embedding"])
            if query_embs:
                # Find the query most similar to this document
                sims = [cosine_sim(doc_emb, q_emb) for q_emb in query_embs]
                best_idx = int(np.argmax(sims))
                ref_q = texts[best_idx]
            else:
                ref_q = "our platform"
            chunk_recs.append(
                {
                    "title": doc["title"],
                    "explanation": (
                        f"Based on your interest in '{ref_q}'."
                    ),
                }
            )

        # 5) Deduplicate by title, preserve order, and limit to top_k
        unique = []
        seen = set()
        for rec in chunk_recs:
            if rec["title"] not in seen:
                seen.add(rec["title"])
                unique.append(rec)
            if len(unique) >= top_k:
                break

        return unique
