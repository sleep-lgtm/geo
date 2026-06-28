from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from db import Base


class GeoPage(Base):
    __tablename__ = "geo_pages"

    id = Column(Integer, primary_key=True)
    title = Column(String(500))
    url = Column(String(2048))
    html = Column(Text, nullable=False)
    jsonld = Column(JSONB)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
