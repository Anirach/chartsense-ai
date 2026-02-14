from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON
from datetime import datetime

from app.db.database import Base


class ChartScore(Base):
    __tablename__ = "chart_scores"

    id = Column(Integer, primary_key=True, index=True)
    encounter_id = Column(String(30), index=True, nullable=False)
    total_score = Column(Float, nullable=False)
    diagnosis_score = Column(Float, default=0)
    procedure_score = Column(Float, default=0)
    consistency_score = Column(Float, default=0)
    documentation_score = Column(Float, default=0)
    breakdown = Column(JSON, default=dict)
    evaluated_at = Column(DateTime, default=datetime.utcnow)


class ChartScoreGap(Base):
    __tablename__ = "chart_score_gaps"

    id = Column(Integer, primary_key=True, index=True)
    chart_score_id = Column(Integer, ForeignKey("chart_scores.id"), nullable=False)
    rule_id = Column(String(20), nullable=False)
    category = Column(String(30), nullable=False)
    description = Column(String(500), nullable=False)
    severity = Column(String(20), default="WARNING")
    suggested_action = Column(String(500), nullable=True)
    suggested_code = Column(String(10), nullable=True)
