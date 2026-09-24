import joblib
import numpy as np
import pandas as pd
import json
from database import SessionLocal, PatientProfile, PredictionRecord
from risk_engine import calculate_risk

def run_prediction_pipeline():
    try:
        model = joblib.load('rf_model.pkl')
        encoder = joblib.load('label_encoder.pkl')
    except FileNotFoundError:
        print("ERROR: Cannot find model or schema files.")
        return

    # 1. Simulate Patient & Symptoms
    reported_symptoms = ["chills", "vomiting", "high_fever", "sweating", "headache", "nausea", "muscle_pain"]
    
    input_df = pd.DataFrame(columns=model.feature_names_in_)
    input_df.loc[0] = 0 
    
    for symptom in reported_symptoms:
        if symptom in input_df.columns:
            input_df.at[0, symptom] = 1
    
    # 2. Generate Probabilities
    probabilities = model.predict_proba(input_df)[0]
    top_3_indices = np.argsort(probabilities)[-3:][::-1]
    
    probability_report = {}
    for idx in top_3_indices:
        disease_name = encoder.classes_[idx]
        score = round(probabilities[idx] * 100, 2)
        probability_report[disease_name] = f"{score}%"

    top_disease = encoder.classes_[top_3_indices[0]]
    top_score = probabilities[top_3_indices[0]]

    # 3. Create Patient with BRFSS Risk Indicators
    db = SessionLocal()
    new_patient = PatientProfile(
        name="John Doe", 
        age=52, 
        gender="Male",
        bmi=31.5,
        smoker=True,
        high_blood_pressure=True,
        diabetes=False
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    # 4. Calculate Risk based on Patient profile and Prediction
    risk_score, severity_level = calculate_risk(new_patient, top_disease, top_score)

    print("\n--- END-TO-END PATIENT REPORT ---")
    print(f"Symptoms: {reported_symptoms}")
    print(f"Top Diagnosis: {top_disease} ({top_score*100:.2f}%)")
    print(f"Differential: {probability_report}")
    print(f"BRFSS Risk Score: {risk_score}/15")
    print(f"Severity Level: {severity_level}")

    # 5. Save comprehensive record
    new_prediction = PredictionRecord(
        patient_id=new_patient.id,
        symptoms_input=json.dumps(reported_symptoms),
        top_prediction=top_disease,
        confidence_score=top_score,
        probability_report=json.dumps(probability_report),
        risk_score=risk_score,
        severity_level=severity_level
    )
    db.add(new_prediction)
    db.commit()
    
    print(f"\nSUCCESS: Pipeline saved to DB for Patient ID {new_patient.id}")
    db.close()

if __name__ == "__main__":
    run_prediction_pipeline()