import google.generativeai as genai
from flask import jsonify, request
from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv
import os
import re

load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URI'))
db = client['dev-db']
patient_collection = db['patients']
careplan_collection = db['careplans']

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


def get_meal_plan(data):
    try:
        prompt = f"""
            you're a professional nutrition expert and you are trained to write meal plans for patients with various diseases and complications. generate a 5 meal-a-day meal plan for a patient with the following info about them: 
            {data}
            give json output, formatted as an array of 5 meals, give only the json object for easier parsing and formatting
            """
        
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
        
        return result


    except Exception as e:
        return {'error': str(e)}
