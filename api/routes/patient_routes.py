from flask import Blueprint, request, jsonify
from controllers.patient_controller import get_patient_details, get_lab_reports

patient_bp = Blueprint('patient', __name__, url_prefix='/patients')

@patient_bp.route('/<patient_id>', methods=['GET'])
def get_patient(patient_id):
    return jsonify(get_patient_details(patient_id))

@patient_bp.route('/<patient_id>/lab_reports', methods=['GET'])
def get_patient_lab_reports(patient_id):
    return jsonify(get_lab_reports(patient_id))
