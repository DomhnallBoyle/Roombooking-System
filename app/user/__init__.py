from flask import Blueprint

admin = Blueprint('user', __name__)

from . import views
from . import forms
