from flask import Blueprint, request, jsonify
from .decorators import token_required
from ..services.health_logic_service import HealthService

appointment_bp = Blueprint('appointment_bp', __name__)

@appointment_bp.route('/appointments', methods=['POST'])
@token_required
def schedule_appointment(current_user):
    if current_user['role'] != 'PACIJENT':
        return jsonify({'message': 'Samo pacijenti mogu zakazivati preglede'}), 403
    
    data = request.get_json()
    response, status_code = HealthService.schedule_appointment(current_user['user_id'], data)
    return jsonify(response), status_code

@appointment_bp.route('/appointments', methods=['GET'])
@token_required
def get_appointments(current_user):
    response, status_code = HealthService.get_appointments_for_user(current_user['user_id'], current_user['role'])
    
    return response, status_code