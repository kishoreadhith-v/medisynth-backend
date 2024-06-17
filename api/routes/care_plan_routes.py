from flask import Blueprint, request, jsonify
from api.controllers.care_plan_controller import generate_care_plan

care_plan_bp = Blueprint('care_plan', __name__, url_prefix='/patients')

@care_plan_bp.route('/<patient_id>/care_plans', methods=['POST'])
def create_care_plan(patient_id):
    return jsonify(generate_care_plan(patient_id))
