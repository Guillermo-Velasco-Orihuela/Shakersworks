import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"
    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    queries    = relationship("UserQueryLog", back_populates="user_profile")

class UserQueryLog(Base):
    __tablename__    = "user_query_logs"
    id                = Column(Integer, primary_key=True, index=True)
    user_profile_id   = Column(Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False)
    query_text        = Column(Text, nullable=False)
    timestamp         = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    user_profile      = relationship("UserProfile", back_populates="queries")
