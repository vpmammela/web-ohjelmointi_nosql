from flask import jsonify, request
from models import User
from flask.views import MethodView
from validators.account import check_profile_picture_max_size, validate_update_profile_picture
from flask_jwt_extended import jwt_required
from validators.auth import validate_logged_in_admin


class UsersRouteHandler(MethodView):
    def get(self):
        users_list = User.get_all()
        return jsonify(users = User.list_to_json(users_list))

    def post(self):
        request_body = request.get_json()
        user = User(request_body['username'], role = request_body.get('role', 'user'))
        user.create()
        return ""

    
class UserRouteHandler(MethodView):
    def get(self, _id):
        user = User.get_by_id(_id)
        return jsonify(user = user.to_json())

    @jwt_required()
    @validate_logged_in_admin
    def delete(self, _id):
        User.delete_by_id(_id)
        return ""
    
    def patch(self, _id):
        request_body = request.get_json()
        user = User.get_by_id(_id)
        user.username = request_body.get('username', user.username)
        user.update()
        return jsonify(user = user.to_json())

    def put(self, _id):
        request_body = request.get_json()
        user = User.get_by_id(_id)
        user.username = request_body.get('username', user.username)
        user.update()
        return jsonify(user = user.to_json())

class UpdateProfilePictureRouteHandler(MethodView):
    @validate_update_profile_picture
    @check_profile_picture_max_size
    def patch(self, _id):
        request_body = request.get_json()
        user = User.get_by_id(_id)
        user.profile_picture = request_body.get('profile_picture', user.profile_picture)
        return jsonify(user = user.to_json())

    @validate_update_profile_picture
    @check_profile_picture_max_size
    def put(self, _id):
        request_body = request.get_json()
        user = User.get_by_id(_id)
        user.profile_picture = request_body.get('profile_picture', user.profile_picture)
        return jsonify(user = user.to_json())