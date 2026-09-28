# Disease Prediction and Risk Assessment System

## Project Overview

This project implements a disease prediction and health risk assessment pipeline using machine learning.

## Technologies Used

- Python
- Pandas
- NumPy
- Scikit-learn
- Random Forest
- SQLite
- Flask

## Project Workflow

Symptoms
→ Data Preprocessing
→ Symptom Encoding
→ Disease Prediction
→ Probability Score
→ Risk Assessment
→ SQLite Database
→ Flask API
→ Health Risk Report

## Machine Learning

The disease symptom dataset is preprocessed by handling missing values and encoding symptoms into binary features.

A Random Forest classification model is trained to predict the disease class and generate probability scores.

## Risk Assessment

Patient-level risk indicators are used to calculate a prototype risk-factor score.

The disease probability is also converted into a probability score.

These values are combined to generate a project risk level:

- Low
- Medium
- High

## Database

SQLite is used to store:

- Patient profiles
- Disease predictions
- Risk assessments

## API

A Flask API provides the health risk report through:

`/risk-report/<patient_id>`

Example:

`/risk-report/3`

## Important Note

The risk scoring logic is a prototype project implementation and is not intended to provide a medical diagnosis or clinically validated risk assessment.