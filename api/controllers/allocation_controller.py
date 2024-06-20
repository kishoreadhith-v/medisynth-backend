from pymongo import MongoClient
from flask import jsonify
from dotenv import load_dotenv
import os

load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URI'))
db = client['dev-db']
patient_collection = db['patients']
resource_collection = db['resources']
user_collection = db['users']

# Create resources_allocated and staffs_assigned fields for all patients if they don't exist already
def create_resources_allocated_field():
    patients = patient_collection.find()
    for patient in patients:
        if 'resources_allocated' not in patient:
            patient_collection.update_one({'patient_id': patient.get('patient_id')}, {'$set': {'resources_allocated': []}})
        if 'staffs_assigned' not in patient:
            patient_collection.update_one({'patient_id': patient.get('patient_id')}, {'$set': {'staffs_assigned': []}})
    return jsonify({'message': 'Resources allocated and staffs assigned fields created successfully'}), 200

# Create staffs_assigned field for all users if it doesn't exist already
def create_staffs_assigned_field():
    patients = patient_collection.find()
    for patient in patients:
        if 'staffs_assigned' not in patient:
            patient_collection.update({'patient_id': patient.get('patient_id')}, {'$set': {'staffs_assigned': []}})
    return jsonify({'message': 'Staffs assigned field created successfully'}), 200

# Create patients_assigned field for all users if it doesn't exist already
def create_patients_assigned_field():
    users = user_collection.find()
    for user in users:
        if 'patients_assigned' not in user:
            user_collection.update_one({'user_id': user.get('user_id')}, {'$set': {'patients_assigned': []}})
    return jsonify({'message': 'Patients assigned field created successfully'}), 200

# Create resource
def create_resource(data):
    resource = {
        'name': data.get('name'),
        'resource_id': data.get('resource_id'),
        'description': data.get('description'),
        'type': data.get('type'),
        'total': data.get('total'),
        'available': data.get('available'), 
        'allocated_patients': []
    }
    existing_resource = resource_collection.find_one({'resource_id': data.get('resource_id')})
    if existing_resource:
        return jsonify({'error': 'Resource already exists'}), 301
    resource_collection.insert_one(resource)
    return jsonify({'message': 'Resource created successfully'}), 201

# Get all resources
def get_all_resources():
    resources = list(resource_collection.find({}, {'_id': 0}))
    return jsonify(resources), 200

# Get resource by id
def get_resource_by_id(resource_id):
    resource = resource_collection.find_one({'resource_id': resource_id}, {'_id': 0})
    if not resource:
        return jsonify({'error': 'Resource not found'}), 404
    return jsonify(resource), 200

# Allocate resource to patient
def allocate_resource_to_patient(patient_id, resource_id):
    patient = patient_collection.find_one({'patient_id': patient_id})
    resource = resource_collection.find_one({'resource_id': resource_id})
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    if not resource:
        return jsonify({'error': 'Resource not found'}), 404
    if resource.get('available') == 0:
        return jsonify({'error': 'Resource not available'}), 400
    resource_collection.update_one({'resource_id': resource_id}, {'$inc': {'available': -1}})
    resource_collection.update_one({'resource_id': resource_id}, {'$push': {'allocated_patients': patient_id}})
    patient_collection.update_one({'patient_id': patient_id}, {'$push': {'resources_allocated': resource_id}})
    return jsonify({'message': 'Resource allocated to patient successfully'}), 200

# Deallocate resource from patient
def deallocate_resource_from_patient(patient_id, resource_id):
    patient = patient_collection.find_one({'patient_id': patient_id})
    resource = resource_collection.find_one({'resource_id': resource_id})
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    if not resource:
        return jsonify({'error': 'Resource not found'}), 404
    if patient_id not in resource.get('allocated_patients') or resource_id not in patient.get('resources_allocated'):
        return jsonify({'error': 'Resource not allocated to patient'}), 400
    resource_collection.update_one({'resource_id': resource_id}, {'$inc': {'available': 1}})
    resource_collection.update_one({'resource_id': resource_id}, {'$pull': {'allocated_patients': patient_id}})
    patient_collection.update_one({'patient_id': patient_id}, {'$pull': {'resources_allocated': resource_id}})
    return jsonify({'message': 'Resource deallocated from patient successfully'}), 200

# Assign staff to patient
def assign_staff_to_patient(patient_id, staff_id):
    patient = patient_collection.find_one({'patient_id': patient_id})
    user = user_collection.find_one({'staff_id': staff_id})
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    if not user:
        return jsonify({'error': 'Staff not found'}), 404
    if staff_id in patient.get('staffs_assigned'):
        return jsonify({'error': 'Staff already assigned to patient'}), 400
    user_collection.update_one({'user_id': staff_id}, {'$push': {'patients_assigned': patient_id}})
    patient_collection.update_one({'patient_id': patient_id}, {'$push': {'staffs_assigned': staff_id}})
    return jsonify({'message': 'Staff assigned to patient successfully'}), 200

# Unassign staff from patient
def unassign_staff_from_patient(patient_id, staff_id):
    patient = patient_collection.find_one({'patient_id': patient_id})
    user = user_collection.find_one({'staff_id': staff_id})
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    if not user:
        return jsonify({'error': 'Staff not found'}), 404
    if staff_id not in patient.get('staffs_assigned'):
        return jsonify({'error': 'Staff not assigned to patient'}), 400
    user_collection.update_one({'user_id': staff_id}, {'$pull': {'patients_assigned': patient_id}})
    patient_collection.update_one({'patient_id': patient_id}, {'$pull': {'staffs_assigned': staff_id}})
    return jsonify({'message': 'Staff unassigned from patient successfully'}), 200
