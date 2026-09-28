import pandas as pd
import sqlite3

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report


# ==========================================
# 1. LOAD THE DATASET
# ==========================================

df = pd.read_csv("dataset/disease_symptoms.csv")

print("Original Dataset Shape:")
print(df.shape)


# ==========================================
# 2. REMOVE UNNECESSARY INDEX COLUMN
# ==========================================

df = df.drop(columns=["Unnamed: 0"])


# ==========================================
# 3. HANDLE MISSING VALUES
# ==========================================

df = df.fillna("")


# ==========================================
# 4. DEFINE SYMPTOM COLUMNS
# ==========================================

symptom_columns = [
    "Symptom_1",
    "Symptom_2",
    "Symptom_3",
    "Symptom_4"
]


# ==========================================
# 5. FIND ALL UNIQUE SYMPTOMS
# ==========================================

all_symptoms = set()

for column in symptom_columns:
    all_symptoms.update(df[column].unique())

all_symptoms.discard("")

symptom_features = sorted(all_symptoms)


# ==========================================
# 6. ENCODE SYMPTOMS
# ==========================================

for symptom in symptom_features:

    df[symptom] = df[symptom_columns].apply(
        lambda row: symptom in row.values,
        axis=1
    ).astype(int)


# ==========================================
# 7. CREATE FEATURES AND TARGET
# ==========================================

X = df[symptom_features]

y = df["Disease"]

print("\nNumber of unique symptoms:")
print(len(symptom_features))

print("\nX Shape:")
print(X.shape)

print("\ny Shape:")
print(y.shape)


# ==========================================
# 8. TRAIN / TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("\nTraining Data:")
print("X_train shape:", X_train.shape)
print("y_train shape:", y_train.shape)

print("\nTesting Data:")
print("X_test shape:", X_test.shape)
print("y_test shape:", y_test.shape)


# ==========================================
# 9. CREATE ML PIPELINE
# ==========================================

pipeline = Pipeline([
    (
        "classifier",
        RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )
    )
])


# ==========================================
# 10. TRAIN THE MODEL
# ==========================================

pipeline.fit(X_train, y_train)

print("\nModel training completed successfully!")


# ==========================================
# 11. MAKE DISEASE PREDICTIONS
# ==========================================

y_pred = pipeline.predict(X_test)

print("\nFirst 10 Predicted Diseases:")
print(y_pred[:10])


# ==========================================
# 12. GENERATE PROBABILITY SCORES
# ==========================================

y_prob = pipeline.predict_proba(X_test)

print("\nProbability Scores Shape:")
print(y_prob.shape)


# ==========================================
# 13. GET DISEASE NAMES
# ==========================================

disease_names = pipeline.named_steps["classifier"].classes_

print("\nNumber of Diseases:")
print(len(disease_names))


# ==========================================
# 14. DISPLAY TOP PROBABILITIES
# ==========================================

first_patient_probabilities = y_prob[0]

probability_table = pd.DataFrame({
    "Disease": disease_names,
    "Probability": first_patient_probabilities
})

probability_table = probability_table.sort_values(
    by="Probability",
    ascending=False
)

print("\nTop Disease Probabilities for First Test Record:")

print(
    probability_table.head(5).to_string(index=False)
)


# ==========================================
# 15. MODEL EVALUATION
# ==========================================

accuracy = accuracy_score(y_test, y_pred)

print("\nModel Accuracy:")
print(accuracy)

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred
    )
)


# ==========================================
# 16. DAY 3 - PATIENT RISK FACTORS
# ==========================================

print("\n==========================================")
print("DAY 3 - PATIENT RISK FACTORS")
print("==========================================")


# Sample patient information
# These are separate patient-level inputs.
# They are not part of the Kaggle dataset.

patient_age = 55

smoking = True

physically_active = False

bmi = 31

diabetes = False

high_blood_pressure = True

high_cholesterol = True


print("Age:", patient_age)

print("Smoking:", "Yes" if smoking else "No")

print(
    "Physical Activity:",
    "Yes" if physically_active else "No"
)

print("BMI:", bmi)

print(
    "Diabetes:",
    "Yes" if diabetes else "No"
)

print(
    "High Blood Pressure:",
    "Yes" if high_blood_pressure else "No"
)

print(
    "High Cholesterol:",
    "Yes" if high_cholesterol else "No"
)


# ==========================================
# 17. CALCULATE RISK FACTOR SCORE
# ==========================================

risk_factor_score = 0


if patient_age >= 50:
    risk_factor_score += 1


if smoking:
    risk_factor_score += 1


if not physically_active:
    risk_factor_score += 1


if bmi >= 30:
    risk_factor_score += 1


if diabetes:
    risk_factor_score += 1


if high_blood_pressure:
    risk_factor_score += 1


if high_cholesterol:
    risk_factor_score += 1


print("\nRisk Factor Score:")
print(risk_factor_score, "/ 7")


# ==========================================
# 18. GET DISEASE PROBABILITY
# ==========================================

top_disease = probability_table.iloc[0]["Disease"]

