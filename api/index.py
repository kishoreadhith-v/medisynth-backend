from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure MongoDB
client = MongoClient(os.getenv('MONGO_URI'))
db = client['dev-db']

# Import blueprints
from routes.patient_routes import patient_bp
from routes.anomaly_routes import anomaly_bp
from routes.care_plan_routes import care_plan_bp
from routes.diagnose_routes import diagnose_bp

# Register blueprints
app.register_blueprint(patient_bp)
app.register_blueprint(anomaly_bp)
app.register_blueprint(care_plan_bp)
app.register_blueprint(diagnose_bp)

@app.route('/')
def home():
    return 'Medisynth Backend'

# Start the application
if __name__ == '__main__':
    app.run(debug=True)
