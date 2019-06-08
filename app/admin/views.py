import json

from flask import abort, flash, redirect, render_template, url_for, request, jsonify
from flask_login import current_user, login_required
from datetime import datetime

from . import admin
from .. import db
from ..models import User, Role, MeterReading, Timetable, Preferences, Room, Building, Booking
from .forms import UserAssignForm, RoleForm, UserForm, RoomForm, BuildingForm
from app.home.views import get_logins

from datetime import timedelta, datetime, date


def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.is_admin:
        abort(403)


@admin.route('/roles')
@login_required
def list_roles():
    check_admin()
    """
    List all roles
    """
    roles = Role.query.all()
    return render_template('admin/roles/roles.html',
                           roles=roles, title='Roles')

@admin.route('/buildings')
@login_required
def list_buildings():
    check_admin()
    """
    List all buildings
    """
    buildings = Building.query.all()
    return render_template('admin/buildings/buildings.html',
                           buildings=buildings, title='Buildings')


@admin.route('/rooms/<int:building_id>')
@login_required
def list_rooms(building_id):
    """
    Return a list of all rooms within the system
    :return:
    """
    check_admin()

    rooms = Room.query.filter_by(building_id=building_id).all()

    return render_template('admin/rooms/rooms.html', rooms=rooms, title='Rooms', building_id=building_id)


@admin.route('/buildings/add/', methods=['GET', 'POST'])
@login_required
def add_building():
    check_admin()

    form = BuildingForm()
    if form.validate_on_submit():
        building = Building(name=form.name.data)

        try:
            # add building to the database
            db.session.add(building)
            db.session.commit()

            flash('You have successfully added a new building.')
        except:
            # in case role name already exists
            flash('Error: building name already exists.')

        # redirect to the roles page
        return redirect(url_for('admin.list_buildings'))


    return render_template('admin/buildings/add_building.html', form=form, title='Add Building')


@admin.route('/rooms/add/<int:building_id>', methods=['GET', 'POST'])
@login_required
def add_room(building_id):
    check_admin()

    form = RoomForm()
    if form.validate_on_submit():
        room = Room(name=form.name.data, floor_level=form.level.data, capacity=form.capacity.data, building_id=building_id)

        try:
            # add room to the database
            db.session.add(room)
            db.session.commit()

            flash('You have successfully added a new room.')
        except:
            # in case role name already exists
            flash('Error: room name already exists.')

        # redirect to the roles page
        return redirect(url_for('admin.list_rooms', building_id=building_id))

    return render_template('admin/rooms/add_room.html', form=form, title='Add Room')


@admin.route('/bookings', methods=['GET', 'POST'])
@login_required
def list_bookings():
    check_admin()

    # year = datetime.today().strftime('%Y')
    # month = datetime.today().strftime('%m')
    # day = datetime.today().strftime('%d')
    #
    # print(year)
    # print(month)
    # print(day)

    # from sqlalchemy import extract
    # # bookings = Booking.query.filter(extract('year', Booking.datetime) == year).filter(extract('month', Booking.datetime) == month).filter(extract('day', Booking.datetime) == day)
    # bookings = Booking.query.filter(extract('year', Booking.datetime) == year)
    # print(bookings)

    # current_date = date(year=datetime.today().year, month=datetime.today().month, day=datetime.today().day)
    # bookings = Booking.query.filter(Booking.datetime >= current_date).all()
    # print(bookings)

    current_date = datetime.today()
    year = current_date.year
    month = current_date.month
    day = current_date.day
    date_string = '{}/{}/{}'.format(day, month, year)

    current_date_start = datetime(year=year, month=month, day=day)
    current_date_end = datetime(year=year, month=month, day=day, hour=23, minute=59)

    from sqlalchemy import and_
    bookings = Booking.query.filter(and_(Booking.datetime >= current_date_start, Booking.datetime <= current_date_end)).all()

    return render_template('admin/bookings/bookings.html', title="Today's Bookings", bookings=bookings, date=date_string)


