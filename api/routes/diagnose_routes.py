from flask import Blueprint, request, jsonify
from api.controllers.diagnose_controller import predict

diagnose_bp = Blueprint('diagnose', __name__, url_prefix='/patients/<patient_id>')

# @diagnose_bp.route('/<report_id>/diagnoses', methods=['POST'])
# def diagnose(patient_id, report_id):
#     return jsonify(diagnose_patient(patient_id, report_id))

@diagnose_bp.route('/predict', methods=['POST'])
def predictions(patient_id):
    return jsonify(predict(patient_id))