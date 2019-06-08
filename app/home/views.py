import os
from flask import abort, flash, render_template, redirect, url_for, request, session, jsonify
from flask_login import current_user,login_required
from sqlalchemy import func
from sqlalchemy.sql import label


from . import home
from .booking import submit_booking_request, book_room, workspace_check
from ..user.forms import UserProfileForm, RoomBookingForm, BookingConfirmationForm
from .. import db
from ..models import Preferences, Login, Timeslot, Booking, Room, BookingRoom, Workspace, Timetable
from utilities.email_utility import EmailUtility

from .utils import OccupancyDisplay, Weather, Chart
import random #keep!
import json

from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import json


def setup_home():
    """
    Render the homepage template on the / route
    """

    silent_load = OccupancyDisplay(random.randint(0,100)/100)
    noisy_load = OccupancyDisplay(random.randint(0,100)/100)
    group_load = OccupancyDisplay(random.randint(0,100)/100)

    # TODO: Add caching in db (15-30 minutes)
    weather = Weather()

    current_datetime = datetime.now()
    day = current_datetime.strftime('%A')

    chart = None
    if day not in ['Saturday', 'Sunday']:
        time_intervals = [
            [8, 9],
            [9, 10],
            [10, 11],
            [11, 12],
            [12, 13],
            [13, 14],
            [14, 15],
            [15, 16],
            [16, 17],
            [17, 18]
        ]

        ti = [
            [9, 12],
            [10, 13],
            [11, 14],
            [12, 15],
            [13, 16],
            [14, 17]
        ]

        time_interval_occupancies = [0 for i in range(0, 10)]

        timeslot_list = []
        for i in ti:
            start_time = datetime(day=1, month=1, year=2017, hour=i[0])
            end_time = datetime(day=1, month=1, year=2017, hour=i[1])

            timeslots = Timeslot.query.filter(Timeslot.start_time >= start_time).filter(
                Timeslot.end_time <= end_time).filter_by(day=day).all()

            for timeslot in timeslots:
                for k in range(0, len(time_intervals)):
                    for j in range(0, len(time_intervals)):
                        if timeslot.start_time.hour == time_intervals[k][0] and timeslot.end_time.hour == \
                                time_intervals[j][1]:
                            if timeslot.id not in timeslot_list:
                                for l in range(k, j+1):
                                    class_ = timeslot.class_
                                    # print('Module code: {}, number: {} into {}'
                                    #       .format(class_.mod_code, class_.number_taking, time_intervals[l]))
                                    time_interval_occupancies[l] += class_.number_taking
                                timeslot_list.append(timeslot.id)

        # print(time_interval_occupancies)
        chart = Chart(day, 8, 18, time_interval_occupancies)

    return silent_load, noisy_load,group_load,chart,weather



@home.route('/')
def homepage():

    silent_load, noisy_load,group_load,chart,weather = setup_home()

    if current_user.is_authenticated:
        if not current_user.is_admin and current_user.year_group:
            timetable = Timetable.query.get(current_user.year_group)
        else:
            timetable = None
    else:
        timetable = None

    return render_template('home/index.html', title="Welcome",
                           silent_load=silent_load, noisy_load=noisy_load,
                           group_load=group_load, chart=chart, weather=weather, timetable=timetable)


@home.route('/dashboard')
@login_required
def dashboard():
    """
    Render the dashboard template on the /dashboard route
    """
    return render_template('home/dashboard.html', title="Dashboard")


def get_logins():
    login_objects = db.session.query(label('computer', Login.computer), func.count(Login.computer)).group_by(
        Login.computer).all()
    login_objects.sort(key=lambda x: x[1], reverse=True)

    highest_used = []
    if login_objects:
        for i in range(0, 11):
            highest_used.append(login_objects[i])

    return highest_used


@home.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)

    return render_template('home/admin_dashboard.html', title="Dashboard", logins = get_logins())


