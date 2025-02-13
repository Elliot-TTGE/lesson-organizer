from flask import jsonify

def response_wrapper(func):
    def wrapper(*args, **kwargs):
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
    return wrapper
                