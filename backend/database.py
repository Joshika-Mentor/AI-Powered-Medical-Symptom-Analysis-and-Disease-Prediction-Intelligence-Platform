from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, JSON, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./medassist.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PatientProfile(Base):
    __tablename__ = "patient_profiles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    gender = Column(String)
    # BRFSS Risk Indicators added below
    bmi = Column(Float)
    smoker = Column(Boolean, default=False)
    high_blood_pressure = Column(Boolean, default=False)
    diabetes = Column(Boolean, default=False)

class PredictionRecord(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"))
    symptoms_input = JSON()
    top_prediction = Column(String)
    confidence_score = Column(Float)
    probability_report = JSON()
    # Risk Assessment Outputs added below
    risk_score = Column(Integer)
    severity_level = Column(String) 
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)
print("Database tables updated and initialized successfully.")