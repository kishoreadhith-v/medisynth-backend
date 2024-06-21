from flask import Blueprint, request, jsonify
from controllers.care_plan_controller import (generate_care_plan, get_meal_plan, det_criticality_score, ask_general, ask_patient_specific)

care_plan_bp = Blueprint('care_plan', __name__, url_prefix='/patients')

@care_plan_bp.route('/<patient_id>/generate_care_plan', methods=['POST'])
def create_care_plan(patient_id):
    return jsonify(generate_care_plan(patient_id))

@care_plan_bp.route('/meal_plan', methods=['GET'])
def meal_plan():
    return jsonify(get_meal_plan(request.json))

@care_plan_bp.route('/<patient_id>/csllm', methods=['GET'])
def get_criticality(patient_id):
    return jsonify(det_criticality_score(patient_id))

@care_plan_bp.route('/ask_general', methods=['POST'])
def ask_gen():
    query = request.json.get('query')
    return jsonify(ask_general(query))

@care_plan_bp.route('/ask_patient_specific/<patient_id>', methods=['POST'])
def ask_pat_spec(patient_id):
    query = request.json.get('query')
    return jsonify(ask_patient_specific(patient_id, query))