@admin.route('/roles/add', methods=['GET', 'POST'])
@login_required
def add_role():
    """
    Add a role to the database
    """
    check_admin()

    add_role = True

    form = RoleForm()
    if form.validate_on_submit():
        role = Role(name=form.name.data,
                    description=form.description.data)

        try:
            # add role to the database
            db.session.add(role)
            db.session.commit()
            flash('You have successfully added a new role.')
        except:
            # in case role name already exists
            flash('Error: role name already exists.')

        # redirect to the roles page
        return redirect(url_for('admin.list_roles'))

    # load role template
    return render_template('admin/roles/role.html', add_role=add_role,
                           form=form, title='Add Role')


@admin.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    """
    Add a user to the database
    """
    check_admin()

    form = UserForm()

    if form.validate_on_submit():
        user = User(email=form.data['email'],
                    password=form.data['password'],
                    username=form.data['username'],
                    first_name=form.data['first_name'],
                    last_name=form.data['last_name'])

        user.preferences = Preferences(number_of_people=2,
                                       has_pc=False,
                                       is_quiet=False)

        db.session.add(user)
        db.session.commit()
        flash('You have successfully added a new user')

        return redirect(url_for('admin.list_users'))

    return render_template('admin/users/add_user.html', form=form, title='Add User')


@admin.route('/roles/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_role(id):
    """
    Edit a role
    """
    check_admin()

    add_role = False

    role = Role.query.get_or_404(id)
    form = RoleForm(obj=role)
    if form.validate_on_submit():
        role.name = form.name.data
        role.description = form.description.data
        db.session.add(role)
        db.session.commit()
        flash('You have successfully edited the role.')

        # redirect to the roles page
        return redirect(url_for('admin.list_roles'))

    form.description.data = role.description
    form.name.data = role.name
    return render_template('admin/roles/role.html', add_role=add_role,
                           form=form, title="Edit Role")


@admin.route('/roles/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_role(id):
    """
    Delete a role from the database
    """
    check_admin()

    role = Role.query.get_or_404(id)
    db.session.delete(role)
    db.session.commit()
    flash('You have successfully deleted the role.')

    # redirect to the roles page
    return redirect(url_for('admin.list_roles'))


@admin.route('/users')
@login_required
def list_users():
    """
    List all users
    """
    check_admin()

    users = User.query.all()
    return render_template('admin/users/users.html',
                           users=users, title='Users')


@admin.route('/users/assign/<int:id>', methods=['GET', 'POST'])
@login_required
def assign_user(id):
    """
    Assign a department and a role to an user
    """
    check_admin()

    user = User.query.get_or_404(id)

    # # prevent admin from being assigned a department or role
    # if user.is_admin:
    #     abort(403)

    form = UserAssignForm(obj=user)

    if form.validate_on_submit():
        user.role = form.data['role']
        user.is_admin = True if form.data['is_admin'] == 'YES' else False

        db.session.add(user)
        db.session.commit()
        flash('You have successfully assigned admin privileges and role.')

        # redirect to the roles page
        return redirect(url_for('admin.list_users'))
    else:
        form.is_admin.default = 'YES' if user.is_admin else 'NO'
        form.process()

    return render_template('admin/users/user.html',
                           user=user, form=form,
                           title='Assign User')


@admin.route('/users/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_user(id):
    """
    Admin: Remove a user
    """
    check_admin()

    user = User.query.get(id)
    if user:
        username = user.username

        db.session.delete(user)
        db.session.commit()

        flash('You have successfully removed user {} from the system.'.format(username))
    else:
        flash('User does not exist.', 'error')

    return redirect(url_for('admin.list_users'))


@admin.route('/efficiency', methods=['POST'])
@login_required
def get_efficiency():
    data = json.loads(request.data)
    meter = data.get('meter')
    date = data.get('date').split('-')

    start = datetime(year=int(date[0]),
                     month=int(date[1]),
                     day=int(date[2]))

    meter_reading = MeterReading.query.filter_by(
        meter_reading_date=start,
        meter_id=int(meter)
    ).first()

    if meter_reading:
        return jsonify(meter_reading=meter_reading.to_dict())

    flash('No meter readings for that meter or date.', 'error')

    return abort(404)


@admin.route('/timetable', methods=['GET', 'POST'])
@login_required
def get_timetable():
    data = json.loads(request.data)
    year_group = data.get('year')

    timetable = Timetable.query.get(year_group)

    if timetable:
        return jsonify(timetable=timetable.to_dict())

    flash('No timetables available.', 'error')

    return abort(404)
