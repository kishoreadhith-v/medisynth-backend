from flask import jsonify, request
from pymongo import MongoClient, UpdateOne
import os
import json
from dotenv import load_dotenv
import fitz  # PyMuPDF
import google.generativeai as genai
import re
from bson import ObjectId

from controllers.allocation_controller import deallocate_resource_from_patient, unassign_staff_from_patient
load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URI'))
db = client['dev-db']
patient_collection = db['patients']

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def split_and_load_ejson(text):
    # Regular expression to find triple backticks with 'json' inside
    pattern = r"```json(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        # Extract JSON content from the match
        json_content = match.group(1).strip()
        
        try:
            # Attempt to parse the extracted JSON content
            data = json.loads(json_content)
            return data
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON format in extracted content: {str(e)}")
            return None
    else:
        print("Error: No valid JSON block found using triple backticks")
        return None

def extract_text_from_pdf(filepath):
    doc = fitz.open(filepath)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def upload_lab_report(patient_id, file):
    try:
        # Save the file
        filename = file.filename
        filepath = os.path.join('uploads', filename)
        file.save(filepath)

        # Extract text from the PDF
        pdf_text = extract_text_from_pdf(filepath)

        # Create prompt with extracted text
        prompt = f"""Extract patient info, anomalies, vitals and lab results from the following lab report text: 
        {pdf_text}. 
        Output format:
        {{
          "patient_info": {{
            "name": "<name>",
            "age": <age>,
            "gender": "<gender>",
            "lab_no": <lab_no>,
            "collected_at": "<collected_at>",
            "reported_at": "<reported_at>",
            "lab": "<lab>",
            "lab_address": "<lab_address>"
          }},
          "anomalies": [
            {{
              "test_name": "<test_name>",
              "result": <result_value>,
              "reference_range": "<reference_range>",
              "unit": "<unit>"
            }}
            // Add more anomalies as needed
          ],
          "vitals": {{
            "<vital_name>": <vital_value> // as many vitals there are
          }},
          "lab_results": {{
            "<lab_result_name>": <lab_result_value> // as many lab results there are
          }}
        }} 
        the above format is a template, please fill in the values. I need the following requirements to be satisfied: 
        1. for the anomalous values include only the ones in which the value is out of the reference range 
        2. There should be the patient info, anomalies, vitals sections, and lab results sections 
        3. The vitals section would contain the vitals of a person like the blood pressure, heart rate, and other things. 
        4. The lab reports section would contain other results that do not come under vitals 
        5. I need the naming in the JSON to match a few formats I have 
        6. The naming should be as follows: ['gender', 'smoking_history', 'age', 'hypertension', 'heart_disease', 'bmi', 'HbA1c_level', 'blood_glucose_level', 'Sex', 'ChestPainType', 'RestingECG', 'ExerciseAngina', 'ST_Slope', 'Age', 'RestingBP', 'Cholesterol', 'MaxHR', 'Oldpeak', 'gender', 'ever_married', 'work_type', 'Residence_type', 'smoking_status', 'age', 'hypertension', 'heart_disease', 'avg_glucose_level', 'bmi'] 
        if any readings from the report indicate the above value but are named differently, rename them to match the above names."""

        # Interact with Gemini API
        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
        response = model.generate_content([prompt])

        # Parse JSON from the response text using regex-based function
        response_text = response.candidates[0].content.parts[0].text.strip()
        print(f"Response from Gemini API: {response_text}")

        if not response_text:
            return {'error': 'Empty response from API'}

        # Use regex-based function to parse JSON response
        result = split_and_load_ejson(response_text)

        if not result:
            return {'error': 'Failed to parse JSON response'}

        print(f"Extracted JSON: {result}")

        # Extract patient info, anomalies, vitals, and lab results from parsed JSON
        patient_info = result.get('patient_info', {})
        anomalies = result.get('anomalies', [])
        vitals = result.get('vitals', {})
        lab_results = result.get('lab_results', {})

        # Retrieve the existing patient data
        existing_patient_data = patient_collection.find_one({'patient_id': patient_id})
        
        if existing_patient_data:
            # Update existing patient data with new values
            existing_patient_data['patient_info'] = {**existing_patient_data.get('patient_info', {}), **patient_info}
            existing_patient_data['anomalies'] = existing_patient_data.get('anomalies', []) + anomalies
            existing_patient_data['vitals'] = {**existing_patient_data.get('vitals', {}), **vitals}
            existing_patient_data['lab_results'] = {**existing_patient_data.get('lab_results', {}), **lab_results}
        else:
            # Create new patient data if none exists
            existing_patient_data = {
                'patient_id': patient_id,
                'patient_info': patient_info,
                'anomalies': anomalies,
                'vitals': vitals,
                'lab_results': lab_results,
                'staffs_assigned': [],
                'resources_allocated': [],
                'notifications': [],
                'isEmergency': False,
                'takenPills': True
            }

        # Store updated patient data in MongoDB
        patient_collection.update_one({'patient_id': patient_id}, {'$set': existing_patient_data}, upsert=True)

        # Convert ObjectId to string before returning
        return convert_objectid_to_str(existing_patient_data)

    except Exception as e:
        return {'error': str(e)}

