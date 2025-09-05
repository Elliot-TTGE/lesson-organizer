from flask import jsonify, make_response
from functools import wraps
from flask_jwt_extended import get_jwt_identity
from app.models.user_model import User

def get_current_user():
    """Get the current authenticated user from JWT token"""
    user_id = get_jwt_identity()
    if user_id:
        return User.query.get(user_id)
    return None

def response_wrapper(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            if isinstance(result, tuple) and len(result) == 2:
                data, status_code = result
            else:
                data, status_code = result, 200

            # Define the response variable before using it
            response = {}

            if status_code == 204:
                response = {
                    "status": "success",
                    "message": "No Content"
                }
                return make_response(jsonify(response), 204)

            if isinstance(data, dict) and "message" in data:
                response = {
                    "status": "success",
                    "message": data["message"]
                }
            else:
                response = {
                    "status": "success",
                    "data": data
                }
            return jsonify(response), status_code
        except Exception as e:
            response = {
                "status": "error",
                "message": str(e)
            }
            return jsonify(response), 500
    return wrapped_function
