import click, pytest, sys 
from flask.cli import with_appcontext, AppGroup
from datetime import datetime

from App.database import db, get_migrate
from App.models import User
from App.main import create_app
from App.controllers import (
    create_user, get_all_users_json, get_all_users, initialize,
    schedule_shift, get_combined_roster, clock_in, clock_out, get_shift_report
)

app = create_app()
migrate = get_migrate(app)

@app.cli.command("init", help="Creates and initializes the database")
def init():
    initialize()
    print('database intialized')


user_cli = AppGroup('user', help='User object commands') 

@user_cli.command("create", help="Creates a user")
@click.argument("username", default="rob")
@click.argument("password", default="robpass")
@click.argument("role", default="staff")
def create_user_command(username, password, role):
    create_user(username, password, role)
    print(f'{username} created!')

@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == 'string':
        print(get_all_users())
    else:
        print(get_all_users_json())

app.cli.add_command(user_cli)



shift_cli = AppGroup('shift', help='Shift management commands')

@shift_cli.command("schedule", help="Admin schedules a shift")
@click.argument("admin_id", type=int)
@click.argument("staff_id", type=int)
@click.argument("start")
@click.argument("end")
def schedule_shift_command(admin_id, staff_id, start, end):
    start_time = datetime.fromisoformat(start)
    end_time = datetime.fromisoformat(end)
    shift = schedule_shift(admin_id, staff_id, start_time, end_time)
    print(f"Shift scheduled: {shift.get_json()}")

@shift_cli.command("roster", help="Staff views combined roster")
@click.argument("staff_id", type=int)
def roster_command(staff_id):
    roster = get_combined_roster(staff_id)
    print(roster)

@shift_cli.command("clockin", help="Staff clocks in")
@click.argument("staff_id", type=int)
@click.argument("shift_id", type=int)
def clockin_command(staff_id, shift_id):
    shift = clock_in(staff_id, shift_id)
    print(f"Clocked in: {shift.get_json()}")

@shift_cli.command("clockout", help="Staff clocks out")
@click.argument("staff_id", type=int)
@click.argument("shift_id", type=int)
def clockout_command(staff_id, shift_id):
    shift = clock_out(staff_id, shift_id)
    print(f"Clocked out: {shift.get_json()}")

@shift_cli.command("report", help="Admin views shift report")
@click.argument("admin_id", type=int)
def report_command(admin_id):
    report = get_shift_report(admin_id)
    print(report)

app.cli.add_command(shift_cli)

schedule_cli = AppGroup('schedule', help='Schedule management commands')

@schedule_cli.command("create", help="Create a schedule")
@click.argument("name")
@click.argument("admin_id", type=int)
def create_schedule_command(name, admin_id):
    from App.models import Schedule
    from App.controllers import get_user
    admin = get_user(admin_id)
    if not admin or admin.role != "admin":
        raise PermissionError("Only admins can create schedules")
    schedule = Schedule(name=name, created_by=admin_id)
    db.session.add(schedule)
    db.session.commit()
    print(f"Schedule created: {schedule.get_json()}")

@schedule_cli.command("list", help="List all schedules")
def list_schedules_command():
    from App.models import Schedule
    schedules = Schedule.query.all()
    print([s.get_json() for s in schedules])

@schedule_cli.command("view", help="View a schedule and its shifts")
@click.argument("schedule_id", type=int)
def view_schedule_command(schedule_id):
    from App.models import Schedule
    schedule = db.session.get(Schedule, schedule_id)
    if not schedule:
        print("Schedule not found")
    else:
        print(schedule.get_json())

app.cli.add_command(schedule_cli)
'''
Test Commands
'''
test = AppGroup('test', help='Testing commands') 

@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))
    
app.cli.add_command(test)
