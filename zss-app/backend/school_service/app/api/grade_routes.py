from flask import Blueprint, jsonify, request
from .decorators import token_required
from ..services.school_logic_service import SchoolService

grade_bp = Blueprint('grade_bp', __name__)

@grade_bp.route('/grades', methods=['POST'])
@token_required
def create_grade(current_user):
    if current_user['role'] != 'NASTAVNIK':
        return jsonify({'message': 'Samo nastavnici mogu unositi ocene'}), 403
    data = request.get_json()
    response, status_code = SchoolService.create_grade(current_user['user_id'], data)
    return jsonify(response), status_code

@grade_bp.route('/grades', methods=['GET'])
@token_required
def get_grades(current_user):
    response, status_code = SchoolService.get_grades_for_user(current_user['user_id'], current_user['role'])
    return response, status_code