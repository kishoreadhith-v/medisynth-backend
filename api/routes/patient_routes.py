from flask import Blueprint, request, jsonify
from controllers.patient_controller import get_patient_details, get_lab_reports, upload_lab_report, manual_input, get_criticality_score

patient_bp = Blueprint('patient', __name__, url_prefix='/patients')

@patient_bp.route('/<patient_id>', methods=['GET'])
def get_patient(patient_id):
    return jsonify(get_patient_details(patient_id))

@patient_bp.route('/<patient_id>/lab_reports', methods=['GET'])
def get_patient_lab_reports(patient_id):
    return jsonify(get_lab_reports(patient_id))

@patient_bp.route('/<patient_id>/upload_lab_report', methods=['POST'])
def upload_patient_lab_report(patient_id):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    return jsonify(upload_lab_report(patient_id, file))

@patient_bp.route('/<patient_id>/manual_input', methods=['POST'])
def manual_input_patient(patient_id):
    data = request.json
    return jsonify(manual_input(patient_id, data))

@patient_bp.route('/<patient_id>/criticality_score', methods=['GET'])
def get_criticality(patient_id):
    return jsonify(get_criticality_score(patient_id))