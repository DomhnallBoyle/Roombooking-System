from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager
from datetime import time

from sqlalchemy import UniqueConstraint


class User(UserMixin, db.Model):
    """
    create an user table
    """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True)
    username = db.Column(db.String(60), index=True, unique=True)
    first_name = db.Column(db.String(60), index=True)
    last_name = db.Column(db.String(60), index=True)
    password_hash = db.Column(db.String(128))

    year_group = db.Column(db.Integer)

    preferences_id = db.Column(db.Integer, db.ForeignKey('preferences.id'))
    preferences = db.relationship('Preferences')

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    role = db.relationship('Role')

    is_admin = db.Column(db.Boolean, default=False)

    room_bookings = db.relationship("RoomBooking", backref="users", lazy='dynamic')

    @property
    def password(self):
        """
        prevent pass from being accessed
        """
        raise AttributeError('password is not a readable attr')

    @password.setter
    def password(self, password):
        """
        set pasword to a hashed pass
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        check hashed password matches actual
        """
        return check_password_hash(self.password_hash, password)

    def __repr__ (self):
        return '<User: {}>'.format(self.username)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Preferences(db.Model):
    """
    create preferences table
    """
    __tablename__ = 'preferences'

    id = db.Column(db.Integer, primary_key=True)
    number_of_people = db.Column(db.Integer)
    is_quiet = db.Column(db.Boolean, default=False)
    has_pc = db.Column(db.Boolean, default=False)
    has_hdmi = db.Column(db.Boolean, default=False)
    has_window = db.Column(db.Boolean, default=False)
    wants_event_notifications = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return '<Preferences: {}>'.format(self.id)


class Role(db.Model):
    """
    create a role table
    """
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)
    description = db.Column(db.String(200))

    def __repr__(self):
        return '<Role: {}>'.format(self.name)


class MeterReading(db.Model):
    __tablename__ = 'meters_readings'

    id = db.Column(db.Integer, primary_key=True)
    meter_reading_date = db.Column(db.DateTime)
    meter_usage_kwh = db.Column(db.Integer)
    block_co2 = db.Column(db.Integer)
    block_cost = db.Column(db.Integer)

    meter_id = db.Column(db.Integer, db.ForeignKey('meters.id'))
    meter = db.relationship('Meter')

    def __repr__(self):
        return '<MeterReading: {}>'.format(self.id)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.meter_reading_date,
            'usage': self.meter_usage_kwh,
            'co2': self.block_co2,
            'cost': self.block_cost
        }


class Meter(db.Model):
    __tablename__ = 'meters'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)

    building_id = db.Column(db.Integer, db.ForeignKey('buildings.id'))
    building = db.relationship('Building')

    meter_readings = db.relationship("MeterReading", backref="meters", lazy='dynamic')

    def __repr__(self):
        return '<Meter: {}>'.format(self.id)


class Building(db.Model):
    __tablename__ = "buildings"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)

    meters = db.relationship("Meter", backref="buildings", lazy='dynamic')
    rooms = db.relationship("Room", backref="buildings", lazy='dynamic')

    def __repr__(self):
        return '<Building: {}>'.format(self.id)


class Room(db.Model):
    __tablename__ = "rooms"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)

    building_id = db.Column(db.Integer, db.ForeignKey('buildings.id'))

    level = db.Column(db.String(16))
    number = db.Column(db.String(16))
    capacity = db.Column(db.Integer)
    coord_left = db.Column(db.Integer)
    coord_top = db.Column(db.Integer)
    floor_level = db.Column(db.Integer)

    room_bookings = db.relationship("RoomBooking", backref="rooms", lazy='dynamic')
    

    def __repr__(self):
        return '<Room: {}>'.format(self.id)

    def to_dict(self):
        return {
            'name': self.name,
            'coord_left': self.coord_left,
            'coord_top': self.coord_top
        }


class Class(db.Model):
    # a timeslot has a class
    # a timetable has many timeslots
    __tablename__ = "classes"

    id = db.Column(db.Integer, primary_key=True)
    mod_code = db.Column(db.String(64))
    mod_name = db.Column(db.String(100))
    number_taking = db.Column(db.Integer)

    events = db.relationship("Event", backref="classes", lazy='dynamic')

    def __repr__(self):
        return '<Class: {}>'.format(self.id)


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)

    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))

    room_bookings = db.relationship("RoomBooking", backref="events", lazy='dynamic')

    def __repr__(self):
        return '<Event: {}>'.format(self.id)


