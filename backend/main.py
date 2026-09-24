from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import joblib
import json
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

# Import your existing database and risk logic
from database import SessionLocal, PatientProfile, PredictionRecord
from risk_engine import calculate_risk

app = FastAPI(title="MedAssist AI API")

# Load ML artifacts into memory on server startup
try:
    model = joblib.load('rf_model.pkl')
    encoder = joblib.load('label_encoder.pkl')
    with open('../data/processed/symptoms_schema.json', 'r') as f:
        symptoms_schema = json.load(f)
except Exception as e:
    raise RuntimeError("Failed to load ML artifacts. Run data_pipeline.py and model_training.py first.")

# Dependency to open and close DB connections per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define the strict data payload expected from the frontend
class PatientRequest(BaseModel):
    name: str
    age: int
    gender: str
    bmi: float
    smoker: bool
    high_blood_pressure: bool
    diabetes: bool
    symptoms: List[str]

@app.get("/api/v1/symptoms")
def get_symptoms():
    """Returns the list of 133 symptoms for the frontend dropdowns."""
    return {"symptoms": symptoms_schema}

@app.post("/api/v1/predict")
def create_prediction_report(request: PatientRequest, db: Session = Depends(get_db)):
    """Ingests patient data, runs AI prediction, calculates risk, and saves to DB."""
    
    # 1. Save Patient Profile
    new_patient = PatientProfile(
        name=request.name,
        age=request.age,
        gender=request.gender,
        bmi=request.bmi,
        smoker=request.smoker,
        high_blood_pressure=request.high_blood_pressure,
        diabetes=request.diabetes
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    # 2. Build AI Input Vector
    input_df = pd.DataFrame(columns=model.feature_names_in_)
    input_df.loc[0] = 0
    
    valid_symptoms = []
    for sym in request.symptoms:
        if sym in input_df.columns:
            input_df.at[0, sym] = 1
            valid_symptoms.append(sym)
            
    if not valid_symptoms:
        raise HTTPException(status_code=400, detail="No valid symptoms recognized.")

    # 3. Generate AI Prediction
    probabilities = model.predict_proba(input_df)[0]
    top_3_indices = np.argsort(probabilities)[-3:][::-1]
    
    probability_report = {
        encoder.classes_[idx]: round(probabilities[idx] * 100, 2)
        for idx in top_3_indices
    }
    
    top_disease = encoder.classes_[top_3_indices[0]]
    top_score = probabilities[top_3_indices[0]]

    # 4. Calculate BRFSS Risk Score
    risk_score, severity_level = calculate_risk(new_patient, top_disease, top_score)

    # 5. Save the Full Assessment Record
    new_prediction = PredictionRecord(
        patient_id=new_patient.id,
        symptoms_input=json.dumps(valid_symptoms),
        top_prediction=top_disease,
        confidence_score=top_score,
        probability_report=json.dumps(probability_report),
        risk_score=risk_score,
        severity_level=severity_level
    )
    db.add(new_prediction)
    db.commit()

    # 6. Return the finalized Health Risk Report to the client
    return {
        "status": "success",
        "patient_id": new_patient.id,
        "patient_name": new_patient.name,
        "diagnosis": {
            "top_prediction": top_disease,
            "confidence_score": f"{top_score * 100:.2f}%",
            "differential": probability_report
        },
        "risk_assessment": {
            "score": f"{risk_score}/15",
            "severity": severity_level
        }
    }