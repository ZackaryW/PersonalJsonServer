from flask import jsonify

def flask_jsonify_response(code=200, message='OK', **kwargs):
    return jsonify({
        'code': code,
        'message': message,
        **kwargs
    })