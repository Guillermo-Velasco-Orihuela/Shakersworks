# backend/scripts/generate_sample_user_data.py

import random
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.db.session     import SessionLocal, Base, engine
from app.db.models      import UserProfile, UserQueryLog

# 1) (Re)create tables in case you’re on a fresh DB
Base.metadata.create_all(bind=engine)

# 2) Spin up a session
db = SessionLocal()

# 3) Define some sample users and queries
sample_users   = ["alice", "bob", "charlie"]
sample_queries = [
    "How do I invite collaborators?",
    "What are the pricing plans?",
    "How do I create a new workspace?",
    "Where can I find the knowledge base?",
    "How do I integrate Slack with Shakers?"
]

# 4) For each user, ensure a profile exists, then log 3 random queries
for uid in sample_users:
    profile = db.query(UserProfile).filter_by(user_id=uid).first()
    if not profile:
        profile = UserProfile(user_id=uid)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    # Log three random historical queries
    for q in random.sample(sample_queries, 3):
        log = UserQueryLog(
            user_profile_id=profile.id,
            query_text=q
        )
        db.add(log)
    db.commit()

db.close()
print("✅ Sample user profiles and query logs created.")
