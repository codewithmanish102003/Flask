import datetime

from bson.objectid import ObjectId
from werkzeug.security import check_password_hash, generate_password_hash


class User:
    def __init__(self, username, password, created_at=None):
        self.username = username
        self.password_hash = generate_password_hash(password) if password else None
        self.created_at = created_at or datetime.datetime.utcnow()
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            "username": self.username,
            "password": self.password_hash,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        user = cls(
            username=data.get("username"),
            password="",  # We don't store plain text passwords
            created_at=data.get("created_at")
        )
        user.password_hash = data.get("password")
        return user