# app/admin/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, PasswordField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from ..models import Role, User, Room, Building


class RoleForm(FlaskForm):
    """
    Form for admin to add or edit a role
    """
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit')


class UserForm(FlaskForm):
    """
    Form for admin to add users
    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[
                                        DataRequired(),
                                        EqualTo('confirm_password')
                                        ])
    confirm_password = PasswordField('Confirm Password')
    submit = SubmitField('Submit')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email is already in use.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username is already in use.')


class UserAssignForm(FlaskForm):
    """
    Form for admin to assign departments and roles to employees
    """
    is_admin = RadioField('Is Admin', choices=[('YES', 'Yes'), ('NO', 'No')])
    # department = QuerySelectField(query_factory=lambda: Department.query.all(),
    #                               get_label="name")
    role = QuerySelectField(query_factory=lambda: Role.query.all(),
                            get_label="name")
    submit = SubmitField('Submit')


class RoomForm(FlaskForm):
    """
    Form to allow admin to add rooms to a particular building
    """
    name = StringField('Room Name', validators=[DataRequired()])
    level = IntegerField('Floor level', validators=[DataRequired()])
    capacity = IntegerField('Capacity', validators=[DataRequired()])
    submit = SubmitField('Submit')


class BuildingForm(FlaskForm):
    """
    Form to allow the admin to add a building to the system
    """
    name = StringField('Building Name', validators=[DataRequired()])
    submit = SubmitField('Submit')
