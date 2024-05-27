from flask import Flask, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import traceback

from diagnoser import outliers, analysis, predict
from criticality import criticality_score, resource_availability, resource_allocation
from patient import patient_history, appointment

load_dotenv()
    
app = Flask(__name__)


# MongoDB Connection
client = MongoClient(os.getenv('MONGO_URI'))
db = client['dev-db']

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

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True, host='0.0.0.0', port=5000)
