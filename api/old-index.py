from flask import Flask, jsonify, request
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import json
import traceback
import uuid
from flask_cors import CORS
import google.generativeai as genai
import fitz  # PyMuPDF

from diagnoser import outliers, analysis, predict
from criticality import criticality_score, resource_availability, resource_allocation
from patient import patient_history, appointment

load_dotenv()

app = Flask(__name__)
CORS(app)

# Upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# MongoDB Connection
client = MongoClient(os.getenv('MONGO_URI'))
db = client['dev-db']
patient_collection = db['patients']
report_collection = db['reports']

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def error_stack(error):
    stack_trace = traceback.format_exc()
    response = {
        'error': error,
        'stack_trace': stack_trace
    }
    return jsonify(response), 500

@app.errorhandler(Exception)
def handle_exception(e):
    return error_stack(str(e))

@app.route('/')
def home():
    return 'Medisynth Backend'

@app.route('/about')
def about():
    return 'About'

@app.route('/test_get', methods=['GET'])
def test_get():
    users = db.users.find()
    userlist = list(users)
    for user in userlist:
        del user['_id']
    
    return jsonify(userlist)

# diagnoser routes
@app.route('/diagnoser/outliers', methods=['POST'])
def get_outliers():
    return outliers()

@app.route('/diagnoser/analysis', methods=['POST'])
def get_analysis():
    return analysis()

@app.route('/diagnoser/predict', methods=['POST'])
def get_predict():
    return predict()

# criticality and resouces routes 
@app.route('/criticality_score', methods=['POST'])
def get_criticality_score():
    return criticality_score()

@app.route('/resource_availability', methods=['GET'])
def get_resource_availability():
    return resource_availability()

@app.route('/allocate_resources', methods=['POST'])
def get_resource_allocation():
    return resource_allocation()

#patient routes
@app.route('/patient/patient_history', methods=['GET'])
def get_patient_history():
    return patient_history()

@app.route('/patient/appointment', methods=['POST'])
def get_appointment():
    return appointment()

# Error handling
def handle_file_processing_error(error):
    return jsonify({'error': 'File processing failed', 'details': str(error)}), 400

def handle_gemini_api_error(error):
    return jsonify({'error': 'Gemini API request failed', 'details': str(error)}), 500

def extract_text_from_pdf(filepath):
    doc = fitz.open(filepath)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        if file_extension not in ['pdf']:
            return jsonify({'error': 'Invalid file type'}), 400
        
        filename = f"{uuid.uuid4()}.{file_extension}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Extract text from the PDF
        pdf_text = extract_text_from_pdf(filepath)
        
        # Create prompt with extracted text
        prompt = f"Extract patient info and anomalies from the following lab report text: \n{pdf_text}. Output only JSON for easy parsing."

        # Interact with Gemini API
        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
        response = model.generate_content([prompt])

        # Debugging: Print the response content
        print("Gemini API Response:")
        print(response)

        # Extract and parse JSON from the response text
        response_text = response.candidates[0].content.parts[0].text.strip()
        
        if response_text.startswith("```json") and response_text.endswith("```"):
            response_text = response_text[7:-3].strip()
        
        result = json.loads(response_text)

        patient_info = result.get('patient_info', {})
        anomalies = result.get('anomalies', [])

        # Store metadata and results in MongoDB
        report_data = {
            'filename': filename,
            'filepath': filepath,
            'patient_info': patient_info,
            'anomalies': anomalies
        }
        insert_result = report_collection.insert_one(report_data)

        # Convert ObjectId to string
        report_data['_id'] = str(insert_result.inserted_id)

        return jsonify(report_data), 201
    
    except Exception as e:
        return handle_file_processing_error(e)

# Main
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
