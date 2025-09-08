from flask import Blueprint, request, jsonify
from .decorators import token_required
from ..services.health_logic_service import HealthService

timeslot_bp = Blueprint('timeslot_bp', __name__)

@timeslot_bp.route('/timeslots/create-day', methods=['POST'])
@token_required
def create_day(current_user):
    if current_user['role'] != 'LEKAR': return jsonify({'message': 'Pristup odbijen'}), 403
    data = request.get_json()
    response, status = HealthService.create_timeslots_for_day(current_user['user_id'], data)
    return jsonify(response), status

@timeslot_bp.route('/timeslots/doctor/<doctor_id>', methods=['GET'])
@token_required
def get_doctor_slots(current_user, doctor_id): 
    if current_user['role'] == 'LEKAR' and current_user['user_id'] != doctor_id:
         return jsonify({'message': 'Lekar može videti samo svoj kalendar'}), 403
    response, status = HealthService.get_timeslots_for_doctor(doctor_id)
    return response, status

@timeslot_bp.route('/timeslots/free/<doctor_id>', methods=['GET'])
@token_required
def get_free_slots(current_user, doctor_id):
    response, status = HealthService.get_free_timeslots(doctor_id)
    return response, status

@timeslot_bp.route('/timeslots/<slot_id>/book', methods=['PUT'])
@token_required
def book_slot(current_user, slot_id):
    if current_user['role'] != 'PACIJENT': return jsonify({'message': 'Pristup odbijen'}), 403
    response, status = HealthService.book_timeslot(slot_id, current_user['user_id'])
    return jsonify(response), status

@timeslot_bp.route('/timeslots/patient', methods=['GET'])
@token_required
def get_patient_appointments(current_user):
    response, status = HealthService.get_appointments_for_patient(current_user['user_id'])
    return response, status

@timeslot_bp.route('/timeslots/check-completed', methods=['POST'])
def check_completed():
    data = request.get_json()
    response, status = HealthService.check_completed_appointment(data)
    return jsonify(response), status