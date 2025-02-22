from datetime import datetime
import uuid

class User:
    def __init__(self, email: str, password: str, role: str):
        self.id = str(uuid.uuid4())
        self.email = email
        self.password = password
        self.role = role  # recruiter/applicant
        self.created_at = datetime.now()
        self.profile = None

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'password': self.password,
            'role': self.role,
            'created_at': self.created_at,
            'profile': self.profile
        }