@home.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UserProfileForm(csrf_enabled=False)
    if current_user and current_user.preferences and request.method == 'GET':
        form.number_of_people.default = str(current_user.preferences.number_of_people)
        form.has_computer.default = current_user.preferences.has_pc
        form.is_quiet.default = current_user.preferences.is_quiet
        form.has_hdmi.default = current_user.preferences.has_hdmi
        form.has_window.default = current_user.preferences.has_window
        form.wants_event_notifications.default = current_user.preferences.wants_event_notifications
        form.process()

    if form.validate_on_submit():
        number_of_people = form.data['number_of_people']
        is_quiet = form.data['is_quiet']
        has_computer = form.data['has_computer']
        has_window = form.data['has_window']
        has_hdmi = form.data['has_hdmi']
        wants_event_notifications = form.data['wants_event_notifications']

        if current_user.preferences:
            current_user.preferences.number_of_people = int(number_of_people)
            current_user.preferences.is_quiet = is_quiet
            current_user.preferences.has_pc = has_computer
            current_user.preferences.has_window = has_window
            current_user.preferences.has_hdmi = has_hdmi
            current_user.preferences.wants_event_notifications = wants_event_notifications
        else:
            current_user.preferences = Preferences(number_of_people=int(number_of_people),
                                                   has_pc=has_computer,
                                                   is_quiet=is_quiet,
                                                   has_hdmi=has_hdmi,
                                                   has_window=has_window,
                                                   wants_event_notifications=wants_event_notifications)

        db.session.add(current_user)
        db.session.commit()

        flash('You have successfully edited the user preferences')

        return redirect(url_for('home.profile'))

    return render_template('home/profile.html', title='Profile', form=form)


@home.route('/createbook', methods=['GET', 'POST'])
@login_required
def room_booking():
    form = RoomBookingForm(csrf_enabled=False)
    if current_user and current_user.preferences and request.method == 'GET':
        form.occupancy.default = str(current_user.preferences.number_of_people)
        form.has_computer.default = current_user.preferences.has_pc
        form.is_quiet.default = current_user.preferences.is_quiet
        form.has_window.default = current_user.preferences.has_window
        form.has_hdmi.default = current_user.preferences.has_hdmi
        current_hour = datetime.now().hour
        next_hour = 0 if current_hour+1 > 23 else current_hour+1
        form.time.default = str(next_hour)
        form.process()


    if form.validate_on_submit():
        b = {}
        date = form.data['date']
        time = int(form.data['time'])
        b['duration'] = int(form.data['duration'])
        b['occupancy'] = int(form.data['occupancy'])
        b['has_computer'] = form.data['has_computer']
        b['has_hdmi'] = form.data['has_hdmi']
        b['has_window'] = form.data['has_window']
        b['is_quiet'] = form.data['is_quiet']

        b['datetime'] = datetime(day=date.day, month=date.month, year=date.year, hour=time)

        response = submit_booking_request(b)

        if response:
            session['booking'] = response
            return redirect(url_for('home.confirm_booking'))

        else:
            flash('No Booking Timeslot available.')
            return redirect(url_for('home.room_booking'))     

    return render_template('home/room_booking.html', title='Room Booking', form=form)


@home.route('/confirmbook', methods=['GET', 'POST'])
@login_required
def confirm_booking():
    form = BookingConfirmationForm(csrf_enabled=False)

    details = session['booking']

    if not details['exact'] and request.method == 'GET':
        flash('Requested time unavailable, next available time suggested.')

    if form.validate_on_submit():
        book_room(details['slots'], details['booking'])
        return redirect(url_for('home.user_bookings')) 


    return render_template('home/confirm_booking.html', title='Confirm Booking', form=form, details=details)

@home.route('/viewbooks', methods=['GET', 'POST'])
@login_required
def user_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    bookings.sort(key=lambda b : b.datetime)

    unique_bookings = {}
    for b in bookings:
        if b.slot_group_ref not in unique_bookings:
            unique_bookings[b.slot_group_ref] = b

    output = []
    for ref in unique_bookings:
        output.append(unique_bookings[ref])

    workspaces = Workspace.query.filter_by(user_id=current_user.id).all()

    return render_template('home/bookings_list.html', title='Current Bookings', bookings=output, workspaces=workspaces)


