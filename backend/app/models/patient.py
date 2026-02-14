from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Text, Boolean, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    hn = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    age = Column(Integer, nullable=False)
    sex = Column(String(10), nullable=False)
    pmh = Column(JSON, default=list)
    allergies = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    encounters = relationship("Encounter", back_populates="patient")


class Encounter(Base):
    __tablename__ = "encounters"

    id = Column(Integer, primary_key=True, index=True)
    encounter_id = Column(String(30), unique=True, index=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    admit_date = Column(DateTime, nullable=False)
    dc_date = Column(DateTime, nullable=True)
    ward = Column(String(50), nullable=False)
    los = Column(Integer, default=0)
    status = Column(String(20), default="ACTIVE")
    chief_complaint = Column(Text, nullable=True)

    patient = relationship("Patient", back_populates="encounters")
    diagnoses = relationship("Diagnosis", back_populates="encounter")
    observations = relationship("Observation", back_populates="encounter")
    orders = relationship("OrderRecord", back_populates="encounter")
    progress_notes = relationship("ProgressNote", back_populates="encounter")


class Diagnosis(Base):
    __tablename__ = "diagnoses"

    id = Column(Integer, primary_key=True, index=True)
    encounter_id = Column(Integer, ForeignKey("encounters.id"), nullable=False)
    icd_code = Column(String(10), nullable=False)
    description = Column(String(500), nullable=False)
    dx_type = Column(String(10), nullable=False)  # PDx, SDx
    source = Column(String(10), default="MD")  # MD, AI
    confidence = Column(Float, nullable=True)
    evidence = Column(JSON, default=list)

    encounter = relationship("Encounter", back_populates="diagnoses")


class Observation(Base):
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, index=True)
    encounter_id = Column(Integer, ForeignKey("encounters.id"), nullable=False)
    obs_type = Column(String(20), nullable=False)  # vital, lab, imaging
    code = Column(String(50), nullable=False)
    display_name = Column(String(200), nullable=False)
    value = Column(String(100), nullable=False)
    unit = Column(String(30), nullable=True)
    date_time = Column(DateTime, nullable=False)
    abnormal_flag = Column(Boolean, default=False)
    reference_range = Column(String(50), nullable=True)

    encounter = relationship("Encounter", back_populates="observations")


class OrderRecord(Base):
    __tablename__ = "order_records"

    id = Column(Integer, primary_key=True, index=True)
    encounter_id = Column(Integer, ForeignKey("encounters.id"), nullable=False)
    category = Column(String(20), nullable=False)  # LAB, IMAGING, MEDICATION, NURSING, DIET
    standard_code = Column(String(50), nullable=False)
    display_name = Column(String(300), nullable=False)
    status = Column(String(20), default="ORDERED")
    cpg_source = Column(String(100), nullable=True)
    priority = Column(String(20), default="RECOMMENDED")

    encounter = relationship("Encounter", back_populates="orders")


class ProgressNote(Base):
    __tablename__ = "progress_notes"

    id = Column(Integer, primary_key=True, index=True)
    encounter_id = Column(Integer, ForeignKey("encounters.id"), nullable=False)
    date_time = Column(DateTime, nullable=False)
    text = Column(Text, nullable=False)
    extracted_dx = Column(JSON, default=list)
    nlp_entities = Column(JSON, default=list)
    author = Column(String(100), nullable=True)

    encounter = relationship("Encounter", back_populates="progress_notes")
