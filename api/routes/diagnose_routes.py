from flask import Blueprint, request, jsonify
from controllers.diagnose_controller import predict_heart, heart_missing_columns, predict_diabetes, diabetes_missing_columns, predict_stroke, stroke_missing_columns

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

@diagnose_bp.route('/predict_diabetes', methods=['POST'])
def diabetes_predictions(patient_id):
    return jsonify(predict_diabetes(patient_id))

@diagnose_bp.route('/diabetes_missing_columns', methods=['GET'])
def diabetes_missing(patient_id):
    return diabetes_missing_columns(patient_id)

@diagnose_bp.route('/predict_stroke', methods=['POST'])
def stroke_predictions(patient_id):
    return jsonify(predict_stroke(patient_id))

@diagnose_bp.route('/stroke_missing_columns', methods=['GET'])
def stroke_missing(patient_id):
    return stroke_missing_columns(patient_id)