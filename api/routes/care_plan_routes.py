from flask import Blueprint, request, jsonify
from controllers.care_plan_controller import generate_care_plan, get_meal_plan

care_plan_bp = Blueprint('care_plan', __name__, url_prefix='/patients')

@care_plan_bp.route('/<patient_id>/generate_care_plan', methods=['POST'])
def create_care_plan(patient_id):
    return jsonify(generate_care_plan(patient_id))

@care_plan_bp.route('/meal_plan', methods=['GET'])
def meal_plan():
    return jsonify(get_meal_plan(request.json))
