from Flask import Flask, jsonify, request

def patient_history():
    return jsonify({'message': 'Patient History'})

def appointment():
    return jsonify({'message': 'Appointment'})