@home.route('/allbook', methods=['GET', 'POST'])
@login_required
def all_bookings():
    bookings = Booking.query.filter(Booking.user_id != None).all()
    if bookings:
        bookings.sort(key=lambda b : b.datetime)

    unique_bookings = {}
    for b in bookings:
        if b.slot_group_ref not in unique_bookings:
            unique_bookings[b.slot_group_ref] = b

    output = []
    for ref in unique_bookings:
        output.append(unique_bookings[ref])

    workspaces = Workspace.query.filter_by(user_id=current_user.id).all()

    return render_template('home/bookings_list.html', title='All Bookings', bookings=output, workspaces=workspaces)


@home.route('/floor_plan', methods=['GET', 'POST'])
@login_required
def floor_plan():
    data = json.loads(request.data)
    floor = data.get('floor-number')

    path = 'floor' + floor + '.png'

    if floor == 'G':
        floor = 0

    rooms = Room.query.filter_by(floor_level=floor).all()

    if rooms:
        return jsonify(rooms=[room.to_dict() for room in rooms], image_path=path)

    flash('No rooms available.', 'error')

    return abort(404)



@home.route('/view_booking/<ref>/<booking_id>', methods=['GET', 'POST'])
@login_required
def view_booking(ref, booking_id):
    b = Booking.query.filter(Booking.id == booking_id).one()
    r = BookingRoom.query.filter(BookingRoom.id == b.room_id).one()

    return render_template('home/view_booking.html',booking=b,room=r)


@home.route('/delete_booking/<ref>/<booking_id>', methods=['GET', 'POST'])
@login_required
def delete_booking(ref, booking_id):
    for b in Booking.query.filter(Booking.slot_group_ref == ref).all():
        b.user_id=None
        b.duration=None
        b.occupancy=None
        b.datetime=None
        b.is_quiet=None
        b.has_pc=None
        b.slot_group_ref=None
        b.checked_in=False
        db.session.add(b)
        db.session.commit()

    return redirect(url_for('home.user_bookings'))      

@home.route('/checkin_booking/<ref>/<booking_id>', methods=['GET', 'POST'])
@login_required
def checkin_booking(ref, booking_id):
    for b in Booking.query.filter(Booking.slot_group_ref == ref).all():
        b.checked_in = True
        db.session.add(b)
        db.session.commit()

    return redirect(url_for('home.view_booking', ref=ref, booking_id=booking_id))


@home.route('/workspace_allocation', methods=['GET', 'POST'])
@login_required
def workspace_allocation():
    w = Workspace.query.filter_by(user_id = current_user.id).all()

    if w:
        for space in w:
            db.session.delete(space)
            db.session.commit()

    spaces = ['First Derivatives Room',
              'Floor 0 Lab',
              'Floor 1 Lab']

    allocated = random.choice(spaces)

    w = Workspace(space=allocated, user_id=current_user.id)
    db.session.add(w)
    db.session.commit()

    scheduler = BackgroundScheduler()
    alarm_time = datetime.now() + timedelta(seconds=15)
    scheduler.add_job(workspace_check, 'date', run_date=alarm_time, args=[current_user.id])
    scheduler.start()

    return render_template('home/workspace_allocation.html', workspace=w)


@home.route('/checkin_workspace/<wid>', methods=['GET', 'POST'])
@login_required
def checkin_workspace(wid):
    workspace = Workspace.query.filter_by(id=wid).one()
    workspace.checked_in = True
    db.session.add(workspace)
    db.session.commit()

    return redirect(url_for('home.user_bookings'))


@home.route('/booking/<ref>/notify', methods=['GET', 'POST'])
@login_required
def booking_notifications(ref):
    data = json.loads(request.data)
    email_addresses = data.get('emails').strip()

    email_addresses = [email_address.strip() for email_address in email_addresses.split(',')]
    booking = Booking.query.filter(Booking.slot_group_ref == ref).first()

    if booking:
        room = Room.query.get(booking.room_id)
        message = 'This is a notification email for the booking of {} at ' \
                  '{} for {} hour/s in room {}.'.format(ref, booking.datetime, booking.duration, room.name)
        email_utility = EmailUtility()
        email_utility.send_email('Booking Notification', message, email_addresses)

        return jsonify(message='Notification email sent successfully.')
    else:
        abort(404)
