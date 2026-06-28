from sqlalchemy import Column, Integer, SmallInteger, String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from db import Base


class CrawlJob(Base):
    __tablename__ = "crawl_jobs"

    id = Column(Integer, primary_key=True)
    site_url = Column(String(2048), nullable=False)
    status = Column(String(50), default="pending")
    progress = Column(SmallInteger, default=0)
    total_pages = Column(SmallInteger, default=0)
    result = Column(JSONB)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    finished_at = Column(DateTime, nullable=True)


class CrawlPage(Base):
    __tablename__ = "crawl_pages"

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("crawl_jobs.id"))
    url = Column(String(2048))
    detect_id = Column(Integer, ForeignKey("detect_records.id"), nullable=True)
    crawled_at = Column(DateTime, server_default=func.now())
