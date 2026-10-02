def assess_risk(diseases: list):
    if not diseases:
        return {"risk_level": "Low", "severity_score": 1.0}
    
    top_prob = diseases[0]['probability']
    if top_prob > 0.8:
        level = "High"
        score = 8.5
    elif top_prob > 0.4:
        level = "Medium"
        score = 5.0
    else:
        level = "Low"
        score = 2.0
        
    return {"risk_level": level, "severity_score": score}
