from flask import Blueprint, request, jsonify
from api.controllers.diagnose_controller import predict_heart, heart_missing_columns

diagnose_bp = Blueprint('diagnose', __name__, url_prefix='/patients/<patient_id>')

# @diagnose_bp.route('/<report_id>/diagnoses', methods=['POST'])
# def diagnose(patient_id, report_id):
#     return jsonify(diagnose_patient(patient_id, report_id))

@diagnose_bp.route('/predict_heart', methods=['POST'])
def predictions(patient_id):
    return jsonify(predict_heart(patient_id))

@diagnose_bp.route('/heart_missing_columns', methods=['GET'])
def missing(patient_id):
    return heart_missing_columns(patient_id)