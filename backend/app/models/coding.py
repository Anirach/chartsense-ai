from sqlalchemy import Column, String, Integer, Float, DateTime, JSON
from datetime import datetime

from app.db.database import Base


class CodeSuggestion(Base):
    __tablename__ = "code_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    encounter_id = Column(String(30), index=True, nullable=False)
    icd_code = Column(String(10), nullable=False)
    description = Column(String(500), nullable=False)
    dx_type = Column(String(10), default="SDx")
    confidence = Column(Float, nullable=False)
    evidence = Column(JSON, default=list)
    rw_impact = Column(Float, default=0)
    status = Column(String(20), default="PENDING")
    created_at = Column(DateTime, default=datetime.utcnow)


class RWCalculation(Base):
    __tablename__ = "rw_calculations"

    id = Column(Integer, primary_key=True, index=True)
    encounter_id = Column(String(30), index=True, nullable=False)
    drg = Column(String(10), nullable=True)
    rw_before = Column(Float, default=0)
    rw_after = Column(Float, default=0)
    delta = Column(Float, default=0)
    revenue_impact = Column(Float, default=0)
    calculated_at = Column(DateTime, default=datetime.utcnow)
