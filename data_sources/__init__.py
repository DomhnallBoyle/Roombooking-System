from app import app
from .base_data_source import *
from .efficiency_data_source import *
from .classes_data_source import *
from .logins_data_source import *
from .timetable_data_source import *
from .bookings_data_source import *
from .rooms_data_source import *
from .event_data_source import *


def get_data_sources():
    if app.config.get('TESTING'):
        return []
    else:
        rooms_data_source = RoomDataSource()
        efficiency_ds = EfficiencyDataSource()
        login_ds = LoginDataSource()
        timetable_ds = TimetableDataSource()
        bookings_ds = BookingsDataSource()
        event_ds = EventDataSource()
        
        return login_ds.objects + timetable_ds.objects + bookings_ds.objects + rooms_data_source.objects + \
               event_ds.objects + efficiency_ds.objects
