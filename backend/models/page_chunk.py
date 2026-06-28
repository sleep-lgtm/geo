from sqlalchemy import Column, Integer, SmallInteger, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
from db import Base


class PageChunk(Base):
    __tablename__ = "page_chunks"

    id = Column(Integer, primary_key=True)
    page_id = Column(Integer, ForeignKey("geo_pages.id"))
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536))
    metadata_ = Column("metadata", JSONB)
    chunk_index = Column(SmallInteger)
