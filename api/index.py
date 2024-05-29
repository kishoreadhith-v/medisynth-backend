from flask import Flask
from flask_cors import CORS
from routes.patient_routes import patient_bp
from routes.anomaly_routes import anomaly_bp
from routes.care_plan_routes import care_plan_bp
from routes.diagnose_routes import diagnose_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(patient_bp)
app.register_blueprint(anomaly_bp)
app.register_blueprint(care_plan_bp)
app.register_blueprint(diagnose_bp)

@app.route('/')
def home():
    return 'Medisynth Backend'

@app.route('/about')
def about():
    return 'About'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
