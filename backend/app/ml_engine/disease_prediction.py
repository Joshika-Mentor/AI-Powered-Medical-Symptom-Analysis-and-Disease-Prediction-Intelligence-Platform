import joblib
import os
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'disease_model.pkl')
try:
    pipeline = joblib.load(MODEL_PATH)
except Exception as e:
    pipeline = None
    print(f"Failed to load model: {e}")

def predict_disease(features_df):
    if not pipeline:
        return {"top_diseases": [{"disease": "Model Not Loaded", "probability": 0.0}]}
    
    probs = pipeline.predict_proba(features_df)[0]
    classes = pipeline.classes_
    top_indices = np.argsort(probs)[::-1][:3]
    
    top_diseases = []
    for i in top_indices:
        if probs[i] > 0.01:  # filter out extremely low probabilities
            top_diseases.append({"disease": classes[i], "probability": round(float(probs[i]), 4)})
            
    return {"top_diseases": top_diseases}
