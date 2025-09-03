class Absence:
    def __init__(self, student_id, teacher_id, date_from, date_to, reason, is_excused=False):
        self.student_id = student_id
        self.teacher_id = teacher_id 
        self.date_from = date_from
        self.date_to = date_to
        self.reason = reason
        self.is_excused = is_excused
        self.justification_status = "NIJE_ZATRAZENO" 
        self.requested_doctor_id = None 

    def to_document(self):
        return self.__dict__