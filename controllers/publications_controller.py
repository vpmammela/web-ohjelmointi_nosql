from flask.views import MethodView
from flask import jsonify, request
from models import Publication
from validators.validate_publications import validate_add_publication

class PublicationsRouteHandler(MethodView):
    @validate_add_publication
    def post(self):
        request_body = request.get_json()
        title = request_body['title']
        description = request_body['description']
        url = request_body['url']
        publication = Publication(title, description, url)
        publication.create()

        return jsonify(publication=publication.to_json())

    def get(self):
        publications = Publication.get_all()

        return jsonify(publications = Publication.list_to_json(publications))
