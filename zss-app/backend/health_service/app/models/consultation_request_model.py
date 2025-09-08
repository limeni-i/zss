from datetime import datetime

class ConsultationRequest:
    def __init__(self, teacher_id, student_id, doctor_id, message):
        self.teacher_id = teacher_id
        self.student_id = student_id
        self.doctor_id = doctor_id
        self.message = message
        self.status = "POSLAT"
        self.created_at = datetime.now()
    
    def to_document(self):
        return self.__dict__