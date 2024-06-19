import datetime
import traceback
from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity


# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
jwt = JWTManager(app)

# Configure MongoDB
client = MongoClient(os.getenv('MONGO_URI'))
db = client['dev-db']

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)


# Import blueprints
from routes.patient_routes import patient_bp
from routes.care_plan_routes import care_plan_bp
from routes.diagnose_routes import diagnose_bp
from routes.forum_routes import forum_bp

app = Flask(__name__)

app.register_blueprint(patient_bp)
app.register_blueprint(care_plan_bp)
app.register_blueprint(diagnose_bp)
app.register_blueprint(forum_bp)

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
