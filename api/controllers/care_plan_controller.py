import json
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

        give the output as a json object with the following format:
        {{
            "diagnosis": "diagnosis brief",
            "goals": "goals",
            "interventions": "interventions",
            "evaluation": "evaluation",
            "patient_education": "patient education",
            "follow_up": "follow-up"
        }}
        give only the json object for easier parsing and formatting, no need for markdown or any other formatting inside the json too
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
        response = split_and_load_ejson(response_text)

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
            output example for format(note this is only for an example, the actual output should be based on the patient's info provided in the prompt):
            [
                {
                "meal_type": "the type of meal(eg. breakfast, mid-morning snack, lunch, afternoon snack, dinner)",
                "description": "the description of the meal",
                "food_items": "an array of food items in the meal",
                }, "other 4 meals follow the same format" 
            ]
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

# generate a criticality score for patient using a formula and gemini api
def det_criticality_score(patient_id):
    patient_data = patient_collection.find_one({'patient_id': patient_id})
    if not patient_data:
        return {'error': 'Patient not found'}
    
    prompt = f"""
    You are a medical professional trained to calculate the criticality score for patients based on their medical history and current health status.
    Please calculate the criticality score for the following patient:
    {patient_data}
    the criticality score must be calculated using the following formula:

    ### Criticality Score Calculation

    1. **Normalization Functions:**
    - **Blood Pressure (BP):** `normalize_bp = (bp - 90) / (180 - 90) * 100`
    - **Heart Rate (HR):** `normalize_hr = (hr - 60) / (200 - 60) * 100`
    - **Binary Values:** `normalize_binary = 100 if positive else 0`
    - **Laboratory Values:** `normalize_lab = (value - min_val) / (max_val - min_val) * 100`
    - **Age:** `normalize_age = (age - 20) / (80 - 20) * 100`
    - **Static Mappings:** `normalize_static = mapping[value]`

    2. **Category Scores:**
    - **Vital Signs (VS):**
        vs_score = (
        normalize_bp(bp) * 0.33 +
        normalize_hr(hr) * 0.33 +
        normalize_binary(exercise_angina) * 0.33
        )
    - **Lab Results (LR):**
        lr_score = (
        normalize_lab(hemoglobin, 12, 18) * 0.2 +
        normalize_lab(platelet_count, 150, 450) * 0.2 +
        normalize_lab(tlc, 4, 11) * 0.2 +
        normalize_lab(rdw, 11.60, 14.00) * 0.2 +
        normalize_lab(mpv, 6.5, 12.0) * 0.2
        )
    - **Medical History (MH):**
        mh_score = (
        normalize_lab(cholesterol, 150, 300) * 0.5
        )
    - **Symptoms (S):**
        chest_pain_mapping = {{'ATA': 25, 'NAP': 50, 'ASY': 75, 'TA': 100}}
        s_score = (
        normalize_static(chest_pain_type, chest_pain_mapping) * 0.5 +
        normalize_lab(oldpeak, 0, 6) * 0.5
        )
    - **Risk Factors (RF):**
        rf_score = (
        normalize_age(age) * 0.5 +
        50  # Assuming 50 for male as default
        )
    - **Diagnostic Tests (DT):**
        resting_ecg_mapping = {{'Normal': 0, 'Abnormal': 100}}
        st_slope_mapping = {{'Up': 0, 'Flat': 50, 'Down': 100}}
        dt_score = (
        normalize_static(resting_ecg, resting_ecg_mapping) * 0.5 +
        normalize_static(st_slope, st_slope_mapping) * 0.5
        )
    - **Functional Status (FS) and Medication Use (MU):**
        fs_score = 0  # If no data is provided
        mu_score = 0  # If no data is provided

    3. **Weights:**
    weights = {{
        'VS': 20,
        'LR': 15,
        'MH': 10,
        'S': 15,
        'RF': 10,
        'DT': 15,
        'FS': 5,
        'MU': 10
    }}

    4. **Weighted Sum:**
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

    5. **Criticality Score:**
    max_possible_score = 10000  # Max score if all components are at their highest (100)
    criticality_score = (weighted_sum / max_possible_score) * 10

    using this, generate a criticality score for the patient from 0 to 10, make it a float number with 2 decimal places
    make the score sensible and based on the patient's data provided in the prompt and based on the scale of 0 to 10
    give the output as a json object with the following format:
    {{
        "criticality_score": "the calculated criticality score",
        "criticality_level": "the level of criticality based on the score (e.g., low (0 to 3), medium (3 to 7), high (7 to 10))"
    }}
    give only the json object for easier parsing and formatting, no need for markdown or any other formatting inside the json too
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
    
    # update the patient's criticality score
    patient_collection.update_one(
        {'patient_id': patient_id},
        {'$set': {'criticality_score': result['criticality_score']}}
    )
    patient_collection.update_one(
        {'patient_id': patient_id},
        {'$set': {'criticality_level': result['criticality_level']}}
    )
    return result

# ask gemini a question based on a patient's data
def ask_patient_specific(patient_id, query):
    patient_data = patient_collection.find_one({'patient_id': patient_id})
    if not patient_data:
        return {'error': 'Patient not found'}
    
    prompt = f"""
    You are a medical professional trained to answer medical questions based on a patient's specific information.
    Please answer the following question based on the patient's data provided below:
    {patient_data}
    Question: {query}
    Provide a detailed and accurate response to the question.
    give the output as a json object with the following format:
    {{
        "answer": "the detailed answer to the question"
    }}
    give only the json object for easier parsing and formatting, no need for markdown or any other formatting inside the json too
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
    if result == None:
        result = json.loads(response_text)

    return result

# ask gemini a general medical question
def ask_general(query):
    prompt = f"""
    You are a medical professional trained to answer general medical questions.
    Please answer the following general medical question:
    {query}
    Provide a detailed and accurate response to the question.
    give the output as a json object with the following format:
    {{
        "answer": "the detailed answer to the question"
    }}
    give only the json object for easier parsing and formatting, no need for markdown or any other formatting inside the json too
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
    result = json.loads(response_text)

    return result



