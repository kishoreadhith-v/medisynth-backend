from flask import Flask, jsonify
from pymongo import MongoClient
import joblib
import pandas as pd
from dotenv import load_dotenv
import os
import numpy as np


load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URI'))
db = client['dev-db']
patient_collection = db['patients']

# model columns

heart_model_columns = {'Age': 'numerical', 'Sex': ['M', 'F'], 'ChestPainType': ['ATA', 'NAP', 'ASY', 'TA'], 'RestingBP': 'numerical', 'Cholesterol': 'numerical', 'FastingBS': 'numerical', 'RestingECG': ['Normal', 'ST', 'LVH'], 'MaxHR': 'numerical', 'ExerciseAngina': ['N', 'Y'], 'Oldpeak': 'numerical', 'ST_Slope': ['Up', 'Flat', 'Down']}
stroke_model_columns = {'gender': ['Male', 'Female', 'Other'], 'age': 'numerical', 'hypertension': [0, 1], 'heart_disease': [1, 0], 'ever_married': ['Yes', 'No'], 'work_type': ['Private', 'Self-employed', 'Govt_job', 'children', 'Never_worked'], 'Residence_type': ['Urban', 'Rural'], 'avg_glucose_level': 'numerical', 'bmi': 'numerical', 'smoking_status': ['formerly smoked', 'never smoked', 'smokes', 'Unknown']}
diabetes_model_columns = {'gender': ['Female', 'Male', 'Other'], 'age': 'numerical', 'hypertension': [0, 1], 'heart_disease': [1, 0], 'smoking_history': ['never', 'No Info', 'current', 'former', 'ever', 'not current'], 'bmi': 'numerical', 'HbA1c_level': 'numerical', 'blood_glucose_level': 'numerical'}

# Functions
def fetch_patient_data(patient_id):
    patient_data = patient_collection.find_one({'patient_id': patient_id})
    if not patient_data:
        return None
    # combine lab results, patint info and vitals
    lab_results = patient_data.get('lab_results', {})
    vitals = patient_data.get('vitals', {})
    patient_info = patient_data.get('patient_info', {})
    manual_data = patient_data.get('manual_data', {})
    data = {**lab_results, **vitals, **patient_info, **manual_data}
    return data


def heart_missing_columns(patient_id):
    patient_data = fetch_patient_data(patient_id)
    if not patient_data:
        return jsonify({'error': 'Patient not found'}), 304
    patient_data['Age'] = patient_data.get('age', 0)
    gender = patient_data['gender']
    if gender == 'Male' or gender == 'male' or gender == 'M':
        patient_data['Sex'] = 'M'
    else:
        patient_data['Sex'] = 'F'

    # check if each column is present in the patient data, if category, check if the value is in the category list, if not, add to missing columns
    missing_columns = {}
    for column, value in heart_model_columns.items():
        if column not in patient_data or patient_data[column] is None:
            missing_columns[column] = value
        elif isinstance(value, list) and patient_data[column] not in value:
            missing_columns[column] = value

    return missing_columns

def predict_heart(patient_id):
    patient_data = fetch_patient_data(patient_id)
    if not patient_data:
        return jsonify({'error': 'Patient not found'}), 304
    
    patient_data['Age'] = patient_data.get('age', 0)
    gender = patient_data.get('gender', 'M')
    if gender in ['Male', 'male', 'M']:
        patient_data['Sex'] = 'M'
    else:
        patient_data['Sex'] = 'F'
    
    # get only the columns needed for the model
    heart_data = {key: patient_data[key] for key in heart_model_columns.keys()}
    
    # load the model
    heart_model = joblib.load('models/heart_rf_model.pkl')

    numerical_features = ['Age', 'RestingBP', 'Cholesterol', 'FastingBS', 'MaxHR', 'Oldpeak']
    categorical_features = ['Sex', 'ChestPainType', 'RestingECG', 'ExerciseAngina', 'ST_Slope']

    expected_columns = numerical_features + categorical_features

    new_data = pd.DataFrame([heart_data])
    new_data = new_data.reindex(columns=expected_columns, fill_value=0)

    prediction = heart_model.predict(new_data)
    prediction_proba = heart_model.predict_proba(new_data)

    # Convert numpy types to native Python types
    heart_prediction = int(prediction[0]) if isinstance(prediction[0], np.integer) else prediction[0]
    heart_confidence = float(max(prediction_proba[0])) if isinstance(max(prediction_proba[0]), np.floating) else max(prediction_proba[0])

    # update patient data with prediction
    patient_collection.update_one(
        {'patient_id': patient_id},
        {'$set': {'heart_failure_prediction': heart_prediction, 'heart_failure_prediction_confidence': heart_confidence}}
    )

    return {'prediction': heart_prediction, 'confidence': heart_confidence}