top_probability = float(
    probability_table.iloc[0]["Probability"]
)


# ==========================================
# 19. COMBINE RISK FACTORS + PROBABILITY
# ==========================================

# Convert disease probability into points.

if top_probability >= 0.70:

    probability_score = 3

elif top_probability >= 0.40:

    probability_score = 2

else:

    probability_score = 1


# Total project risk score

total_risk_score = (
    risk_factor_score +
    probability_score
)


# ==========================================
# 20. FINAL RISK LEVEL
# ==========================================

if total_risk_score >= 7:

    risk_level = "High"

elif total_risk_score >= 4:

    risk_level = "Medium"

else:

    risk_level = "Low"


print("\n==========================================")
print("FINAL RISK ASSESSMENT")
print("==========================================")

print("Predicted Disease:", top_disease)

print("Disease Probability:", top_probability)

print("Risk Factor Score:", risk_factor_score, "/ 7")

print("Probability Score:", probability_score, "/ 3")

print("Total Risk Score:", total_risk_score, "/ 10")

print("Final Risk Level:", risk_level)


# ==========================================
# 21. CREATE SQLITE DATABASE
# ==========================================

connection = sqlite3.connect(
    "disease_predictions.db"
)

cursor = connection.cursor()


# ==========================================
# 22. CREATE PATIENT PROFILE TABLE
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS patient_profiles (
    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name TEXT NOT NULL,
    age INTEGER,
    gender TEXT
)
""")


# ==========================================
# 23. CREATE PREDICTIONS TABLE
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    predicted_disease TEXT,
    probability REAL,
    FOREIGN KEY (patient_id)
        REFERENCES patient_profiles(patient_id)
)
""")


# ==========================================
# 24. CREATE RISK ASSESSMENTS TABLE
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS risk_assessments (
    risk_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    predicted_disease TEXT,
    probability REAL,
    risk_factor_score INTEGER,
    probability_score INTEGER,
    total_risk_score INTEGER,
    risk_level TEXT,
    FOREIGN KEY (patient_id)
        REFERENCES patient_profiles(patient_id)
)
""")


# ==========================================
# 25. CREATE SAMPLE PATIENT
# ==========================================

cursor.execute("""
INSERT INTO patient_profiles
(patient_name, age, gender)
VALUES (?, ?, ?)
""", (
    "Sample Patient",
    patient_age,
    "Female"
))


patient_id = cursor.lastrowid


# ==========================================
# 26. SAVE TOP DISEASE PREDICTIONS
# ==========================================

top_predictions = probability_table.head(5)


for _, row in top_predictions.iterrows():

    cursor.execute("""
    INSERT INTO predictions
    (patient_id, predicted_disease, probability)
    VALUES (?, ?, ?)
    """, (

        patient_id,

        row["Disease"],

        float(row["Probability"])

    ))


# ==========================================
# 27. SAVE RISK ASSESSMENT
# ==========================================

cursor.execute("""
INSERT INTO risk_assessments
(
    patient_id,
    predicted_disease,
    probability,
    risk_factor_score,
    probability_score,
    total_risk_score,
    risk_level
)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", (

    patient_id,

    top_disease,

    top_probability,

    risk_factor_score,

    probability_score,

    total_risk_score,

    risk_level

))


# ==========================================
# 28. SAVE DATABASE CHANGES
# ==========================================

connection.commit()


# ==========================================
# 29. DISPLAY SAVED PREDICTIONS
# ==========================================

print("\n==========================================")
print("SAVED PATIENT PREDICTIONS")
print("==========================================")


cursor.execute("""
SELECT
    patient_profiles.patient_id,
    patient_profiles.patient_name,
    predictions.predicted_disease,
    predictions.probability
FROM patient_profiles
JOIN predictions
ON patient_profiles.patient_id =
   predictions.patient_id
WHERE patient_profiles.patient_id = ?
""", (
    patient_id,
))


saved_predictions = cursor.fetchall()


for prediction in saved_predictions:

    print(prediction)


# ==========================================
# 30. DISPLAY SAVED RISK ASSESSMENT
# ==========================================

print("\n==========================================")
print("SAVED RISK ASSESSMENT")
print("==========================================")


cursor.execute("""
SELECT
    patient_id,
    predicted_disease,
    probability,
    risk_factor_score,
    probability_score,
    total_risk_score,
    risk_level
FROM risk_assessments
WHERE patient_id = ?
""", (
    patient_id,
))


saved_risk = cursor.fetchone()


print("Patient ID:", saved_risk[0])

print("Predicted Disease:", saved_risk[1])

print("Probability:", saved_risk[2])

print("Risk Factor Score:", saved_risk[3])

print("Probability Score:", saved_risk[4])

print("Total Risk Score:", saved_risk[5])

print("Risk Level:", saved_risk[6])


# ==========================================
# 31. CLOSE DATABASE
# ==========================================

connection.close()


print("\n==========================================")
print("DAY 3 COMPLETED SUCCESSFULLY!")
print("==========================================")