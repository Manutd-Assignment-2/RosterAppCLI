from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    
    __mapper_args__ = {
        "polymorphic_identity": "user",
        "polymorphic_on": "role"
    }   
    
    def __init__(self, username, password, role="user"):
        self.username = username
        self.role = role
        self.set_password(password)

    def get_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role
        }

    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)


class Admin(User):
    __mapper_args__ = {
        "polymorphic_identity": "admin",
    }
    
    def __init__(self, username, password):
        super().__init__(username, password, "admin")


class Staff(User):
    __mapper_args__ = {
        "polymorphic_identity": "staff",
    }
    
    def __init__(self, username, password):
        super().__init__(username, password, "staff")


class Shift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    clock_in = db.Column(db.DateTime, nullable=True)
    clock_out = db.Column(db.DateTime, nullable=True)

    staff = db.relationship("Staff", backref="shifts", foreign_keys=[staff_id])

    def get_json(self):
        return {
            "id": self.id,
            "staff_id": self.staff_id,
            "staff_name": self.staff.username if self.staff else None,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "clock_in": self.clock_in.isoformat() if self.clock_in else None,
            "clock_out": self.clock_out.isoformat() if self.clock_out else None
        }
