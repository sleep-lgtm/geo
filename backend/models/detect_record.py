from sqlalchemy import Column, Integer, SmallInteger, String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from db import Base


class DetectRecord(Base):
    __tablename__ = "detect_records"

    id = Column(Integer, primary_key=True)
    url = Column(String(2048))
    total = Column(SmallInteger)
    structure = Column(SmallInteger)
    entity = Column(SmallInteger)
    semantic = Column(SmallInteger)
    freshness = Column(SmallInteger)
    issues = Column(JSONB)
    suggestions = Column(JSONB)
    page_id = Column(Integer, ForeignKey("geo_pages.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
