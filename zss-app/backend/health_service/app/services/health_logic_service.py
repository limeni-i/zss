from flask import current_app
from ..extensions import mongo
from bson import ObjectId, json_util
import json
import requests
from fpdf import FPDF
from ..models.timeslot_model import TimeSlot
from datetime import datetime, timedelta

class HealthService:

    @staticmethod
    def create_timeslots_for_day(doctor_id, data):
        day_str = data['date']
        start_hour = int(data['start_hour'])
        end_hour = int(data['end_hour'])
        
        day = datetime.strptime(day_str, '%Y-%m-%d')
        
        new_slots = []
        current_time = day.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        end_time_of_day = day.replace(hour=end_hour, minute=0, second=0, microsecond=0)

        while current_time < end_time_of_day:
            end_of_slot = current_time + timedelta(minutes=30)
            slot = TimeSlot(
                doctor_id=doctor_id,
                start_time=current_time,
                end_time=end_of_slot
            )
            slot_doc = slot.__dict__

            if slot_doc['title'] == 'Slobodan termin':
                del slot_doc['title']
            new_slots.append(slot_doc)

            current_time = end_of_slot

        if new_slots:
            mongo.db.timeslots.insert_many(new_slots)
        
        return {'message': f'Kreirano {len(new_slots)} novih termina.'}, 201

    @staticmethod
    def get_timeslots_for_doctor(doctor_id):
        slots_cursor = mongo.db.timeslots.find({'doctor_id': doctor_id})
        return json.loads(json_util.dumps(list(slots_cursor))), 200

    @staticmethod
    def get_free_timeslots(doctor_id):
        query = {
            'doctor_id': doctor_id,
            'status': 'SLOBODAN',
            'start_time': {'$gte': datetime.utcnow()} 
        }
        slots_cursor = mongo.db.timeslots.find(query).sort('start_time', 1)
        return json.loads(json_util.dumps(list(slots_cursor))), 200

    @staticmethod
    def book_timeslot(slot_id, patient_id):
        update_result = mongo.db.timeslots.find_one_and_update(
            {'_id': ObjectId(slot_id), 'status': 'SLOBODAN'},
            {'$set': {
                'status': 'REZERVISAN',
                'patient_id': patient_id,
                'title': 'Rezervisan termin'
            }}
        )
        if not update_result:
            return {'message': 'Termin nije dostupan ili ne postoji'}, 409 
        return {'message': 'Termin uspešno rezervisan'}, 200

    @staticmethod
    def get_appointments_for_patient(patient_id):
        slots_cursor = mongo.db.timeslots.find({'patient_id': patient_id})
        return json.loads(json_util.dumps(list(slots_cursor))), 200

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
    
    
    
    @staticmethod
    def check_completed_appointment(data):
        patient_id = data['patient_id']
        doctor_id = data['doctor_id']
        date_from = datetime.strptime(data['date_from'], '%Y-%m-%d')
        date_to = datetime.strptime(data['date_to'], '%Y-%m-%d')

        query = {
            'patient_id': patient_id,
            'doctor_id': doctor_id,
            'status': 'REZERVISAN', 
            'start_time': {
                '$gte': date_from,
                '$lte': date_to + timedelta(days=1)
            }
        }
        appointment = mongo.db.timeslots.find_one(query)
        return {'appointment_exists': appointment is not None}, 200
    
    @staticmethod
    def create_consultation_request(data):
        from ..models.consultation_request_model import ConsultationRequest
        new_req = ConsultationRequest(
            teacher_id=data['teacher_id'], 
            student_id=data['student_id'],
            doctor_id=data['doctor_id'], 
            message=data['message']
        )
        mongo.db.consultation_requests.insert_one(new_req.to_document())
        return {'message': 'Zahtev za konsultacije uspešno poslat'}, 201

    @staticmethod
    def get_consultation_requests_for_doctor(doctor_id):
        req_cursor = mongo.db.consultation_requests.find({'doctor_id': doctor_id})
        return json.loads(json_util.dumps(list(req_cursor))), 200