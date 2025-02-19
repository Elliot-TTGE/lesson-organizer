from flask import jsonify, make_response
from functools import wraps

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
