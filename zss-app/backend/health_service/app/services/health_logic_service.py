from flask import current_app
from ..extensions import mongo
from bson import ObjectId, json_util
import json
import requests
from fpdf import FPDF

class HealthService:

    @staticmethod
    def schedule_appointment(patient_id, data):
        mongo.db.appointments.insert_one({'patient_id': patient_id, 'doctor_id': data['doctor_id'], 'date': data['date'], 'status': 'ZAKAZAN'})
        return {'message': 'Pregled uspešno zakazan'}, 201

    @staticmethod
    def get_appointments_for_user(user_id, user_role):
        query = {'patient_id': user_id} if user_role in ['PACIJENT', 'UCENIK', 'RODITELJ'] else {'doctor_id': user_id}
        appointments_cursor = mongo.db.appointments.find(query)
        return json.loads(json_util.dumps(list(appointments_cursor))), 200

    @staticmethod
    def create_justification_request(data):
        from ..models.justification_request_model import JustificationRequest
        new_request = JustificationRequest(student_id=data['student_id'], doctor_id=data['doctor_id'], absence_id=data['absence_id'], reason_from_student=data['reason_from_student'])
        mongo.db.justification_requests.insert_one(new_request.to_document())
        return {'message': 'Zahtev za opravdanje uspešno kreiran'}, 201

    @staticmethod
    def get_justification_requests_for_doctor(doctor_id):
        requests_cursor = mongo.db.justification_requests.find({'doctor_id': doctor_id})
        return json.loads(json_util.dumps(list(requests_cursor))), 200

    @staticmethod
    def process_justification_request(request_id, doctor_id, new_status, config):
        if new_status not in ["ODOBREN", "ODBIJEN"]:
            return {'message': 'Nevažeći status'}, 400

        update_result = mongo.db.justification_requests.find_one_and_update(
            {'_id': ObjectId(request_id), 'doctor_id': doctor_id},
            {'$set': {'status': new_status}},
            return_document=True
        )

        if not update_result:
            return {'message': 'Zahtev nije pronađen ili nemate ovlašćenje'}, 404

        pdf_bytes = None
        if new_status == "ODOBREN":
            sso_url = config['SSO_SERVICE_URL']
            try:
                student_id_str = str(update_result['student_id'])
                doctor_id_str = str(update_result['doctor_id'])

                student_res = requests.get(f"{sso_url}/users/{student_id_str}")
                student_res.raise_for_status()
                
                doctor_res = requests.get(f"{sso_url}/users/{doctor_id_str}")
                doctor_res.raise_for_status()

                student_name = student_res.json().get('name', 'Nepoznat učenik')
                doctor_name = doctor_res.json().get('name', 'Nepoznat lekar')
            except requests.exceptions.RequestException as e:
                print(f"!!! GREŠKA pri pozivu SSO servisa: {e}", flush=True)
                student_name = f"ID: {update_result['student_id']}"
                doctor_name = f"ID: {update_result['doctor_id']}"
            
            pdf = FPDF()
            pdf.add_page()
            pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
            pdf.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf', uni=True)
            
            pdf.set_font('DejaVu', 'B', 16)
            pdf.cell(200, 10, txt="Lekarsko Opravdanje", ln=True, align='C')
            pdf.ln(20)

            pdf.set_font('DejaVu', '', 12)
            pdf.multi_cell(0, 10, f"Potvrđuje se da je učenik, {student_name}, bio sprečen da pohađa nastavu zbog zdravstvenih razloga.")
            pdf.ln(20)
            pdf.cell(0, 10, f"Lekar: {doctor_name}", align='R')
            
            pdf_bytes = bytes(pdf.output())

        try:
            school_url = f"{config['SCHOOL_SERVICE_URL']}/absences/update-status"
            print(f"--- Slanje PUT zahteva na: {school_url}", flush=True)

            files = {'pdf_file': ('opravdanje.pdf', pdf_bytes, 'application/pdf')} if pdf_bytes else None
            payload = {
                'absence_id': str(update_result['absence_id']),
                'new_status': 'OPRAVDANO' if new_status == 'ODOBREN' else 'ODBIJEN'
            }
            response = requests.put(school_url, data=payload, files=files)
            response.raise_for_status()
            
        except requests.exceptions.RequestException as e:
            mongo.db.justification_requests.update_one(
                {'_id': ObjectId(request_id)}, {'$set': {'status': 'ZAPRIMLJEN'}}
            )
            return {'message': 'Greška pri komunikaciji sa školskim servisom', 'error': str(e)}, 500
        
        return {'message': f'Zahtev uspešno {new_status.lower()}'}, 200