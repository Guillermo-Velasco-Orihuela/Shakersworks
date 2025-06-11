import numpy as np
from app.db.models import UserProfile, UserQueryLog

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

class RecService:
    def __init__(self, db, embedding_client, vector_store):
        self.db              = db
        self.embedding_client = embedding_client
        self.vector_store     = vector_store

    def recommend(self, user_id: str, top_k: int = 3):
        # 1) Get or create profile
        profile = self.db.query(UserProfile).filter_by(user_id=user_id).first()
        if not profile:
            profile = UserProfile(user_id=user_id)
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)

        # 2) Load past queries
        logs   = (
            self.db.query(UserQueryLog)
            .filter_by(user_profile_id=profile.id)
            .order_by(UserQueryLog.timestamp.desc())
            .all()
        )
        texts  = [log.query_text for log in logs]

        # 3) Embed each individual query
        query_embs = [np.array(self.embedding_client.embed(t)) for t in texts]

        # 4) Build combined profile embedding (mean) for retrieval
        if query_embs:
            profile_emb = np.mean(query_embs, axis=0).tolist()
        else:
            profile_emb = self.embedding_client.embed("")

        # 5) Retrieve top docs (now include doc embeddings)
        docs = self.vector_store.query(profile_emb, top_k=top_k)

        # 6) For each doc, pick the query with highest cosine similarity
        recs = []
        for d in docs:
            doc_emb = np.array(d["embedding"])
            if query_embs:
                sims = [cosine_sim(doc_emb, q_emb) for q_emb in query_embs]
                best_i = int(np.argmax(sims))
                ref_q  = texts[best_i]
            else:
                ref_q = "our platform"
            recs.append({
                "title": d["title"],
                "explanation": f"Based on your interest in '{ref_q}'."
            })

        return recs
