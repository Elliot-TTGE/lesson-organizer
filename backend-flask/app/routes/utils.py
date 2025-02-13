from flask import jsonify
from functools import wraps

def response_wrapper(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            response = {
                "status": "success", 
                "data": result
            }
            return jsonify(response), 200
        except Exception as e:
            response = {
                "status": "error", 
                "message": str(e)
            }
            return jsonify(response), 500
    return wrapped_function
                