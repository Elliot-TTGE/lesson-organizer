from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required, 
    get_jwt_identity,
    get_jwt,
    create_access_token,
    set_access_cookies,
    unset_jwt_cookies
)
from datetime import datetime, timedelta, timezone
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')
    user = User.query.filter_by(email=email).first()
    
    if user and user.verify_password(password):
        access_token = create_access_token(identity=user.id, expires_delta=timedelta(hours=4))
        
        response = jsonify(status='success', data={'access_token': access_token})
        set_access_cookies(response, access_token)
        return response, 200
    else:
        return jsonify(status='fail', message='Bad email or password'), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    response = jsonify(status='success', message='Logged out successfully')
    unset_jwt_cookies(response)
    return response, 200

def refresh_expiring_jwts(response):
    try:
        if not get_jwt():
            return response
        
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(hours=2))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity(), expires_delta=timedelta(hours=4))
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        return response

@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify(status='success', data={'logged_in_as': user.email}), 200