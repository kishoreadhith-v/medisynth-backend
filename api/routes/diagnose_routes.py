from flask import Blueprint, request, jsonify
from api.controllers.diagnose_controller import diagnose_patient

diagnose_bp = Blueprint('diagnose', __name__, url_prefix='/patients/<patient_id>/lab_reports')

@diagnose_bp.route('/<report_id>/diagnoses', methods=['POST'])
def diagnose(patient_id, report_id):
    return jsonify(diagnose_patient(patient_id, report_id))
