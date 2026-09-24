def calculate_risk(patient, top_disease, confidence_score):
    """
    Evaluates severity and calculates a risk score based on BRFSS indicators
    (Age, BMI, Smoking, Blood Pressure, Diabetes) combined with the AI prediction.
    """
    risk_score = 0
    
    # 1. BRFSS Demographic & Lifestyle Factors
    if patient.age > 60:
        risk_score += 2
    elif patient.age > 45:
        risk_score += 1
        
    if patient.bmi > 30.0: # Obese
        risk_score += 2
    elif patient.bmi > 25.0: # Overweight
        risk_score += 1
        
    if patient.smoker:
        risk_score += 2
    if patient.high_blood_pressure:
        risk_score += 2
    if patient.diabetes:
        risk_score += 2

    # 2. Disease Severity Modifiers (Emergency vs standard conditions)
    high_severity_conditions = ["Heart attack", "Paralysis (brain hemorrhage)", "AIDS", "Malaria"]
    medium_severity_conditions = ["Diabetes ", "Hypertension ", "Pneumonia", "Dengue"]
    
    if top_disease in high_severity_conditions:
        risk_score += 5
    elif top_disease in medium_severity_conditions:
        risk_score += 3
    else:
        risk_score += 1

    # 3. Confidence Penalty (If AI is unsure, risk of misdiagnosis requires escalation)
    if confidence_score < 0.50:
        risk_score += 1

    # 4. Final Risk Categorization
    if risk_score >= 8:
        severity_level = "HIGH - Immediate Medical Attention Recommended"
    elif risk_score >= 4:
        severity_level = "MEDIUM - Schedule Consultation Soon"
    else:
        severity_level = "LOW - Monitor Symptoms"

    return risk_score, severity_level