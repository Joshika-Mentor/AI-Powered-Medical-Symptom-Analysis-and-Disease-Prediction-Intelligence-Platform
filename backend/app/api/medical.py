from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json
from app.db.database import get_db, MedicalReport
from app.ml_engine import symptom_understanding, feature_engineering, disease_prediction, risk_assessment, recommendation_engine

router = APIRouter()

class AnalysisRequest(BaseModel):
    patient_id: str
    symptoms: str
    age: int
    gender: str
    blood_pressure: str = "Normal"
    cholesterol: str = "Normal"

@router.post("/analyze")
def analyze_symptoms(req: AnalysisRequest, db: Session = Depends(get_db)):
    parsed = symptom_understanding.parse_symptoms(req.symptoms)
    features = feature_engineering.extract_features(parsed, {"Age": req.age, "Gender": req.gender, "Blood Pressure": req.blood_pressure, "Cholesterol Level": req.cholesterol})
    prediction = disease_prediction.predict_disease(features)
    risk = risk_assessment.assess_risk(prediction.get("top_diseases", []))
    recommendation = recommendation_engine.generate_recommendations(prediction.get("top_diseases", []), risk.get("risk_level", "Low"))
    
    # Save to Database
    db_report = MedicalReport(
        patient_id=req.patient_id,
        symptoms=req.symptoms,
        predictions=json.dumps(prediction.get("top_diseases", [])),
        risk_level=risk.get("risk_level", "Low"),
        recommendation=recommendation.get("advice", "")
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    
    return {
        "report_id": db_report.id,
        "symptoms_parsed": parsed,
        "prediction": prediction,
        "risk_assessment": risk,
        "recommendation": recommendation
    }

@router.get("/history/{patient_id}")
def get_history(patient_id: str, db: Session = Depends(get_db)):
    reports = db.query(MedicalReport).filter(MedicalReport.patient_id == patient_id).order_by(MedicalReport.timestamp.desc()).all()
    return [{"id": r.id, "date": r.timestamp, "symptoms": r.symptoms, "risk": r.risk_level, "predictions": json.loads(r.predictions)} for r in reports]
