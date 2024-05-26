from flask import Flask, jsonify, request

def outliers():
    return jsonify({'message': 'Outliers'})

def analysis():
    return jsonify({'message': 'Analysis'})

def predict():
    return jsonify({'message': 'Predict'})
