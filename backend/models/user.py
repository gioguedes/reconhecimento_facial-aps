from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
import json

@dataclass
class User:
    name: str
    permission_level: int
    face_encodings: List[List[float]]
    mfa_secret: Optional[str] = None
    enrolled_date: Optional[str] = None
    last_access: Optional[str] = None
    failed_attempts: int = 0
    lockout_until: Optional[float] = None

    def __post_init__(self):
        if not self.enrolled_date:
            self.enrolled_date = datetime.now().isoformat()

    def requires_mfa(self):
        return self.permission_level >= 2

    def is_locked_out(self):
        if not self.lockout_until:
            return False
        return datetime.now().timestamp() < self.lockout_until

    def reset_failed_attempts(self):
        self.failed_attempts = 0
        self.lockout_until = None

    def increment_failed_attempts(self, lockout_duration=300):
        self.failed_attempts += 1
        if self.failed_attempts >= 3:
            self.lockout_until = datetime.now().timestamp() + lockout_duration

    def update_last_access(self):
        self.last_access = datetime.now().isoformat()

    def to_dict(self):
        return {
            'name': self.name,
            'permission_level': self.permission_level,
            'enrolled_date': self.enrolled_date,
            'last_access': self.last_access,
            'requires_mfa': self.requires_mfa()
        }

class UserEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, User):
            return {
                'name': obj.name,
                'permission_level': obj.permission_level,
                'face_encodings': obj.face_encodings,
                'mfa_secret': obj.mfa_secret,
                'enrolled_date': obj.enrolled_date,
                'last_access': obj.last_access,
                'failed_attempts': obj.failed_attempts,
                'lockout_until': obj.lockout_until
            }
        return super().default(obj)

@dataclass
class UserResponse:
    success: bool
    message: str
    data: Optional[dict] = None
    error: Optional[str] = None

    def to_dict(self):
        response = {'success': self.success, 'message': self.message}
        if self.data:
            response['data'] = self.data
        if self.error:
            response['error'] = self.error
        return response
