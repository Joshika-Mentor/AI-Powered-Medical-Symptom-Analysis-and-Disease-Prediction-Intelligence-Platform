import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import joblib

def train_model():
    clean_file_path = '../data/processed/cleaned_symptoms.csv'
    model_save_path = 'rf_model.pkl'
    encoder_save_path = 'label_encoder.pkl'

    print("Loading cleaned dataset...")
    try:
        df = pd.read_csv(clean_file_path)
    except FileNotFoundError:
        print(f"ERROR: Cannot find {clean_file_path}. Run data_pipeline.py first.")
        return

    X = df.drop(columns=['prognosis'])
    y_raw = df['prognosis']

    le = LabelEncoder()
    y = le.fit_transform(y_raw)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Training Random Forest model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    print("Testing model accuracy...")
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    
    print(f"\n--- Model Accuracy: {accuracy * 100:.2f}% ---\n")

    joblib.dump(model, model_save_path)
    joblib.dump(le, encoder_save_path)
    print(f"Saved model to {model_save_path}")
    print(f"Saved encoder to {encoder_save_path}")

if __name__ == "__main__":
    train_model()