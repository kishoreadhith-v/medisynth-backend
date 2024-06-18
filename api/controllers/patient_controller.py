from flask import jsonify, request
from pymongo import MongoClient, UpdateOne
import os
import json
from dotenv import load_dotenv
import fitz  # PyMuPDF
import google.generativeai as genai
import re
from bson import ObjectId

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
                'lab_results': lab_results
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
