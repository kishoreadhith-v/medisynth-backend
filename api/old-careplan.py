from flask import Flask, jsonify, request

def preferences():
    return jsonify({'message': 'Preferences'})

def generate_careplan():
    return jsonify({'message': 'Generate Careplan'})