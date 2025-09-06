from flask import current_app, jsonify
from ..extensions import mongo
from bson import ObjectId, json_util
import json
import requests



class HealthService:

    @staticmethod
    def schedule_appointment(patient_id, data):
        """Logika za zakazivanje pregleda."""
        mongo.db.appointments.insert_one({
            'patient_id': patient_id,
            'doctor_id': data['doctor_id'],
            'date': data['date'],
            'status': 'ZAKAZAN'
        })
        return {'message': 'Pregled uspešno zakazan'}, 201

    @staticmethod
    def get_appointments_for_user(user_id, user_role):
        """Vraća preglede za pacijenta ili lekara."""
        query = {'patient_id': user_id} if user_role in ['PACIJENT', 'UCENIK', 'RODITELJ'] else {'doctor_id': user_id}
        appointments_cursor = mongo.db.appointments.find(query)
        return json.loads(json_util.dumps(list(appointments_cursor))), 200

    @staticmethod
    def create_justification_request(data):
        """Školski servis poziva ovu metodu da kreira novi zahtev za opravdanje."""
        from ..models.justification_request_model import JustificationRequest
        new_request = JustificationRequest(
            student_id=data['student_id'],
            doctor_id=data['doctor_id'],
            absence_id=data['absence_id'],
            reason_from_student=data['reason_from_student']
        )
        mongo.db.justification_requests.insert_one(new_request.to_document())
        return {'message': 'Zahtev za opravdanje uspešno kreiran'}, 201

    @staticmethod
    def get_justification_requests_for_doctor(doctor_id):
        """Vraća sve zahteve za opravdanje dodeljene lekaru."""
        requests_cursor = mongo.db.justification_requests.find({'doctor_id': doctor_id})
        return json.loads(json_util.dumps(list(requests_cursor))), 200

    @staticmethod
    def process_justification_request(request_id, doctor_id, new_status):
        """Lekar odobrava ili odbija zahtev."""
        if new_status not in ["ODOBREN", "ODBIJEN"]:
            return {'message': 'Nevažeći status'}, 400

        update_result = mongo.db.justification_requests.find_one_and_update(
            {'_id': ObjectId(request_id), 'doctor_id': doctor_id},
            {'$set': {'status': new_status}},
            return_document=True 
        )

        if not update_result:
            return {'message': 'Zahtev nije pronađen ili nemate ovlašćenje'}, 404

        school_service_url = f"{current_app.config['SCHOOL_SERVICE_URL']}/absences/update-status"
        try:
            payload = {
                'absence_id': update_result['absence_id'],
                'new_status': 'OPRAVDANO' if new_status == 'ODOBREN' else 'ODBIJENO'
            }
            response = requests.put(school_service_url, json=payload)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:

            mongo.db.justification_requests.update_one(
                {'_id': ObjectId(request_id)},
                {'$set': {'status': 'ZAPRIMLJEN'}}
            )
            return {'message': 'Greška pri komunikaciji sa školskim servisom', 'error': str(e)}, 500
        
        return {'message': f'Zahtev uspešno {new_status.lower()}'}, 200