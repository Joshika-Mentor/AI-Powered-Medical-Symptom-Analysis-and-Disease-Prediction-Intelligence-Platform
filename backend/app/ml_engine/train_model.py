import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

print('Loading dataset...')
df = pd.read_csv('C:/Users/sweth_z24b216/OneDrive/Desktop/INFOSYS/backend/cleaned_dataset.csv')

# Drop Outcome Variable for simplicity, target is Disease
X = df[['Fever', 'Cough', 'Fatigue', 'Difficulty Breathing', 'Age', 'Gender', 'Blood Pressure', 'Cholesterol Level']]
y = df['Disease']

print('Building model pipeline...')
# Categorical and numerical columns
categorical_cols = ['Fever', 'Cough', 'Fatigue', 'Difficulty Breathing', 'Gender', 'Blood Pressure', 'Cholesterol Level']
numerical_cols = ['Age']

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_cols),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols)
    ])

pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
])

print('Training model...')
pipeline.fit(X, y)

model_path = os.path.join(os.path.dirname(__file__), 'disease_model.pkl')
joblib.dump(pipeline, model_path)
print(f'Model trained and saved to {model_path}')
