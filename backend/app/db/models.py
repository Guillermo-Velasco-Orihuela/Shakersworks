import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


# SQLAlchemy models for user profiles and their query logs
class UserProfile(Base):
    """
    Represents a user profile, storing the unique user identifier and
    linking to the user's query history.
    """
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    # Relationship to associate with UserQueryLog entries
    queries = relationship("UserQueryLog", back_populates="user_profile")


class UserQueryLog(Base):
    """
    Logs individual user queries, including the query text and timestamp,
    linked back to the corresponding UserProfile.
    """
    __tablename__ = "user_query_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_profile_id = Column(
        Integer,
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    query_text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    # Back-reference to the owning UserProfile
    user_profile = relationship("UserProfile", back_populates="queries")


class TalentProfile(Base):
    __tablename__ = "talent_profiles"
    id              = Column(Integer, primary_key=True)
    name            = Column(String, nullable=False)
    headline        = Column(String, nullable=False)
    skills          = Column(String)  # comma-separated
    experience_years= Column(Integer)
    bio             = Column(Text)
