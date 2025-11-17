from datetime import datetime

from werkzeug.security import generate_password_hash


class User:
    """User model for the application."""
    
    def __init__(self, email, password, role='user', is_hashed=False):
        self.email = email
        self.password = generate_password_hash(password) if not is_hashed else password
        self.role = role
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert user object to dictionary."""
        return {
            'email': self.email,
            'password': self.password,
            'role': self.role,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def from_dict(data):
        """Create user object from dictionary."""
        user = User(
            email=data.get('email'),
            password=data.get('password'),
            role=data.get('role', 'user'),
            is_hashed=True
        )
        if 'created_at' in data:
            user.created_at = data['created_at']
        if 'updated_at' in data:
            user.updated_at = data['updated_at']
        return user