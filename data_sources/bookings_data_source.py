import pandas as pd
import os, re

from datetime import datetime
from app.models import Room, Class, Event, RoomBooking
from data_sources import BaseDataSource


class BookingsDataSource(BaseDataSource):

    def __init__(self):
        super(BookingsDataSource, self).__init__()

    def import_data(self):

        path = os.path.join(self.raw_data_directory, 'RoomBookingDataFeed.txt')
        df = pd.read_csv(path, sep=",", skiprows=2, skipinitialspace=True, names=range(4))[:-1]

        # slice df 
        room_names = []
        for line in open(path):
            if line.startswith('Room -'):
               room_names.append(line.rstrip())

        groups = df[0].isin(room_names).cumsum()
        bookings = {g.iloc[0,0]: g.iloc[1:] for k,g in df.groupby(groups)}    

        # Add rooms
        room_objects = []
        counter = 1
        for r in room_names:
            r_split = r.split("-")[1].split("/")
            id = counter
            name = r.split("-")[1]
            building_id = 1
            level = r_split[1]
            number = r_split[2]
            capacity = -1
            room = Room(id=id, name=name, building_id=building_id, level=level, number=number, capacity=capacity)
            room_objects.append(room)

            counter = counter + 1

        # Add classes & Events
        class_objects = []
        event_objects = []

        class_id = 500
        event_id = 1
        for room in room_names:
            for booking in bookings[room].dropna().itertuples():
                if booking[1] == "Event name":
                    continue
                rex = re.compile("^[A-Z]{3}[0-9]{4}$")
                name = str(booking[1])
                mod_code = name.split("/")[0]
                
                related_class = -1
                if rex.match(mod_code):
                    class_obj = next((class_ for class_ in class_objects
                                      if class_.mod_code == mod_code), None)
                    if class_obj == None:
                        class_ = Class(id=class_id, mod_code=mod_code, mod_name=mod_code, number_taking=-1)

                        related_class = class_id
                        class_objects.append(class_)
                        class_id = class_id + 1
                    else:
                        related_class = class_obj.id
                
                event_obj = next((event for event in event_objects
                                      if event.name == name), None) 
                if event_obj == None:
                    event = Event(id=event_id, name=name, class_id=related_class)
                    event_objects.append(event)
                    event_id = event_id + 1

                
        booking_objects = []
        
        booking_id = 1
        for room in room_names:
            room_name = name = r.split("-")[1]
            room_id = next((room.id for room in room_objects
                                      if room.name == name), None)
            for booking in bookings[room].dropna().itertuples():
                if booking[1] == "Event name":
                    continue
                name = str(booking[1])
                event_id = next((event.id for event in event_objects
                                      if event.name == name), -1)
                duration = booking[2]
                timestr = booking[3]

                dateandtime = datetime.strptime(timestr, '%d.%m.%Y %H:%M:%S')
                planned_size = booking[4]
                user_id = 1000 # TODO

                room_booking = RoomBooking(id=booking_id, room_id=room_id, event_id=event_id, duration=duration, datetime=dateandtime, planned_size=planned_size, user_id=user_id)
                booking_objects.append(room_booking)
                booking_id = booking_id + 1


        self.objects = room_objects + class_objects + event_objects + booking_objects

        
