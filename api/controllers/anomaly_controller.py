from flask import jsonify
from services.anomaly_service import detect_anomalies

def get_anomalies(patient_id, report_id):
    anomalies = detect_anomalies(patient_id, report_id)
    return jsonify(anomalies)

def get_anomalies(patient_id, report_id):
    # Logic to detect anomalies in a lab report
    return {"message": "get_anomalies not implemented"}
