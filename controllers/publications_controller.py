from flask.views import MethodView
from flask import jsonify, request
from models import Publication
from validators.validate_publications import validate_add_publication
from flask_jwt_extended import jwt_required, get_jwt

class PublicationsRouteHandler(MethodView):
    @validate_add_publication
    @jwt_required(optional=True)
    def post(self):
        logged_in_user = get_jwt()
        owner = None
        visibility = 2
        request_body = request.get_json()
        if logged_in_user:
            owner = logged_in_user['sub']
            visibility = request_body.get('visibility', 2)

        title = request_body['title']
        description = request_body['description']
        url = request_body['url']
        publication = Publication(title, description, url, owner = owner, visibility = visibility)
        publication.create()

        return jsonify(publication=publication.to_json())

    @jwt_required(optional = True)
    def get(self):
        logged_in_user = get_jwt()
        if not logged_in_user:
            # haetaan vain publicationit joissa visibility 2
            publications = Publication.get_by_visibility(visibility=2)
        else:
            if logged_in_user['role'] == 'admin':
                publications = Publication.get_all()
            elif logged_in_user['role'] == 'user':
                # julkaisut joissa visibility 1 tai 2
                publications = Publication.get_logged_in_users_and_public_publications(logged_in_user)
        return jsonify(publications = Publication.list_to_json(publications))
