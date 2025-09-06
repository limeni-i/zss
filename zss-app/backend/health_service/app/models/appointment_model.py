from datetime import datetime
from enum import Enum

class AppointmentStatus(Enum):
    ZAKAZAN = "ZAKAZAN"
    OTKAZAN = "OTKAZAN"
    ZAVRSEN = "ZAVRSEN"

class Appointment:
    def __init__(self, patient_id, doctor_id, date, status=AppointmentStatus.ZAKAZAN.value):
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.date = date
        self.status = status

    def to_document(self):
        return self.__dict__