import random
import sys
import os
from datetime import datetime, timedelta

# Ensure project root is on the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal, Base, engine
from app.db.models import UserProfile, UserQueryLog


if __name__ == "__main__":
    """
    Seed the database with 10 sample user profiles, each having 5–10
    historical query logs spread over the past 30 days.
    """
    # 1) (Re)create tables in case of a fresh database
    Base.metadata.create_all(bind=engine)

    # 2) Open a new database session
    db = SessionLocal()

    # 3) Define sample user IDs
    sample_users = [
        "alice", "bob", "charlie", "david", "eve",
        "frank", "grace", "heidi", "ivan", "judy",
    ]

    # 4) Define a pool of possible queries
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
        "How do I schedule automated reports?",
    ]

    # 5) Create profiles and log random queries for each user
    for user_id in sample_users:
        # Retrieve or create user profile
        profile = (
            db.query(UserProfile)
            .filter_by(user_id=user_id)
            .first()
        )
        if not profile:
            profile = UserProfile(user_id=user_id)
            db.add(profile)
            db.commit()
            db.refresh(profile)

        # Randomly choose 5–10 unique queries
        n_queries = random.randint(5, 10)
        chosen = random.sample(sample_queries, n_queries)

        # Log each query with a timestamp within the last 30 days
        now = datetime.utcnow()
        for text in chosen:
            timestamp = now - timedelta(days=random.uniform(0, 30))
            log_entry = UserQueryLog(
                user_profile_id=profile.id,
                query_text=text,
                timestamp=timestamp,
            )
            db.add(log_entry)
        db.commit()

    # 6) Close session and report completion
    db.close()
    print("✅ Created 10 sample user profiles with 5–10 historical queries each.")
