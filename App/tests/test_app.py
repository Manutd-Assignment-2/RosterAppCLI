import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash
from App.main import create_app
from App.database import db, create_db
from datetime import datetime
from App.models import User, Schedule, Shift
from App.controllers import (
    create_user,
    get_all_users_json,
    login,
    get_user,
    update_user,
    schedule_shift, 
    get_shift_report,
    get_combined_roster,
    clock_in

)


LOGGER = logging.getLogger(__name__)

'''
   Unit Tests
'''



class UserUnitTests(unittest.TestCase):

# User unit tests
    def test_new_user_admin(self):
        user = create_user("bot", "bobpass","admin")
        assert user.username == "bot"

    def test_new_user_staff(self):
        user = create_user("pam", "pampass","staff")
        assert user.username == "pam"

    def test_create_user_invalid_role(self):
        user = create_user("jim", "jimpass","ceo")
        assert user == None


    def test_get_json(self):
        user = User("bob", "bobpass", "admin")
        user_json = user.get_json()
        self.assertDictEqual(user_json, {"id":None, "username":"bob", "role":"admin"})
    
    def test_hashed_password(self):
        password = "mypass"
        user = User(username="tester", password=password)
        assert user.password != password
        assert user.check_password(password) is True

    def test_check_password(self):
        password = "mypass"
        user = User("bob", password)
        assert user.check_password(password)
# Admin unit tests
    def test_schedule_shift_valid(self):
        admin = create_user("admin1", "adminpass", "admin")
        staff = create_user("staff1", "staffpass", "staff")
        schedule = Schedule(name="Morning Schedule", created_by=admin.id)
        db.session.add(schedule)
        db.session.commit()

        start = datetime(2025, 10, 22, 8, 0, 0)
        end = datetime(2025, 10, 22, 16, 0, 0)

        shift = schedule_shift(admin.id, staff.id, schedule.id, start, end)

        assert shift.staff_id == staff.id
        assert shift.schedule_id == schedule.id
        assert shift.start_time == start
        assert shift.end_time == end
        assert isinstance(shift, Shift)

    def test_schedule_shift_invalid(self):
        admin = User("admin2", "adminpass", "admin")
        staff = User("staff2", "staffpass", "staff")
        invalid_schedule_id = 999

        start = datetime(2025, 10, 22, 8, 0, 0)
        end = datetime(2025, 10, 22, 16, 0, 0)
        try:
            shift = schedule_shift(admin.id, staff.id, invalid_schedule_id, start, end)
            assert shift is None  
        except Exception:
            assert True

    def test_get_shift_report(self):
        admin = create_user("superadmin", "superpass", "admin")
        staff = create_user("worker1", "workerpass", "staff")
        db.session.add_all([admin, staff])
        db.session.commit()

        schedule = Schedule(name="Weekend Schedule", created_by=admin.id)
        db.session.add(schedule)
        db.session.commit()

        shift1 = schedule_shift(admin.id, staff.id, schedule.id,
                                datetime(2025, 10, 26, 8, 0, 0),
                                datetime(2025, 10, 26, 16, 0, 0))
        shift2 = schedule_shift(admin.id, staff.id, schedule.id,
                                datetime(2025, 10, 27, 8, 0, 0),
                                datetime(2025, 10, 27, 16, 0, 0))
        
        report = get_shift_report(admin.id)
        assert len(report) >= 2
        assert report[0]["staff_id"] == staff.id
        assert report[0]["schedule_id"] == schedule.id

    def test_get_shift_report_invalid(self):
        non_admin = User("randomstaff", "randompass", "staff")

        try:
            get_shift_report(non_admin.id)
            assert False, "Expected PermissionError for non-admin user"
        except PermissionError as e:
            assert str(e) == "Only admins can view shift reports"
# Staff unit tests
    def test_get_combined_roster_valid(self):
        staff = create_user("staff3", "pass123", "staff")
        admin = create_user("admin3", "adminpass", "admin")
        schedule = Schedule(name="Test Schedule", created_by=admin.id)
        db.session.add(schedule)
        db.session.commit()

        # create a shift
        shift = schedule_shift(admin.id, staff.id, schedule.id,
                               datetime(2025, 10, 23, 8, 0, 0),
                               datetime(2025, 10, 23, 16, 0, 0))

        roster = get_combined_roster(staff.id)
        assert len(roster) >= 1
        assert roster[0]["staff_id"] == staff.id
        assert roster[0]["schedule_id"] == schedule.id

    def test_get_combined_roster_invalid(self):
        non_staff = create_user("admin4", "adminpass", "admin")
        try:
            get_combined_roster(non_staff.id)
            assert False, "Expected PermissionError for non-staff"
        except PermissionError as e:
            assert str(e) == "Only staff can view roster"






'''
    Integration Tests
'''
@pytest.fixture(autouse=True)
def clean_db():
    db.drop_all()
    create_db()
    yield
# This fixture creates an empty database for the test and deletes it after the test
# scope="class" would execute the fixture once and resued for all methods in the class
@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    create_db()
    yield app.test_client()
    db.drop_all()


def test_authenticate():
    user = User("bob", "bobpass","user")
    assert login("bob", "bobpass") != None

class UsersIntegrationTests(unittest.TestCase):

    def test_get_all_users_json(self):
        user = create_user("bot", "bobpass","admin")
        user = create_user("pam", "pampass","staff")
        users_json = get_all_users_json()
        self.assertListEqual([{"id":1, "username":"bot", "role":"admin"}, {"id":2, "username":"pam","role":"staff"}], users_json)

    # Tests data changes in the database
    def test_update_user(self):
        user = create_user("bot", "bobpass","admin")
        update_user(1, "ronnie")
        user = get_user(1)
        assert user.username == "ronnie"
        