def get_patient_details(patient_id):
    patient = patient_collection.find_one({'patient_id': patient_id})
    if patient:
        # Convert ObjectId to string before returning
        return convert_objectid_to_str(patient)
    else:
        return {'error': 'Patient not found'}

def get_lab_reports(patient_id):
    patient = patient_collection.find_one({'patient_id': patient_id})
    if patient:
        # Convert ObjectId to string before returning
        return convert_objectid_to_str(patient.get('anomalies', []))
    else:
        return {'error': 'Patient not found or no lab reports available'}

from bson import ObjectId

def convert_objectid_to_str(data):
    if isinstance(data, list):
        return [convert_objectid_to_str(item) for item in data]
    elif isinstance(data, dict):
        return {key: convert_objectid_to_str(value) for key, value in data.items()}
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data


def manual_input(patient_id, data):
    # add data to the manual_data field, do not overwrite existing data
    patient = patient_collection.find_one({'patient_id': patient_id})
    if patient:
        existing_manual_data = patient.get('manual_data', {})
        update_query = {'patient_id': patient_id}
        # if the key already exists, it will be overwritten
        update_data = {'$set': {'manual_data': {**existing_manual_data, **data}}}
        
        # Using update_one to update the document
        patient_collection.update_one(update_query, update_data)
        
        return get_patient_details(patient_id)
    else:
        return {'error': 'Patient not found'}


# cricality score

