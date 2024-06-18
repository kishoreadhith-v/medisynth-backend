import traceback
from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
# CORS(app)

# Configure MongoDB
client = MongoClient(os.getenv('MONGO_URI'))
db = client['dev-db']

# Import blueprints
from routes.patient_routes import patient_bp
from routes.anomaly_routes import anomaly_bp
from routes.care_plan_routes import care_plan_bp
from routes.diagnose_routes import diagnose_bp

app = Flask(__name__)

app.register_blueprint(patient_bp)
app.register_blueprint(anomaly_bp)
app.register_blueprint(care_plan_bp)
app.register_blueprint(diagnose_bp)

@app.route('/')
def home():
    return 'Medisynth Backend'

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


# Start the application
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
