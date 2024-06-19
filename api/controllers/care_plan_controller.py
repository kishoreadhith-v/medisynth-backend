import google.generativeai as genai
from flask import jsonify, request
from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv
import os

load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URI'))
db = client['dev-db']
patient_collection = db['patients']
careplan_collection = db['careplans']

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def generate_care_plan(patient_id):
    try:
        # Retrieve the patient information
        patient = patient_collection.find_one({'patient_id': patient_id})
        if not patient:
            return {'error': 'Patient not found'}
        
        prompt = f"""
        You are a medical professional trained to write individualized care plans for patients.
        Please generate a care plan for the following patient:
        {patient}
        the care plan must include the following:
        - Diagnosis brief
        - goals
        - interventions
        - evaluation
        - patient education
        - follow-up
        """

        # Interact with Gemini API
        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
        response = model.generate_content([prompt])

        # Extract the generated care plan
        response = response.candidates[0].content.parts[0].text.strip()

        # update the patient's care plan
        careplan_collection.update_one(
            {'patient_id': patient_id},
            {'$set': {'care_plan': response}}
        )

        return {'care_plan': response}
    
    except Exception as e:
        return {'error': str(e)}


