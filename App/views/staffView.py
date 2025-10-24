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
# app/views/staff_views.py
from flask import Blueprint, jsonify
from App.controllers import staff
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError

staff_views = Blueprint('staff_views', __name__, template_folder='../templates')

# Staff view roster route
@staff_views.route('/staff/roster', methods=['GET'])
@jwt_required()
def view_roster():
    try:
        staff_id = get_jwt_identity()  # get the user id stored in JWT
        # staffData = staff.get_user(staff_id).get_json()  # Fetch staff data
        roster = staff.get_combined_roster(staff_id)  # staff.get_combined_roster should return the json data of the roseter
        return jsonify(roster), 200
    except SQLAlchemyError:
        return jsonify({"error": "Database error"}), 500

# Staff Clock in endpoint
@staff_views.route('/staff/clock_in/<int:shift_id>', methods=['POST'])
@jwt_required()
def clock_in(shift_id):
    try:
        staff_id = get_jwt_identity()
        shift = staff.clock_in(staff_id, shift_id)  # Call controller
        return jsonify(shift.get_json()), 200
    except (PermissionError, ValueError) as e:
        return jsonify({"error": str(e)}), 403
    except SQLAlchemyError:
        return jsonify({"error": "Database error"}), 500


# Staff Clock in endpoint
@staff_views.route('/staff/clock_out/<int:shift_id>', methods=['POST'])
@jwt_required()
def clock_out(shift_id):
    try:
        staff_id = get_jwt_identity()
        shift = staff.clock_out(staff_id, shift_id)  # Call controller
        return jsonify(shift.get_json()), 200
    except (PermissionError, ValueError) as e:
        return jsonify({"error": str(e)}), 403
    except SQLAlchemyError:
        return jsonify({"error": "Database error"}), 500