from flask import Blueprint, request, jsonify
from .decorators import token_required
from ..services.health_logic_service import HealthService

justification_bp = Blueprint('justification_bp', __name__)

@justification_bp.route('/justifications/request', methods=['POST'])
def create_request():
    data = request.get_json()
    response, status_code = HealthService.create_justification_request(data)
    return jsonify(response), status_code


@justification_bp.route('/justifications', methods=['GET'])
@token_required
def get_requests(current_user):
    if current_user['role'] != 'LEKAR':
        return jsonify({'message': 'Pristup odbijen'}), 403
    response, status_code = HealthService.get_justification_requests_for_doctor(current_user['user_id'])
    return response, status_code


@justification_bp.route('/justifications/<request_id>/approve', methods=['PUT'])
@token_required
def approve_request(current_user, request_id):
    if current_user['role'] != 'LEKAR':
        return jsonify({'message': 'Samo lekari mogu odobravati zahteve'}), 403
    response, status_code = HealthService.process_justification_request(request_id, current_user['user_id'], "ODOBREN")
    return jsonify(response), status_code


@justification_bp.route('/justifications/<request_id>/reject', methods=['PUT'])
@token_required
def reject_request(current_user, request_id):
    if current_user['role'] != 'LEKAR':
        return jsonify({'message': 'Samo lekari mogu odbijati zahteve'}), 403
    response, status_code = HealthService.process_justification_request(request_id, current_user['user_id'], "ODBIJEN")
    return jsonify(response), status_code