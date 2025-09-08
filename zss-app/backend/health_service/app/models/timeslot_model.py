from datetime import datetime

class TimeSlot:
    def __init__(self, doctor_id, start_time, end_time):
        self.doctor_id = doctor_id
        self.start_time = start_time
        self.end_time = end_time
        self.status = "SLOBODAN"
        self.patient_id = None
        self.title = "Slobodan termin"