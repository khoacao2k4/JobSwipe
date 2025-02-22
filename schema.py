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
    
class Application:
    def __init__(self, job_id: str, applicant_id: str, status: str = 'pending'):
        self.id = str(uuid.uuid4())
        self.job_id = job_id
        self.applicant_id = applicant_id
        self.status = status  # 'pending', 'accepted', 'rejected'
        self.created_at = datetime.now()

    def to_dict(self):
        return {
            'id': self.id,
            'job_id': self.job_id,
            'applicant_id': self.applicant_id,
            'status': self.status,
            'created_at': self.created_at
        }