
import random
import string
from flask.views import MethodView
from flask import jsonify, request
from errors.not_found import NotFound
from errors.validation_error import ValidationError
from models import Publication, Comment
from validators.auth import validate_logged_in_admin, validate_logged_in_user
from validators.validate_publications import validate_add_publication
from flask_jwt_extended import jwt_required, get_jwt
from bson.objectid import ObjectId

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
        publications = []
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

class PublicationRouteHandler(MethodView):
    @jwt_required(optional = True)
    def get(self, _id):
        logged_in_user = get_jwt()
        if logged_in_user:
            if logged_in_user['role'] == 'admin':
                publication = Publication.get_by_id(_id)
            elif logged_in_user['role'] == 'user':
                publication = Publication.get_logged_in_users_and_public_publication(_id, logged_in_user)   
        else:
            publication = Publication.get_one_by_id_visibility(_id)
        return jsonify(publication=publication.to_json())

    @jwt_required(optional = False)
    @validate_logged_in_user
    @validate_logged_in_admin
    def delete(self, _id):
        logged_in_user = get_jwt()
        #if logged_in_user['role'] == 'admin':
        #    Publication.delete_by_id(_id)
        if logged_in_user['role'] == 'user':
            Publication.delete_by_id_and_owner(_id, logged_in_user)
        Publication.delete_by_id(_id)
        return ""


    @jwt_required(optional = False)
    @validate_logged_in_user
    @validate_logged_in_admin
    def patch(self, _id):
        logged_in_user = get_jwt()
        publication = Publication.get_by_id(_id)
        if logged_in_user['role'] == 'user':
            if publication.owner is None or str(publication.owner) != logged_in_user['sub']:
                raise NotFound(message = 'publication not found')
        request_body = request.get_json()
        publication.title = request_body.get('title', publication.title)
        publication.description = request_body.get('description', publication.description)
        publication.visibility = request_body.get('visibility', publication.visibility)

        publication.update()
        return jsonify(publication=publication.to_json())


class LikePublicationRouteHandler(MethodView):
    @jwt_required(optional=False)
    @validate_logged_in_user
    def patch(self, _id):
        logged_in_user = get_jwt()
        publication = Publication.get_by_id(_id)
        found_index = -1 # oletusarvo = -1 koska arrayt / listat alkavat 0. 
                         # -1 tarkoittaa siis, ettei käyttäjää oli likes-listassa
        for index, user_object_id in enumerate(publication.likes):
            if str(user_object_id) == logged_in_user['sub']:
                found_index = index
                break

        if found_index != -1:
            del publication.likes[found_index]
        else:
            publication.likes.append(ObjectId(logged_in_user['sub']))

        publication.like()
        return jsonify(publication=publication.to_json())


class SharePublicationRouteHandler(MethodView):
    @jwt_required(optional=False)
    @validate_logged_in_user
    def patch(self, _id):
        publication = Publication.get_by_id(_id)
        if publication.share_link is None:
            letters = string.ascii_lowercase
            publication.share_link = ''.join(random.choice(letters) for _ in range(8))
        publication.shares += 1

        publication.share()
        return jsonify(publication=publication.to_json())


class PublicationCommentsRouteHandler(MethodView):
    @jwt_required(optional=False)
    @validate_logged_in_user
    def post(self, _id):
        request_body = request.get_json()
        if request_body and 'body' in request_body:
            logged_in_user = get_jwt()
            comment = Comment(request_body['body'], logged_in_user['sub'], _id)
            comment.create()
            return jsonify(comment=comment.to_json())
        raise ValidationError(message='body is required')

    def get(self, _id):
        #publication = Publication.get_by_id(_id)
        #comments = publication.get_comments()

        comments = Comment.get_all_by_publication(_id)
        return jsonify(comments=Comment.list_to_json(comments))


class PublicationCommentRouteHandler(MethodView):
    @jwt_required()
    @validate_logged_in_user
    #@validate_logged_in_admin
    def delete(self, _id, comment_id):
        logged_in_user = get_jwt()
        if logged_in_user['role'] == 'user':
            Comment.delete_by_id_and_owner(comment_id, logged_in_user)
        Comment.delete_by_id(comment_id)
        return ""

    @jwt_required()
    @validate_logged_in_user
    #@validate_logged_in_admin
    def patch(self, _id, comment_id):
        logged_in_user = get_jwt()
        comment = Comment.get_comment_by_publication_id_and_comment_id(_id, comment_id).to_json()
        request_body = request.get_json()
        if request_body and 'body' in request_body:
            if logged_in_user['sub'] == comment['owner'] or logged_in_user['role'] == 'admin':
                comment = Comment.update_by_id(comment_id, request_body['body'])
                return jsonify(comment=comment.to_json())
            else:
                raise ValidationError(message='comment not found')
        raise ValidationError(message='body is required')
        