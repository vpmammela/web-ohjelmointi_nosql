import pymongo
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from config import Config
from errors.not_found import NotFound
from errors.validation_error import ValidationError


client = pymongo.MongoClient(Config.CONNECTION_STRING, 
server_api=ServerApi('1'))
db = client.flask_db

class User:
    def __init__(self, username, password = None, role = 'user', _id = None):
        self.username = username
        self.password = password
        self.role = role
        if _id is not None:
            _id = str(_id)
        self._id = _id

    @staticmethod
    def get_all():
        users_cursor = db.users.find()
        users_list = list(users_cursor)
        users = []
        for user_dictionary in users_list:
            users.append(User(user_dictionary['username'],
            role = user_dictionary['role'],
            _id = user_dictionary['_id']))
        return users

    def create(self):
        user = db.users.find_one({'username': self.username})
        if user is not None:
            raise ValidationError(message = 'username must be unique')
        result = db.users.insert_one({'username': self.username, 'role': self.role, 'password': self.password})
        self._id = str(result.inserted_id)

    def to_json(self):
        return {
            '_id': str(self._id),
            'username': self.username,
            'role': self.role,
            
    }

    def update(self):
        _filter = {'_id': ObjectId(self._id)}
        _update = {
        '$set': {'username': self.username}
        }
        db.users.update_one(_filter, _update)

    @staticmethod
    def list_to_json(user_list):
        users = []
        for user in user_list:
            users.append(user.to_json())
        return users

    @staticmethod
    def get_by_id(_id):
        user_dictionary = db.users.find_one({'_id': ObjectId(_id)})
        if user_dictionary is None:
            raise NotFound(message = "user not found")
        user = User(user_dictionary['username'],
            role = user_dictionary['role'],
            _id = user_dictionary['_id'])
        return user

    @staticmethod
    def get_by_username(username):
        user_dictionary = db.users.find_one({'username': username})
        if user_dictionary is None:
            raise NotFound(message = "user not found")
        user = User(user_dictionary['username'],
            role = user_dictionary['role'],
            _id = user_dictionary['_id'],
            password = user_dictionary['password'])
        return user

    @staticmethod
    def delete_by_id(_id):
        db.users.delete_one({'_id': ObjectId(_id)})



class Publication:
    def __init__(self, 
    title, 
    description, 
    url, 
    owner = None, 
    likes = [],
    _id = None):
        self.title = title
        self.description = description
        self.url = url
        self.owner = owner
        self.likes = likes
        if _id is not None:
            _id = str(_id)
        self._id = _id

    def to_json(self):
        return {
            '_id': str(self._id),
            'title': self.title,
            'description': self.description,
            'url': self.url
        }

    @staticmethod
    def list_to_json(publication_list):
        publications = []
        for publication in publication_list:
            publications.append(publication.to_json())
        return publications


    def create(self):
        result = db.publications.insert_one({
            'title': self.title,
            'description': self.description,
            'url': self.url
        })

        self._id = str(result.inserted_id)

    @staticmethod
    def get_all():
        publications_cursor = db.publications.find()
        publications_list = list(publications_cursor)
        publications = []
        for publication in publications_list:
            publication_object = Publication(
                publication['title'],
                publication['description'],
                publication['url'],
                _id = publication['_id'])
            publications.append(publication_object)
        return publications
        