from flask import Blueprint, request, jsonify, Response
from .decorators import token_required
from ..services.school_logic_service import SchoolService
from flask import send_file

absence_bp = Blueprint('absence_bp', __name__)

@absence_bp.route('/absences', methods=['POST'])
@token_required
def record_absence(current_user):
    if current_user['role'] != 'NASTAVNIK':
        return jsonify({'message': 'Samo nastavnici mogu evidentirati izostanke'}), 403
    data = request.get_json()
    response, status_code = SchoolService.record_absence(current_user['user_id'], data)
    return jsonify(response), status_code

@absence_bp.route('/absences', methods=['GET'])
@token_required
def get_absences(current_user):
    response, status_code = SchoolService.get_absences_for_user(current_user['user_id'], current_user['role'])
    return response, status_code

@absence_bp.route('/absences/<absence_id>/request-justification', methods=['POST'])
@token_required
def request_justification(current_user, absence_id):
    if current_user['role'] != 'UCENIK':
        return jsonify({'message': 'Samo učenici mogu tražiti opravdanje'}), 403
    data = request.get_json()
    response, status_code = SchoolService.request_justification(absence_id, current_user['user_id'], data)
    return jsonify(response), status_code
 
@absence_bp.route('/absences/update-status', methods=['PUT'])
def update_status_from_doctor():
    pdf_file = request.files.get('pdf_file')
    data = request.form.to_dict()
    response, status_code = SchoolService.update_absence_status_from_doctor(pdf_file, data)
    return jsonify(response), status_code


@absence_bp.route('/absences/<absence_id>/download-justification', methods=['GET'])
@token_required
def download_justification(current_user, absence_id):
    if current_user['role'] != 'NASTAVNIK':
        return jsonify({'message': 'Pristup odbijen'}), 403
    
    pdf_bytes = SchoolService.get_justification_pdf(absence_id, current_user['user_id'])
    
    if not pdf_bytes:
        return jsonify({'message': 'Fajl nije pronađen'}), 404
    
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment;filename=opravdanje.pdf"}
    )