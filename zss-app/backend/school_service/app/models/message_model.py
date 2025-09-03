from datetime import datetime

class Message:
    def __init__(self, sender_id, receiver_id, content, sender_role, receiver_role):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.sender_role = sender_role
        self.receiver_role = receiver_role
        self.content = content
        self.timestamp = datetime.now()

    def to_document(self):
        return self.__dict__