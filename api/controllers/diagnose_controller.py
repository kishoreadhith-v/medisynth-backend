from flask import Flask, jsonify
from pymongo import MongoClient
import joblib
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URI'))
db = client['dev-db']
patient_collection = db['patients']

def predict(patient_id):
    # Fetch patient data from MongoDB
    patient_data = patient_collection.find_one({"patient_id": patient_id})
    if not patient_data:
        return jsonify({"error": "Patient not found"}), 404

    # Extract lab results and vitals
    lab_results = patient_data.get('lab_results', {})
    vitals = patient_data.get('vitals', {})

    # Combine lab results and vitals
    data = {**lab_results, **vitals}

    # Prepare data for each model
    heart_data = {
        'Age': data.get('Age', 0),
        'Sex': data.get('Sex', 'M'),
        'ChestPainType': data.get('ChestPainType', 'ATA'),
        'RestingBP': data.get('RestingBP', 0),
        'Cholesterol': data.get('Cholesterol', 0),
        'FastingBS': 0,  # Default as no fasting blood sugar info
        'RestingECG': data.get('RestingECG', 'Normal'),
        'MaxHR': data.get('MaxHR', 0),
        'ExerciseAngina': data.get('ExerciseAngina', 'N'),
        'Oldpeak': data.get('Oldpeak', 0),
        'ST_Slope': data.get('ST_Slope', 'Up')
    }

    stroke_data = {
        'age': data.get('age', 0),
        'hypertension': data.get('hypertension', 0),
        'heart_disease': data.get('heart_disease', 0),
        'ever_married': data.get('ever_married', 'No'),
        'work_type': data.get('work_type', 'Private'),
        'Residence_type': data.get('Residence_type', 'Urban'),
        'avg_glucose_level': data.get('avg_glucose_level', 0),
        'bmi': data.get('bmi', 0),
        'smoking_status': data.get('smoking_status', 'never smoked')
    }

    # Make predictions
    predictions = []
    heart_prediction, heart_confidence = make_prediction('heart_rf_model.pkl', heart_data)
    stroke_prediction, stroke_confidence = make_prediction('stroke_rf_model.pkl', stroke_data)

    predictions.append({
        "disease": "Heart Disease",
        "prediction": heart_prediction,
        "confidence": heart_confidence
    })
    predictions.append({
        "disease": "Stroke",
        "prediction": stroke_prediction,
        "confidence": stroke_confidence
    })

    # Update the MongoDB document with predictions
    patient_collection.update_one({"patient_id": patient_id}, {"$set": {"predictions": predictions}})

    return jsonify({"patient_id": patient_id, "predictions": predictions})

def make_prediction(model_path, input_data):
    # Load the model
    model = joblib.load(f'models/{model_path}')
    input_df = pd.DataFrame([input_data])

    # Ensure the new data has the same columns as the training data
    preprocess = model.named_steps['preprocessor']
    expected_columns = preprocess.transformers_[0][2] + \
        preprocess.transformers_[1][1].named_steps['onehot'].get_feature_names_out().tolist()
    input_df = input_df.reindex(columns=expected_columns, fill_value=0)

    prediction = model.predict(input_df)[0]
    prediction_proba = model.predict_proba(input_df)[0]

    return prediction, max(prediction_proba)
