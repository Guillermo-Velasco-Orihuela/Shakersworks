import random
import sys
import os
from datetime import datetime, timedelta

# Make sure we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal, Base, engine
from app.db.models import UserProfile, UserQueryLog

# 1) (Re)create tables in case you’re on a fresh DB
Base.metadata.create_all(bind=engine)

# 2) Spin up a session
db = SessionLocal()

# 3) Define 10 sample users
sample_users = [
    "alice", "bob", "charlie", "david", "eve",
    "frank", "grace", "heidi", "ivan", "judy"
]

# 4) Define a larger pool of sample queries
sample_queries = [
    "How do I invite collaborators?",
    "What are the pricing plans?",
    "How do I create a new workspace?",
    "Where can I find the knowledge base?",
    "How do I integrate Slack with Shakers?",
    "How do I configure notifications?",
    "How do I export data?",
    "How do I manage billing contacts?",
    "How do I set up SSO?",
    "How do I reset my password?",
    "How do I customize my dashboard?",
    "How do I upload files?",
    "How do I delete a workspace?",
    "How do I change my email address?",
    "How do I view usage analytics?",
    "How do I enable two-factor authentication?",
    "How do I share a link to a document?",
    "How do I search across all workspaces?",
    "How do I recover deleted items?",
    "How do I schedule automated reports?"
]

# 5) For each user, ensure a profile exists, then log 5–10 random queries
for uid in sample_users:
    profile = db.query(UserProfile).filter_by(user_id=uid).first()
    if not profile:
        profile = UserProfile(user_id=uid)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    # Decide how many queries to log for this user: between 5 and 10
    n_queries = random.randint(5, 10)
    # Sample without replacement to avoid duplicates for the same user
    chosen_queries = random.sample(sample_queries, n_queries)

    # Spread timestamps over the past 30 days
    now = datetime.utcnow()
    for i, q in enumerate(chosen_queries):
        # Assign an earlier timestamp for older queries
        ts = now - timedelta(days=random.uniform(0, 30))
        log = UserQueryLog(
            user_profile_id=profile.id,
            query_text=q,
            timestamp=ts
        )
        db.add(log)
    db.commit()

db.close()
print("✅ Created 10 sample user profiles with 5–10 historical queries each.")
