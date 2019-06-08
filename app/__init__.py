import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_datepicker import datepicker
from flask_mail import Mail
from config import app_config
import time


project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_file = os.path.join(project_dir, 'database.db')

if os.path.exists(db_file):
    os.remove(db_file)

database_file = "sqlite:///{}".format(os.path.join(project_dir, "database.db"))

app = Flask(__name__, instance_relative_config=True)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
datepicker(app)
login_manager = LoginManager()
mail = Mail(app)


@app.template_filter('date_to_millis')
def date_to_millis(d):
    """Converts a datetime object to the number of milliseconds since the unix epoch."""
    return int(time.mktime(d.timetuple())) * 1000


def create_app(config_name):
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')

    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_message = 'You must be logged in to access this page'
    login_manager.login_view = "auth.login"

    # migrate = Migrate(app,db)
    Bootstrap(app)

    from app.models import (User, Preferences, Role, MeterReading, Meter,
							Building, Class, Login, Timeslot, Timetable,
							Booking, CSBEvent)
    from data_sources import get_data_sources

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint,url_prefix='/admin')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .home import home as home_blueprint
    app.register_blueprint(home_blueprint)

    with app.app_context():
        db.create_all()

        # fake objects used for testing
        role1 = Role(name='Student')
        role2 = Role(name='General Staff')
        role3 = Role(name='Lecturer')

        pref1 = Preferences(number_of_people=5, is_quiet=False, has_pc=True, wants_event_notifications=False)
        user1 = User(email='admin@admin.com', username='admin', password='admin', is_admin=True, first_name="Admin",
                     last_name="Admin", preferences=pref1)
        user2 = User(first_name='Ciaran', last_name='Duncan', email='ciaran.duncan@gmail.com', username='ciaran.duncan@gmail.com', password='password', year_group=1)
        user3 = User(first_name='Domhnall', last_name='Boyle', email='domhnallboyle@gmail.com', username='domhnallboyle@gmail.com', password='password', year_group=2)
        user4 = User(first_name='Joe', last_name='Cargill', email='jcargill01@qub.ac.uk', username='jcargill01@qub.ac.uk', password='password', year_group=3)
        user5 = User(first_name='Robert', last_name='Henzel', email='rhenzel01@qub.ac.uk', username='rhenzel01@qub.ac.uk', password='password', year_group=4)

        objects = [
            # roles
            role1, role2, role3,

			# users
			user1, user2, user3, user4, user5
        ] + get_data_sources()

        db.session.add_all(objects)
        db.session.commit()

        build_room_slots()

	return app


def build_room_slots():
    """
    Populate every room with an empty booking slot for every hour. 
    Every booking slot can hold a multiple days bookings for that hour.
    """
    from .models import Booking, BookingSlots, BookingRoom, Room

    bookable_room_ids = [14, 15, 16, 18, 23, 24]
    all_rooms = Room.query.filter(Room.id.in_(bookable_room_ids)).all()
    if all_rooms:
        all_rooms.sort(key=lambda r : r.id)

        bookable_rooms = []
        for r in all_rooms:
            bookable_rooms.append(BookingRoom(name=r.name))

        if bookable_rooms:
            bookable_rooms[0].is_quiet = False
            bookable_rooms[0].has_pc = False
            bookable_rooms[0].has_hdmi = True
            bookable_rooms[0].has_window = True
            bookable_rooms[0].max_occupancy= 8

            bookable_rooms[1].is_quiet = False
            bookable_rooms[1].has_pc = False
            bookable_rooms[1].has_hdmi = True
            bookable_rooms[1].has_window = True
            bookable_rooms[1].max_occupancy= 8

            bookable_rooms[2].is_quiet = False
            bookable_rooms[2].has_pc = False
            bookable_rooms[2].has_hdmi = True
            bookable_rooms[2].has_window = True
            bookable_rooms[2].max_occupancy= 8

            bookable_rooms[3].is_quiet = True
            bookable_rooms[3].has_pc = True
            bookable_rooms[3].has_hdmi = False
            bookable_rooms[3].has_window = False
            bookable_rooms[3].max_occupancy= 10

            bookable_rooms[4].is_quiet =  True
            bookable_rooms[4].has_pc = False
            bookable_rooms[4].has_hdmi = True
            bookable_rooms[4].has_window = True
            bookable_rooms[4].max_occupancy= 8

            bookable_rooms[5].is_quiet = True
            bookable_rooms[5].has_pc = False
            bookable_rooms[5].has_hdmi = True
            bookable_rooms[5].has_window = True
            bookable_rooms[5].max_occupancy= 8


            for room in bookable_rooms:
                db.session.add(room)
            db.session.commit()

    else:
        # placeholder before real rooms imported
        for r in range(0,4):

            name = 'room {}'.format(r)
            room = BookingRoom(name=name, max_occupancy=4)

            db.session.add(room)

        name = 'room with PC'
        pcroom = BookingRoom(name=name, max_occupancy=8, has_pc=True)
        db.session.add(pcroom)

        db.session.commit()  

    rooms = BookingRoom.query.all()


    for room in rooms:
        days = []
        for s in range(0,7):
            slots = BookingSlots()
            for b in range(0,24):
                empty = Booking(user_id=None)
                slots.bookings.append(empty)
            
            days.append(slots)
        room.slots = days

        db.session.add(room)
        db.session.commit()
    
