from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

DATABASE = "disease_predictions.db"


def get_database_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def home():
    return jsonify({
        "message": "Health Risk Report API is running"
    })


@app.route("/risk-report/<int:patient_id>")
def get_risk_report(patient_id):

    conn = get_database_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            p.patient_id,
            p.patient_name,
            p.age,
            p.gender,
            r.predicted_disease,
            r.probability,
            r.risk_factor_score,
            r.probability_score,
            r.total_risk_score,
            r.risk_level
        FROM patient_profiles p
        JOIN risk_assessments r
        ON p.patient_id = r.patient_id
        WHERE p.patient_id = ?
        ORDER BY r.risk_id DESC
        LIMIT 1
    """, (patient_id,))

    result = cursor.fetchone()

    conn.close()

    if result is None:
        return jsonify({
            "error": "Patient risk assessment not found"
        }), 404

    return jsonify({
        "patient_id": result["patient_id"],
        "patient_name": result["patient_name"],
        "age": result["age"],
        "gender": result["gender"],
        "predicted_disease": result["predicted_disease"],
        "disease_probability": result["probability"],
        "risk_factor_score": result["risk_factor_score"],
        "probability_score": result["probability_score"],
        "total_risk_score": result["total_risk_score"],
        "risk_level": result["risk_level"]
    })


if __name__ == "__main__":
    app.run(debug=True)