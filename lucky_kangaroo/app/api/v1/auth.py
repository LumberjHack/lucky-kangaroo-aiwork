from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, create_access_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.post('/login')
def login():
    # Minimal demo login issuing a token without password verification
    token = create_access_token(identity='demo-user')
    return jsonify({'access_token': token})

@auth_bp.get('/me')
@jwt_required()
def me():
    return jsonify({'user': 'demo-user'})
