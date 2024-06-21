from flask import Blueprint, request, jsonify
from controllers.allocation_controller import create_resources_allocated_field, create_patients_assigned_field, create_staffs_assigned_field, create_resource, get_all_resources, get_resource_by_id, allocate_resource_to_patient, deallocate_resource_from_patient, assign_staff_to_patient, unassign_staff_from_patient

allocation_bp = Blueprint('allocation', __name__, url_prefix='/allocation')

@allocation_bp.route('/create_resources_allocated_field', methods=['POST'])
def create_resources_allocated():
    return create_resources_allocated_field()

@allocation_bp.route('/create_patients_assigned_field', methods=['POST'])
def create_patients_assigned():
    return create_patients_assigned_field()

@allocation_bp.route('/create_staffs_assigned_field', methods=['POST'])
def create_staffs_assigned():
    return create_staffs_assigned_field()

@allocation_bp.route('/create_resource', methods=['POST'])
def create_res():
    return create_resource(request.json)

@allocation_bp.route('/resources', methods=['GET'])
def resources():
    return get_all_resources()

@allocation_bp.route('/resources/<resource_id>', methods=['GET'])
def resource(resource_id):
    return get_resource_by_id(resource_id)

@allocation_bp.route('/allocate_resource_to_patient/<patient_id>/<resource_id>', methods=['POST'])
def allocate_resource(patient_id, resource_id):
    return allocate_resource_to_patient(patient_id, resource_id)

@allocation_bp.route('/deallocate_resource_from_patient/<patient_id>/<resource_id>', methods=['POST'])
def deallocate_resource(patient_id, resource_id):
    return deallocate_resource_from_patient(patient_id, resource_id)

@allocation_bp.route('/assign_staff_to_patient/<patient_id>/<staff_id>', methods=['POST'])
def assign_staff(patient_id, staff_id):
    return assign_staff_to_patient(patient_id, staff_id)

@allocation_bp.route('/unassign_staff_from_patient/<patient_id>/<staff_id>', methods=['POST'])
def unassign_staff(patient_id, staff_id):
    return unassign_staff_from_patient(patient_id, staff_id)