def calculate_criticality_score(patient_data):
    # Define weights for each category based on clinical judgment
    weights = {
        'VS': 20,
        'LR': 15,
        'MH': 10,
        'S': 15,
        'RF': 10,
        'DT': 15,
        'FS': 5,
        'MU': 10
    }

    # Normalization functions for each input variable
    def normalize_bp(bp):
        return (bp - 90) / (180 - 90) * 10

    def normalize_hr(hr):
        return (hr - 60) / (200 - 60) * 10

    def normalize_binary(value, positive='Y'):
        return 10 if value == positive else 0

    def normalize_lab(value, min_val, max_val):
        if min_val == max_val:
            return 0
        return (value - min_val) / (max_val - min_val) * 10

    def normalize_age(age):
        return (age - 20) / (80 - 20) * 10

    def normalize_static(value, mapping):
        return mapping.get(value, 0)

    # Get values safely from the patient_data with default fallbacks
    manual_data = patient_data.get('manual_data', {})
    lab_results = patient_data.get('lab_results', {})
    vitals = patient_data.get('vitals', {})
    anomalies = patient_data.get('anomalies', [])
    patient_info = patient_data.get('patient_info', {})

    # Vital Signs (VS)
    vs_score = (
        normalize_bp(manual_data.get('RestingBP', 120)) * 0.33 +
        normalize_hr(manual_data.get('MaxHR', 100)) * 0.33 +
        normalize_binary(manual_data.get('ExerciseAngina', 'N')) * 0.33
    )

    # Lab Results (LR)
    hemoglobin = lab_results.get('Hemoglobin', 15)
    platelet_count = lab_results.get('Platelet Count', 200)
    tlc = lab_results.get('Total Leukocyte Count  (TLC)', 8)
    rdw = next((item['result'] for item in anomalies if item['test_name'] == 'Red Cell Distribution Width (RDW)'), 12)
    mpv = next((item['result'] for item in anomalies if item['test_name'] == 'Mean Platelet Volume'), 10)

    lr_score = (
        normalize_lab(hemoglobin, 12, 18) * 0.2 +
        normalize_lab(platelet_count, 150, 450) * 0.2 +
        normalize_lab(tlc, 4, 11) * 0.2 +
        normalize_lab(rdw, 11.60, 14.00) * 0.2 +
        normalize_lab(mpv, 6.5, 12.0) * 0.2
    )

    # Medical History (MH)
    cholesterol = manual_data.get('Cholesterol', 200)
    mh_score = (
        normalize_lab(cholesterol, 150, 300) * 0.5 +
        0  # FastingBS is not provided in numerical form
    )

    # Symptoms (S)
    chest_pain_mapping = {'ATA': 25, 'NAP': 50, 'ASY': 75, 'TA': 100}
    chest_pain_type = vitals.get('ChestPainType', 'ATA')
    oldpeak = manual_data.get('Oldpeak', 0)

    s_score = (
        normalize_static(chest_pain_type, chest_pain_mapping) * 0.5 +
        normalize_lab(oldpeak, 0, 6) * 0.5
    )

    # Risk Factors (RF)
    age = patient_info.get('age', 50)
    rf_score = (
        normalize_age(age) * 0.5 +
        50  # Assuming 50 for Male as mentioned
    )

    # Diagnostic Tests (DT)
    resting_ecg_mapping = {'Normal': 0, 'Abnormal': 100}
    st_slope_mapping = {'Up': 0, 'Flat': 50, 'Down': 100}
    resting_ecg = manual_data.get('RestingECG', 'Normal')
    st_slope = manual_data.get('ST_Slope', 'Up')

    dt_score = (
        normalize_static(resting_ecg, resting_ecg_mapping) * 0.5 +
        normalize_static(st_slope, st_slope_mapping) * 0.5
    )

    # Functional Status (FS)
    fs_score = 0  # No data provided

    # Medication Use (MU)
    mu_score = 0  # No data provided

    # Calculate the final criticality score
    weighted_sum = (
        (weights['VS'] * vs_score) +
        (weights['LR'] * lr_score) +
        (weights['MH'] * mh_score) +
        (weights['S'] * s_score) +
        (weights['RF'] * rf_score) +
        (weights['DT'] * dt_score) +
        (weights['FS'] * fs_score) +
        (weights['MU'] * mu_score)
    )

    # Normalize the weighted sum to a 0-10 scale
    max_possible_score = sum(weights.values())  # Max score if all components are at their highest (100)
    criticality_score = (weighted_sum / max_possible_score)

    return criticality_score


def get_criticality_score(patient_id):
    patient_data = patient_collection.find_one({'patient_id': patient_id})
    if patient_data:
        criticality_score = calculate_criticality_score(patient_data)
        # update the patient's criticality score
        patient_collection.update_one(
            {'patient_id': patient_id},
            {'$set': {'criticality_score': criticality_score}}
        )
        return {'criticality_score': criticality_score}
    else:
        return {'error': 'Patient not found'}
    

# remove patient from the system, deallocate resources and staffs assigned
def remove_patient(patient_id):
    # deallocate resources
    patient = patient_collection.find_one({'patient_id': patient_id})
    if patient:
        resources_allocated = patient.get('resources_allocated', [])
        for resource_id in resources_allocated:
            deallocate_resource_from_patient(patient_id, resource_id)
        # unassign staffs
        staffs_assigned = patient.get('staffs_assigned', [])
        for staff_id in staffs_assigned:
            unassign_staff_from_patient(patient_id, staff_id)
        # delete the patient
        patient_collection.delete_one({'patient_id': patient_id})
        return {'message': 'Patient removed successfully'}
    else:
        return {'error': 'Patient not found'}
    
# get all patients
def get_all_patients():
    patients = patient_collection.find()
    return convert_objectid_to_str(list(patients))

# get patients assigned to a staff, staff_id in staffs_assigned array
def get_patients_assigned_to_staff(staff_id):
    patients = patient_collection.find({'staffs_assigned': staff_id})
    return convert_objectid_to_str(list(patients))