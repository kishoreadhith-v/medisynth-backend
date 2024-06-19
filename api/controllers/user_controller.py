import datetime
import hashlib
from flask import jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URI'))
db = client['dev-db']
user_collection = db['users']

# create a new user
def signup(data):
    new_user = {
        'email': data.get('email'),
        'password': data.get('password'),
        'first_name': data.get('first_name'),
        'last_name': data.get('last_name'),
        'created_at': datetime.datetime.now(),
        'role': data.get('role'),
        'notifications': [],
    }
    new_user['password'] = hashlib.sha256(new_user['password'].encode("utf-8")).hexdigest()
    existing_user = user_collection.find_one({'email': new_user['email']})
    if existing_user:
        return {'error': 'User already exists'}
    result = user_collection.insert_one(new_user)
    return {'message': 'User created successfully', 'user_id': str(result.inserted_id)}

# login a user
def login(data):
    email = data.get('email')
    password = data.get('password')
    hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
    user = user_collection.find_one({'email': email, 'password': hashed_password})
    if user:
        access_token = create_access_token(identity=email)
        return {'access_token': access_token}
    return {'error': 'Invalid credentials'}

# profile of a user
def profile():
    email = get_jwt_identity()
    user = user_collection.find_one({'email': email})
    if user:
        user['_id'] = str(user['_id'])
        return user
    return {'error': 'User not found'}

# update user profile
def update_profile(data):
    email = get_jwt_identity()
    user = user_collection.find_one({'email': email})
    if user:
        update = {
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'role': data.get('role'),
        }
        user_collection.update_one(
            {'email': email},
            {'$set': update}
        )
        return {'message': 'Profile updated successfully'}
    
    return {'error': 'User not found'}

# delete a user
def delete_user():
    email = get_jwt_identity()
    user = user_collection.find_one({'email':email})
    if user:
        user_collection.delete_one({'email': email})
        return {'message': 'User deleted successfully'}
    return {'error': 'User not found'}

# add a notification to a user
def add_notification(data):
    email = get_jwt_identity()
    user = user_collection.find

