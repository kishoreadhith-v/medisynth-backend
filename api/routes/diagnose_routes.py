from flask import Blueprint, request, jsonify
from controllers.diagnose_controller import diagnose_patient

diagnose_bp = Blueprint('diagnose', __name__, url_prefix='/patients/<patient_id>/lab_reports/<report_id>')

@diagnose_bp.route('/diagnoses', methods=['POST'])
def diagnose(patient_id, report_id):
    return jsonify(diagnose_patient(patient_id, report_id))
