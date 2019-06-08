from ..models import Preferences, Login, Timeslot, Booking, BookingSlots, BookingRoom, Workspace, User
from flask_login import current_user

from apscheduler.schedulers.background import BackgroundScheduler

from .. import db

from datetime import datetime, timedelta
from utilities.email_utility import EmailUtility


def submit_booking_request(booking):
    
    

    rooms = BookingRoom.query.all()

    matching_rooms = []
    for room in rooms:
        if (room.max_occupancy >= booking['occupancy']
        and room.has_pc >= booking['has_computer']
        and room.is_quiet >= booking['is_quiet']):
            matching_rooms.append(room)

    perfect_matches = []
    matching_rooms.sort(key=lambda mr : mr.max_occupancy)
    for room in matching_rooms:
        if (room.max_occupancy >= booking['occupancy']
        and room.has_pc == booking['has_computer']
        and room.is_quiet == booking['is_quiet']):
            perfect_matches.append(room)

    if perfect_matches:
        success = find_room(perfect_matches, booking, attempt=1)
        if success:
            return success

    return find_room(matching_rooms, booking, attempt=2)


def find_room(matches, booking, attempt, exact=True,):

    today = datetime.now().day
    book_day = booking['datetime'].day
    slot_day = book_day - today

    slots_needed = booking['duration']

    if slot_day not in range(0,7):
        return False

    for room in matches:
        h = booking['datetime'].hour

        timeslots = room.slots[slot_day]
        
        available_slots = []

        slot = timeslots.bookings[h]

        if slot.user_id == None:
            available_slots.append(h)

            for t in range(1, slots_needed):
                next_h = h + t

                if next_h < 24:
                    next_slot = timeslots.bookings[next_h]
                    if next_slot.user_id == None:
                        available_slots.append(h+t)


        if len(available_slots) == slots_needed:
            booking['occupancy'] = room.max_occupancy
            booking['is_quiet'] = room.is_quiet
            booking['has_computer'] = room.has_pc
            booking['room_id'] = room.id
            booking['room_name'] = room.name
            return {'slots':available_slots, 'booking':booking, 'exact':exact}
        
    if attempt > 1 and attempt < 26:
        attempt += 1
        booking['datetime'] = booking['datetime'] + timedelta(hours=1)
        return find_room(matches, booking, attempt=attempt, exact=False)
            
    return None


def book_room(available_slots, booking):
    today = datetime.now().day
    book_day = booking['datetime'].day
    slot_day = book_day - today

    room = BookingRoom.query.filter_by(id=booking['room_id']).one()

    timeslots = room.slots[slot_day]
    for slot_time in available_slots:
        timeslots.bookings[slot_time].user_id=current_user.id
        timeslots.bookings[slot_time].room_id=room.id
        timeslots.bookings[slot_time].room_name=room.name
        timeslots.bookings[slot_time].duration=booking['duration']
        timeslots.bookings[slot_time].occupancy=room.max_occupancy
        timeslots.bookings[slot_time].datetime=booking['datetime']
        timeslots.bookings[slot_time].is_quiet=room.is_quiet
        timeslots.bookings[slot_time].has_pc=room.has_pc
        timeslots.bookings[slot_time].has_window=room.has_window
        timeslots.bookings[slot_time].has_hdmi=room.has_hdmi
        timeslots.bookings[slot_time].slot_group_ref=str(current_user.id)+'U'+str(booking['datetime'])+'T'

    db.session.add(room)
    db.session.commit()

    master_booking_id = timeslots.bookings[available_slots[0]].id
    ref = timeslots.bookings[available_slots[0]].slot_group_ref
    scheduler = BackgroundScheduler()
    
    # set late cancellation for 15 minutes after booking start time
    alarm_time = booking['datetime'] + timedelta(minutes=10)
    
    # DEMO set late cancellation for 15 seconds after booking creation time
    # alarm_time = datetime.now() + timedelta(seconds=15)

    scheduler.add_job(booking_check, 'date', run_date=alarm_time, args=[master_booking_id])
    scheduler.start()

    email_utility = EmailUtility()
    email_utility.send_email('Booking Confirmed',
                             'The following booking with reference {} has been confirmed.'.format(ref),
                             recipients=[current_user.email])


def booking_check(booking_id):
    booking = Booking.query.filter(Booking.id == booking_id).one()
    ref = booking.slot_group_ref
    email_utility = EmailUtility()
    if not booking.checked_in:
        recipient = User.query.get(booking.user_id)
        datetime = booking.datetime
        duration = booking.duration
        for b in Booking.query.filter(Booking.slot_group_ref == ref).all():
            b.user_id=None
            b.duration=None
            b.occupancy=None
            b.datetime=None
            b.is_quiet=None
            b.has_pc=None
            b.has_hdmi=None
            b.has_window=None
            b.slot_group_ref=None
            db.session.add(b)
            db.session.commit()

        # TODO - send notification that booking is lost
        email_utility.send_email('Booking Cancelled',
                                 'The following booking with reference {} has been cancelled because there has been no '
                                 'check-in confirmation.'.format(ref),
                                 recipients=[recipient.email])

        # TODO - notify people that a new space is available
        recipients = []
        for user in User.query.filter(User.id != recipient.id):
            preferences = user.preferences
            if preferences and preferences.wants_event_notifications:
                recipients.append(user.email)

        email_utility.send_email('Booking Space Update',
                                 'The following timeslot has become available in the system: {} for {} '
                                 'hour/s. You can unsubscribe from these emails from your settings.'.format(
                                     datetime, duration),
                                 recipients=recipients)


def workspace_check(user_id):
    workspace = Workspace.query.filter_by(user_id = user_id).all()
    if workspace:
        if not workspace[0].checked_in:
            db.session.delete(workspace[0])
            db.session.commit()
