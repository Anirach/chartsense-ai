from sqlalchemy import Column, String, Integer, Float, JSON, Boolean, Text
from app.db.database import Base


class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(String(20), unique=True, index=True, nullable=False)
    category = Column(String(30), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    weight = Column(Float, default=1.0)
    condition = Column(JSON, nullable=False)
    active = Column(Boolean, default=True)


class CPGTemplate(Base):
    __tablename__ = "cpg_templates"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(String(30), unique=True, index=True, nullable=False)
    disease_group = Column(String(50), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    orders = Column(JSON, default=list)
    criteria = Column(JSON, default=dict)
    version = Column(String(10), default="1.0")
