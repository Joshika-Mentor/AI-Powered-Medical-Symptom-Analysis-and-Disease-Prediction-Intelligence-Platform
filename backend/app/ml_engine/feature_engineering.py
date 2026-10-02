import pandas as pd

def extract_features(symptoms: dict, demographics: dict):
    data = {**symptoms, **demographics}
    return pd.DataFrame([data])
