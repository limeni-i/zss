import jwt
import datetime
from flask import current_app
from ..extensions import mongo, bcrypt
from ..models.user_model import User # Dodajte ovaj import

class AuthService:

    @staticmethod
    def register_user(data):
        users_collection = mongo.db.users
        
        if users_collection.find_one({'email': data['email']}):
            return {'error': 'Korisnik sa ovim email-om već postoji'}, 409

        hashed_password = User.hash_password(data['password'])

        new_user = User(
            name=data['name'],
            email=data['email'],
            password=hashed_password,
            role=data['role']
        )
        
        new_user_id = users_collection.insert_one(new_user.to_document()).inserted_id

        return {'message': 'Korisnik uspešno registrovan', 'user_id': str(new_user_id)}, 201

    @staticmethod
    def login_user(data):
        users_collection = mongo.db.users
        user_data = users_collection.find_one({'email': data['email']})

        if user_data and User.check_password(user_data['password'], data['password']):
            token = jwt.encode({
                'user_id': str(user_data['_id']),
                'role': user_data['role'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, current_app.config['SECRET_KEY'], algorithm="HS256")

            return {'token': token}, 200
        
        return {'error': 'Neispravan email ili lozinka'}, 401