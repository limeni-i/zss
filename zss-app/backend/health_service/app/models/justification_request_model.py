from datetime import datetime

class JustificationRequest:
    def __init__(self, student_id, doctor_id, absence_id, reason_from_student):
        self.student_id = student_id
        self.doctor_id = doctor_id
        self.absence_id = absence_id
        self.reason_from_student = reason_from_student
        self.status = "ZAPRIMLJEN" 
        self.created_at = datetime.utcnow()

    def to_document(self):
        return self.__dict__