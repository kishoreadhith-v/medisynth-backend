from flask import Blueprint, request, jsonify
from controllers.care_plan_controller import generate_care_plan

care_plan_bp = Blueprint('care_plan', __name__, url_prefix='/patients/<patient_id>')

@care_plan_bp.route('/care_plans', methods=['POST'])
def care_plan(patient_id):
    return jsonify(generate_care_plan(patient_id))
