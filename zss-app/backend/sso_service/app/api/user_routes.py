from flask import Blueprint, jsonify
from bson import json_util
import json
from ..extensions import mongo

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/users', methods=['GET'])
def get_all_users():
    """Vraća listu svih korisnika iz baze (bez lozinki)."""
    users_collection = mongo.db.users
    
    users = users_collection.find({}, {'password': 0})
    
    return json.loads(json_util.dumps(list(users))), 200