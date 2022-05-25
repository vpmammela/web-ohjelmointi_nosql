from flask import jsonify
from flask_jwt_extended import get_jwt

from models import User

def validate_logged_in_user(func):
    def validate_logged_in_user_wrapper(*args, **kwargs):
        logged_in_user = get_jwt()
        user = User.get_by_id(logged_in_user['sub'])
        if user is None:
            return jsonify(err='Unauthorized'), 401
        return func(*args, **kwargs)
    return validate_logged_in_user_wrapper

""" def validate_logged_in_admin(func):
    def validate_logged_in_admin_wrapper(*args, **kwargs):
        logged_in_user = get_jwt()
        print("#########################", logged_in_user)
        user = User.get_by_id(logged_in_user['role'])
        if user['role'] != 'admin':
            return jsonify(err='Unauthorized'), 401
        return func(*args, **kwargs)
    return validate_logged_in_admin_wrapper """