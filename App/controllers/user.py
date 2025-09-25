from App.models import User, Admin, Staff, Shift
from App.database import db
from datetime import datetime

VALID_ROLES = {"user", "staff", "admin"}

def create_user(username, password, role):
    role = role.lower().strip()
    if role not in VALID_ROLES:
        raise ValueError(f"Invalid role '{role}'. Must be one of {VALID_ROLES}")
    
    if role == "admin":
        newuser = Admin(username=username, password=password)
    elif role == "staff":
        newuser = Staff(username=username, password=password)
    else:
        newuser = User(username=username, password=password, role="user")
    
    db.session.add(newuser)
    db.session.commit()
    return newuser

def get_user_by_username(username):
    return User.query.filter_by(username=username).first()

def get_user(id):
    return db.session.get(User, id)

def get_all_users():
    return User.query.all()

def get_all_users_json():
    users = get_all_users()
    if not users:
        return []
    return [user.get_json() for user in users]

def update_user(id, username):
    user = get_user(id)
    if user:
        user.username = username
        db.session.commit()
        return user
    return None



def schedule_shift(admin_id, staff_id, start_time, end_time):
    admin = get_user(admin_id)
    staff = get_user(staff_id)
    if not admin or admin.role != "admin":
        raise PermissionError("Only admins can schedule shifts")
    if not staff or staff.role != "staff":
        raise ValueError("Invalid staff member")

    new_shift = Shift(staff_id=staff_id, start_time=start_time, end_time=end_time)
    db.session.add(new_shift)
    db.session.commit()
    return new_shift

def get_combined_roster(staff_id):
    staff = get_user(staff_id)
    if not staff or staff.role != "staff":
        raise PermissionError("Only staff can view roster")
    return [shift.get_json() for shift in Shift.query.order_by(Shift.start_time).all()]

def clock_in(staff_id, shift_id):
    staff = get_user(staff_id)
    if not staff or staff.role != "staff":
        raise PermissionError("Only staff can clock in")
    shift = db.session.get(Shift, shift_id)
    if not shift or shift.staff_id != staff_id:
        raise ValueError("Invalid shift for staff")
    shift.clock_in = datetime.now()
    db.session.commit()
    return shift

def clock_out(staff_id, shift_id):
    staff = get_user(staff_id)
    if not staff or staff.role != "staff":
        raise PermissionError("Only staff can clock out")
    shift = db.session.get(Shift, shift_id)
    if not shift or shift.staff_id != staff_id:
        raise ValueError("Invalid shift for staff")
    shift.clock_out = datetime.now()
    db.session.commit()
    return shift

def get_shift_report(admin_id):
    admin = get_user(admin_id)
    if not admin or admin.role != "admin":
        raise PermissionError("Only admins can view shift reports")
    return [shift.get_json() for shift in Shift.query.order_by(Shift.start_time).all()]
