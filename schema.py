from datetime import datetime
from typing import Dict, List
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
    def __init__(self, job_id: str, applicant_id: str, answers: list[str], status: str = 'pending'):
        self.id = str(uuid.uuid4())
        self.job_id = job_id
        self.applicant_id = applicant_id
        self.answers = answers
        self.status = status  # 'pending', 'accepted', 'rejected'
        self.created_at = datetime.now()

    def to_dict(self):
        return {
            'id': self.id,
            'job_id': self.job_id,
            'applicant_id': self.applicant_id,
            'answers': self.answers,
            'status': self.status,
            'created_at': self.created_at
        }

class JobPosting:
    def __init__(self, title: str, description: str, recruiter_id: str, job_qualities: str, questions: List[Dict[str, str]]):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.recruiter_id = recruiter_id
        self.job_qualities = job_qualities
        self.questions = questions
        self.created_at = datetime.now()

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'recruiter_id': self.recruiter_id,
            'job_qualities': self.job_qualities,
            'questions': self.questions,
            'created_at': self.created_at
        }