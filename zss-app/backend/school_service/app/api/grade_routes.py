from flask import Blueprint, jsonify, request
from .decorators import token_required
from ..services.school_logic_service import SchoolService
from flask import Response

grade_bp = Blueprint('grade_bp', __name__)

@grade_bp.route('/grades', methods=['POST'])
@token_required
def create_grade(current_user):
    if current_user['role'] != 'NASTAVNIK':
        return jsonify({'message': 'Samo nastavnici mogu unositi ocene'}), 403
    data = request.get_json()
    response, status_code = SchoolService.create_grade(current_user['user_id'], data)
    return jsonify(response), status_code


@grade_bp.route('/grades/export-pdf', methods=['GET'])
@token_required
def export_grades(current_user):
    if current_user['role'] != 'UCENIK':
        return jsonify({'message': 'Samo učenici mogu preuzeti svedočanstvo'}), 403
    
    pdf_bytes = SchoolService.export_grades_to_pdf(current_user['user_id'])
    
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment;filename=svedocanstvo.pdf"}
    )

@grade_bp.route('/grades', methods=['GET'])
@token_required
def get_grades(current_user):
    response, status_code = SchoolService.get_grades_for_user(current_user['user_id'], current_user['role'])
    return response, status_code
