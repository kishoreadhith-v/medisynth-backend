from flask import Blueprint, request, jsonify
from controllers.anomaly_controller import get_anomalies

anomaly_bp = Blueprint('anomaly', __name__, url_prefix='/patients/<patient_id>/lab_reports')

@anomaly_bp.route('/<report_id>/anomalies', methods=['GET'])
def detect_anomalies(patient_id, report_id):
    return jsonify(get_anomalies(patient_id, report_id))

@anomaly_bp.route('/anomalies', methods=['GET'])
def anomalies(patient_id, report_id):
    return get_anomalies(patient_id, report_id)
