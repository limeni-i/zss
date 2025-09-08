from ..extensions import mongo
from bson import ObjectId, json_util
import json
import requests
from flask import current_app
from fpdf import FPDF
import gridfs

class SchoolService:

    @staticmethod
    def create_grade(teacher_id, data):
        mongo.db.grades.insert_one({'student_id': data['student_id'], 'teacher_id': teacher_id, 'subject': data['subject'], 'value': data['value'], 'date': data['date']})
        return {'message': 'Ocena uspešno uneta'}, 201

    @staticmethod
    def get_grades_for_user(user_id, user_role):
        query = {'student_id': user_id} if user_role == 'UCENIK' else {'teacher_id': user_id}
        grades_cursor = mongo.db.grades.find(query)
        return json.loads(json_util.dumps(list(grades_cursor))), 200

    @staticmethod
    def record_absence(teacher_id, data):
        from ..models.absence_model import Absence
        new_absence = Absence(student_id=data['student_id'], teacher_id=teacher_id, date_from=data['date_from'], date_to=data['date_to'], reason=data.get('reason', 'Nije naveden'))
        mongo.db.absences.insert_one(new_absence.to_document())
        return {'message': 'Izostanak evidentiran'}, 201

    @staticmethod
    def get_absences_for_user(user_id, user_role):
        query = {'student_id': user_id} if user_role == 'UCENIK' else {'teacher_id': user_id}
        absences_cursor = mongo.db.absences.find(query)
        return json.loads(json_util.dumps(list(absences_cursor))), 200

    @staticmethod
    def request_justification(absence_id, student_id, data):
        existing_pending_request = mongo.db.absences.find_one({
            'student_id': student_id,
            'justification_status': 'U_PROCESU'
        })
        
        if existing_pending_request:
            return {'message': 'Već imate jedan zahtev za opravdanje na čekanju. Molimo sačekajte da se on obradi.'}, 400

        mongo.db.absences.update_one(
            {'_id': ObjectId(absence_id), 'student_id': student_id},
            {'$set': {
                'justification_status': 'U_PROCESU',
                'requested_doctor_id': data['doctor_id']
            }}
        )

        health_service_url = f"{current_app.config['HEALTH_SERVICE_URL']}/justifications/request"
        try:
            payload = {
                'student_id': student_id,
                'doctor_id': data['doctor_id'],
                'absence_id': absence_id,
                'reason_from_student': data.get('reason', 'Molim za opravdanje.')
            }
            response = requests.post(health_service_url, json=payload)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            mongo.db.absences.update_one(
                {'_id': ObjectId(absence_id)},
                {'$set': {'justification_status': 'NIJE_ZATRAZENO', 'requested_doctor_id': None}}
            )
            return {'message': 'Greška pri slanju zahteva lekaru', 'error': str(e)}, 500
            
        return {'message': 'Zahtev za opravdanje uspešno poslat'}, 200

    @staticmethod
    def update_absence_status_from_doctor(pdf_file, data):
        absence_id = data['absence_id']
        new_status = data['new_status']

        update_data = {
            'justification_status': new_status,
            'is_excused': new_status == 'OPRAVDANO'
        }

        if pdf_file:
            fs = gridfs.GridFS(mongo.db)
            pdf_id = fs.put(pdf_file.read(), filename=pdf_file.filename)
            update_data['justification_pdf_id'] = str(pdf_id)

        updated_absence = mongo.db.absences.find_one_and_update(
            {'_id': ObjectId(absence_id)},
            {'$set': update_data},
            return_document=True
        )

        if not updated_absence:
            return {'message': 'Izostanak za ažuriranje nije pronađen'}, 404
        
        if new_status == 'OPRAVDANO':
            from ..models.message_model import Message

            teacher_id = updated_absence.get('teacher_id')
            student_id = updated_absence.get('student_id')
            message_content = f"Izostanak za učenika (ID: {student_id}) je opravdan od strane lekara. Opravdanje je dostupno za preuzimanje na panelu."

            new_message = Message(
                sender_id="SISTEM",
                receiver_id=teacher_id,
                content=message_content,
                sender_role="SISTEM",
                receiver_role="NASTAVNIK"
            )
            mongo.db.messages.insert_one(new_message.to_document())
        return {'message': 'Status izostanka ažuriran'}, 200

    @staticmethod
    def send_message(sender_id, sender_role, data):
        from ..models.message_model import Message
        new_message = Message(sender_id=sender_id, receiver_id=data['receiver_id'], content=data['content'], sender_role=sender_role, receiver_role=data['receiver_role'])
        mongo.db.messages.insert_one(new_message.to_document())
        return {'message': 'Poruka poslata'}, 201

    @staticmethod
    def get_conversation(user1_id, user2_id):
        query = {'$or': [{'sender_id': user1_id, 'receiver_id': user2_id}, {'sender_id': user2_id, 'receiver_id': user1_id}]}
        messages_cursor = mongo.db.messages.find(query).sort('timestamp', 1)
        return json.loads(json_util.dumps(list(messages_cursor))), 200
    
    @staticmethod
    def get_justification_pdf(absence_id, teacher_id):
        absence = mongo.db.absences.find_one({'_id': ObjectId(absence_id), 'teacher_id': teacher_id})
        if not absence or 'justification_pdf_id' not in absence:
            return None
        
        fs = gridfs.GridFS(mongo.db)
        pdf_id = ObjectId(absence['justification_pdf_id'])
        pdf_file_object = fs.get(pdf_id)
        return pdf_file_object.read()

    @staticmethod
    def export_grades_to_pdf(student_id):
        grades = list(mongo.db.grades.find({'student_id': student_id}))
        sso_url = current_app.config['SSO_SERVICE_URL']
        try:
            student_res = requests.get(f"{sso_url}/users/{student_id}")
            student_name = student_res.json().get('name', 'Nepoznat učenik')
        except Exception:
            student_name = f"Učenik ID: {student_id}"
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
        pdf.set_font('DejaVu', '', 16)
        pdf.cell(200, 10, txt="Svedočanstvo", ln=True, align='C')
        pdf.cell(200, 10, txt=student_name, ln=True, align='C') 
        pdf.ln(10)
        pdf.set_font('DejaVu', '', 12)
        pdf.cell(80, 10, "Predmet", 1)
        pdf.cell(30, 10, "Ocena", 1)
        pdf.cell(50, 10, "Datum", 1)
        pdf.ln()
        for grade in grades:
            try:
                pdf.cell(80, 10, grade['subject'], 1)
            except UnicodeEncodeError:
                pdf.cell(80, 10, grade['subject'].encode('latin-1', 'replace').decode('latin-1'), 1)
            pdf.cell(30, 10, str(grade['value']), 1)
            pdf.cell(50, 10, grade['date'], 1)
            pdf.ln()
        return bytes(pdf.output())
    
    
    @staticmethod
    def send_consultation_request(teacher_id, data):
        health_url = f"{current_app.config['HEALTH_SERVICE_URL']}/consultations/request"
        try:
            payload = {
                'teacher_id': teacher_id,
                'student_id': data['student_id'],
                'doctor_id': data['doctor_id'],
                'message': data['message']
            }
            response = requests.post(health_url, json=payload)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return {'message': 'Greška pri slanju zahteva zdravstvenom sistemu', 'error': str(e)}, 500
        return {'message': 'Zahtev uspešno poslat'}, 200