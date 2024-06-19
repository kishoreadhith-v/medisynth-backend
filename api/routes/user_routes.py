from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from controllers.user_controller import signup, login, profile, update_profile, delete_user, send_message

user_bp = Blueprint('user', __name__, url_prefix='/users')

@user_bp.route('/signup', methods=['POST'])
def signup_user():
    data = request.json
    return jsonify(signup(data))

@user_bp.route('/login', methods=['POST'])
def login_user():
    data = request.json
    return jsonify(login(data))

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    return jsonify(profile())

@user_bp.route('/update_profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    data = request.json
    return jsonify(update_profile(data))

@user_bp.route('/delete_user', methods=['DELETE'])
@jwt_required()
def delete_user_profile():
    return jsonify(delete_user())

@user_bp.route('/send_message', methods=['POST'])
def send_slack_message():
    data = request.json
    channel_id = data.get('channel_id')
    message = data.get('message')
    return jsonify(send_message(channel_id, message))