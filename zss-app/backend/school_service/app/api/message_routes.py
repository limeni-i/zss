from flask import Blueprint, request, jsonify
from .decorators import token_required
from ..services.school_logic_service import SchoolService

message_bp = Blueprint('message_bp', __name__)

@message_bp.route('/messages', methods=['POST'])
@token_required
def send_message(current_user):
    if current_user['role'] not in ['NASTAVNIK', 'RODITELJ']:
        return jsonify({'message': 'Samo nastavnici i roditelji mogu slati poruke'}), 403
    data = request.get_json()
    response, status_code = SchoolService.send_message(current_user['user_id'], current_user['role'], data)
    return jsonify(response), status_code

@message_bp.route('/messages/conversation/<other_user_id>', methods=['GET'])
@token_required
def get_conversation(current_user, other_user_id):
    response, status_code = SchoolService.get_conversation(current_user['user_id'], other_user_id)
    return response, status_code