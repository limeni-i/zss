from flask import Blueprint, jsonify
from bson import json_util
import json
from ..extensions import mongo

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/users', methods=['GET'])
def get_all_users():
    users_collection = mongo.db.users
    
    users = users_collection.find({}, {'password': 0})
    
    return json.loads(json_util.dumps(list(users))), 200

@user_bp.route('/users/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
    from ..services.auth_service import AuthService
    response, status_code = AuthService.get_user_by_id(user_id)
    return response, status_code