def stroke_missing_columns(patient_id):
    patient_data = fetch_patient_data(patient_id)
    if not patient_data:
        return jsonify({'error': 'Patient not found'}), 304
    
    gender = patient_data.get('gender', 'Male')
    if gender in ['Male', 'male', 'M']:
        patient_data['gender'] = 'Male'
    else:
        patient_data['gender'] = 'Female'

    missing_columns = {}
    for column, value in stroke_model_columns.items():
        if column not in patient_data or patient_data[column] is None:
            missing_columns[column] = value
        elif isinstance(value, list) and patient_data[column] not in value:
            missing_columns[column] = value

    return missing_columns

def predict_stroke(patient_id):
    patient_data = fetch_patient_data(patient_id)
    if not patient_data:
        return jsonify({'error': 'Patient not found'}), 304

    # get only the columns needed for the model
    stroke_data = {key: patient_data[key] for key in stroke_model_columns.keys()}
    
    # load the model
    stroke_model = joblib.load('models/stroke_rf_model.pkl')

    categorical_features=['gender', 'ever_married', 'work_type', 'Residence_type', 'smoking_status']
    numerical_features=['age', 'hypertension', 'heart_disease', 'avg_glucose_level', 'bmi']

    expected_columns = numerical_features + categorical_features

    new_data = pd.DataFrame([stroke_data])

    new_data = new_data.reindex(columns=expected_columns, fill_value=0)

    prediction = stroke_model.predict(new_data)
    prediction_proba = stroke_model.predict_proba(new_data)

    # Convert numpy types to native Python types
    stroke_prediction = int(prediction[0]) if isinstance(prediction[0], np.integer) else prediction[0]
    stroke_confidence = float(max(prediction_proba[0])) if isinstance(max(prediction_proba[0]), np.floating) else max(prediction_proba[0])

    # update patient data with prediction
    patient_collection.update_one(
        {'patient_id': patient_id},
        {'$set': {'stroke_prediction': stroke_prediction, 'stroke_prediction_confidence': stroke_confidence}}
    )

    return {'prediction': stroke_prediction, 'confidence': stroke_confidence}

def diabetes_missing_columns(patient_id):
    patient_data = fetch_patient_data(patient_id)
    if not patient_data:
        return jsonify({'error': 'Patient not found'}), 304
    
    gender = patient_data.get('gender', 'Male')
    if gender in ['Male', 'male', 'M']:
        patient_data['gender'] = 'Male'
    else:
        patient_data['gender'] = 'Female'

    missing_columns = {}
    for column, value in diabetes_model_columns.items():
        if column not in patient_data or patient_data[column] is None:
            missing_columns[column] = value
        elif isinstance(value, list) and patient_data[column] not in value:
            missing_columns[column] = value

    return missing_columns

def predict_diabetes(patient_id):
    patient_data = fetch_patient_data(patient_id)
    if not patient_data:
        return jsonify({'error': 'Patient not found'}), 304

    # get only the columns needed for the model
    diabetes_data = {key: patient_data[key] for key in diabetes_model_columns.keys()}
    
    # load the model
    diabetes_model = joblib.load('models/diabetes_rf_model.pkl')

    categorical_features=['gender', 'smoking_history']
    numerical_features=['age', 'hypertension', 'heart_disease', 'bmi', 'HbA1c_level', 'blood_glucose_level']

    expected_columns = numerical_features + categorical_features

    new_data = pd.DataFrame([diabetes_data])

    new_data = new_data.reindex(columns=expected_columns, fill_value=0)

    prediction = diabetes_model.predict(new_data)
    prediction_proba = diabetes_model.predict_proba(new_data)

    # Convert numpy types to native Python types
    diabetes_prediction = int(prediction[0]) if isinstance(prediction[0], np.integer) else prediction[0]
    diabetes_confidence = float(max(prediction_proba[0])) if isinstance(max(prediction_proba[0]), np.floating) else max(prediction_proba[0])

    # update patient data with prediction
    patient_collection.update_one(
        {'patient_id': patient_id},
        {'$set': {'diabetes_prediction': diabetes_prediction, 'diabetes_confidence': diabetes_confidence}}
    )

    return {'prediction': diabetes_prediction, 'confidence': diabetes_confidence}


def get_all_missing_columns(patient_id):
    heart_columns = heart_missing_columns(patient_id)
    stroke_columns = stroke_missing_columns(patient_id)
    diabetes_columns = diabetes_missing_columns(patient_id)
    missing_columns = {**heart_columns, **stroke_columns, **diabetes_columns}
    return missing_columns

# predict all diseases sequentially
def predict_all(patient_id):
    heart_prediction = predict_heart(patient_id)
    stroke_prediction = predict_stroke(patient_id)
    diabetes_prediction = predict_diabetes(patient_id)
    return {'heart': heart_prediction, 'stroke': stroke_prediction, 'diabetes': diabetes_prediction}

