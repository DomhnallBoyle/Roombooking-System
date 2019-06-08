# app/admin/forms.py
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields.html5 import DateField, TimeField
from ..models import  Role


time_options = [('0',"00:00"), ('1',"01:00"), ('2',"02:00"), ('3',"03:00"), ('4',"04:00"),
                ('5',"05:00"), ('6',"06:00"), ('7',"07:00"), ('8',"08:00"), ('9',"09:00"), 
                ('10',"10:00"), ('11',"11:00"), ('12',"12:00"), ('13',"13:00"), 
                ('14',"14:00"), ('15',"15:00"), ('16',"16:00"), ('17',"17:00"),
                ('18',"18:00"), ('19',"19:00"), ('20',"20:00"), ('21',"21:00"), 
                ('22',"22:00"), ('23',"23:00")]

class UserProfileForm(FlaskForm):
    """
    Form for admin to assign departments and roles to employees
    """
    number_of_people = SelectField(label='Group room occupants:',
                                   choices=[(str(i), i) for i in range(1, 11)],
                                   default='2')
    is_quiet = BooleanField(label="Quiet work area desired",
                            default=False)
    has_computer = BooleanField(label="Computer required",
                                default=False)
    has_hdmi = BooleanField(label="Display screen & hdmi required",
                            default=False)
    has_window = BooleanField(label="Window desired",
                              default=False)
    wants_event_notifications = BooleanField(label="Would you like to receive event notifications?", default=False)
    submit = SubmitField('Save preferences')


class RoomBookingForm(FlaskForm):
    """
    Form for booking a room, preloads user preferences
    """
    date = DateField(label="Date of desired booking:",
                     default=datetime.today())
    time = SelectField(label="Booking start time:",
                       choices=time_options)
    duration = SelectField(label="Duration in hours:",
                           choices=[(str(i), i) for i in range(1,4)],
                           default='1')
    occupancy = SelectField(label='Number of occupants:',
                            choices=[(str(i), i) for i in range(1, 11)],
                            default='2')
    has_computer = BooleanField(label="Computer required",
                                default=False)
    has_hdmi = BooleanField(label="Display screen & hdmi required",
                            default=False)
    has_window = BooleanField(label="Window desired",
                              default=False)
    is_quiet = BooleanField(label="Quiet work area desired",
                            default=False)
    submit = SubmitField('Submit Booking')


class BookingConfirmationForm(FlaskForm):
    """
    Form for confirming details before booking a room
    """
    submit = SubmitField("Complete Booking")