class RoomBooking(db.Model):
    #bookingID #roomID #eventID #duration #date #time #plannedSize
    __tablename__ = 'roombookings'

    id = db.Column(db.Integer, primary_key=True)

    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))
    
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))

    duration = db.Column(db.Integer)
    datetime = db.Column(db.DateTime)

    planned_size = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<RoomBooking: {}>'.format(self.id)

class Timeslot(db.Model):
    __tablename__ = 'timeslot'

    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(64))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    module_code = db.Column(db.String(100))

    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    class_ = db.relationship('Class')
    timetable_id = db.Column(db.Integer, db.ForeignKey('timetables.id'))
    timetable = db.relationship('Timetable')

    def __repr__(self):
        return '<Timeslot: {}>'.format(self.id)


class Timetable(db.Model):
    __tablename__ = 'timetables'

    id = db.Column(db.Integer, primary_key=True)
    timeslots = db.relationship("Timeslot", backref="timetables", lazy='dynamic')

    def __repr__(self):
        return '<Timetable: {}>'.format(self.id)

    def to_dict(self):
        return {
            'timeslots': [{
                'day': timeslot.day,
                'start_time': timeslot.start_time,
                'end_time': timeslot.end_time,
                'module_code': timeslot.module_code,
                'module_name': timeslot.class_.mod_name,
                'number_taking': timeslot.class_.number_taking
            } for timeslot in self.timeslots]
        }


class Login(db.Model):
    __tablename__ = "logins"

    id = db.Column(db.Integer, primary_key=True)
    login_time = db.Column(db.DateTime)
    logoff_time = db.Column(db.DateTime)
    domain = db.Column(db.String(64))
    computer = db.Column(db.String(64))

    def __repr__(self):
        return '<Login: {}>'.format(self.id)


class Booking(db.Model):
	__tablename__ = "bookings"

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	room_id = db.Column(db.Integer)
	room_name = db.Column(db.String(100))
	event_id = db.Column(db.Integer)
	duration = db.Column(db.Integer)
	occupancy = db.Column(db.Integer)
	datetime = db.Column(db.DateTime)

	checked_in = db.Column(db.Boolean, default=False)

	is_quiet = db.Column(db.Boolean, default=False)
	has_pc = db.Column(db.Boolean, default=False)
	has_hdmi = db.Column(db.Boolean, default=False)
	has_window =db.Column(db.Boolean, default=False)

	slot_group_ref = db.Column(db.String(100))

	slots_id = db.Column(db.Integer, db.ForeignKey('bookslots.id'))
	
	def __repr__(self):
		return '<Booking: {}>'.format(self.id)

	def __str__(self):
		return ("Booking id = {}\n".format(self.id) +
			    "        user_id = {}\n".format(self.user_id) +
			    "        room_id = {}\n".format(self.room_id) +
			    "        event_id = {}\n".format(self.event_id) +
			    "        duration = {}\n".format(self.duration) +
			    "        occupancy = {}\n".format(self.occupancy) +
			    "        datetime = {}\n".format(self.datetime) +
			    "        slot_group_ref = {}\n".format(self.slot_group_ref))


class BookingSlots(db.Model):
	__tablename__ = "bookslots"

	id = db.Column(db.Integer, primary_key=True)
	hour = db.Column(db.Integer)
	room_id = db.Column(db.Integer, db.ForeignKey('bookingrooms.id'))
	bookings = db.relationship('Booking', backref='bookingslots_parent', lazy=True)

	def __repr(self):
		return '<BookingSlots: {}'.format(self.id)


class BookingRoom(db.Model):
	__tablename__ = "bookingrooms"

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), unique=True)
	slots = db.relationship('BookingSlots', backref='room_parent', lazy=True)
	max_occupancy = db.Column(db.Integer)
	is_quiet = db.Column(db.Boolean, default=False)
	has_pc = db.Column(db.Boolean, default=False)
	has_hdmi = db.Column(db.Boolean, default=False)
	has_window = db.Column(db.Boolean, default=False)

	def __repr(self):
		return '<BookingRoom: {}'.format(self.id)


class Workspace(db.Model):
	__tablename__ = "workspaces"

	id = db.Column(db.Integer, primary_key=True)
	space = db.Column(db.String(100), unique=True)
	user_id = db.Column(db.Integer);
	checked_in = db.Column(db.Boolean, default=False)

	def __repr(self):
		return '<Workspace: {} : {}'.format(self.id, self.space)


class CSBEvent(db.Model):
    __tablename__ = "csb_events"

    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(400))
    duration = db.Column(db.Integer)
    date_time = db.Column(db.DateTime)
    planned_size = db.Column(db.Integer)

    def __repr__(self):
        return '<CSBEvent: {}>'.format(self.id)
