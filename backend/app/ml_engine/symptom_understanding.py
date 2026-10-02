def parse_symptoms(raw_text: str):
    text = str(raw_text).lower()
    
    # Synonym Mapping & Normalization
    fever_synonyms = ['fever', 'warm', 'hot', 'cold', 'chills', 'temperature']
    cough_synonyms = ['cough', 'coughing', 'hack']
    fatigue_synonyms = ['fatigue', 'tired', 'exhausted', 'weak', 'sleepy']
    breath_synonyms = ['breath', 'breathing', 'wheeze', 'gasp', 'pant']
    
    return {
        "Fever": "Yes" if any(s in text for s in fever_synonyms) else "No",
        "Cough": "Yes" if any(s in text for s in cough_synonyms) else "No",
        "Fatigue": "Yes" if any(s in text for s in fatigue_synonyms) else "No",
        "Difficulty Breathing": "Yes" if any(s in text for s in breath_synonyms) else "No"
    }
