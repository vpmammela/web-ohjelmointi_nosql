from crypt import methods
from flask import Flask, jsonify
from controllers.auth_controller import LoginRouteHandler, RegisterRouteHandler
from controllers.home_controller import home_route_handler
from controllers.publications_controller import PublicationRouteHandler, PublicationsRouteHandler
from controllers.users_controller import UsersRouteHandler, UserRouteHandler
from errors.not_found import NotFound
from errors.validation_error import ValidationError
from flask_jwt_extended import JWTManager

app = Flask(__name__)

app.config.from_object('config.Config')

jwt = JWTManager(app)


@app.errorhandler(ValidationError)
def handle_validation_error(err):
    return jsonify(err=err.args), 400

@app.errorhandler(NotFound)
def handle_not_found_error(err):
    return jsonify(err=err.args), 404

app.add_url_rule('/', view_func=home_route_handler)
app.add_url_rule('/api/users', view_func=UsersRouteHandler.as_view('users_route_handler'), methods = ['GET', 'POST'])
app.add_url_rule('/api/users/<_id>', view_func=UserRouteHandler.as_view('user_route_handler'), 
methods = ['GET', 'DELETE', 'PUT', 'PATCH'])

app.add_url_rule('/api/register', view_func = RegisterRouteHandler.as_view('register_route_handler'), methods = ['POST'])
app.add_url_rule('/api/login', view_func=LoginRouteHandler.as_view('login_route_handler'), methods=['POST'])

app.add_url_rule('/api/publications', view_func=PublicationsRouteHandler.as_view('publications_route_handler'), 
methods = ['POST', 'GET'])

app.add_url_rule('/api/publication/<_id>', view_func=PublicationRouteHandler.as_view('publication_route_handler'), 
methods = ['GET', 'DELETE', 'PATCH'])

app.run(debug=True)