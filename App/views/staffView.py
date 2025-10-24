# app/views/staff_views.py
from flask import Blueprint, jsonify, request
from App.controllers import staff, auth
from sqlalchemy.exc import SQLAlchemyError

staff_views = Blueprint('staff_views', __name__, template_folder='../templates')

#Based on the controllers in App/controllers/staff.py, staff can do the following actions:
# 1. View combined roster
# 2. Clock in 
# 3. Clock out
# 4. View specific shift details

#Staff authentication decorator
def staff_required(f):
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Authorization token is missing"}), 401
        try:
            staff_id = auth.verify_token(token)
            return f(staff_id, *args, **kwargs)
        except PermissionError as e:
            return jsonify({"error": str(e)}), 403
    wrapper.__name__ = f.__name__
    return wrapper

#Staff View Roster endpoint
@staff_views.route('/staff/roster', methods=['GET'])
@staff_required
def view_roster(staff_id):
    try:
        roster = staff.get_combined_roster(staff_id) # Call the staff.view_roster controller
        return jsonify(roster), 200 # "get_combined_roster" returns a list of shifts in JSON format || HTTP 200 = OK
    except SQLAlchemyError as e:
        return jsonify({"error": "Database error"}), 500

#Staff Clock in endpoint
@staff_views.route('/staff/clock_in/<int:shift_id>', methods=['POST'])
@staff_required
def clock_in(staff_id, shift_id):
    try:
        shift = staff.clock_in(staff_id, shift_id) # Call the staff.clock_in controller
        return jsonify(shift.get_json()), 200 # Return the shift details as JSON || HTTP 200 = OK
    except (PermissionError, ValueError) as e:
        return jsonify({"error": str(e)}), 403
    except SQLAlchemyError as e:
        return jsonify({"error": "Database error"}), 500

#Staff Clock out endpoint
@staff_views.route('/staff/clock_out/<int:shift_id>', methods=['POST'])
@staff_required
def clock_out(staff_id, shift_id):
    try:
        shift = staff.clock_out(staff_id, shift_id) # Call the staff.clock_out controller
        return jsonify(shift.get_json()), 200 # Return the shift details as JSON || HTTP 200 = OK
    except (PermissionError, ValueError) as e:
        return jsonify({"error": str(e)}), 403
    except SQLAlchemyError as e:
        return jsonify({"error": "Database error"}), 500