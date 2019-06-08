import pandas as pd
import os

from app.models import CSBEvent
from data_sources import BaseDataSource
from datetime import datetime


class EventDataSource(BaseDataSource):

    def __init__(self):
        super(EventDataSource, self).__init__()

    def import_data(self):

        events = pd.read_csv(os.path.join(self.raw_data_directory, 'events.csv'))

        event_objects = []
        counter = 1
        for index, row in events.iterrows():
            id = counter
            event_name = row['event_name']
            duration = row['duration']
            date_time = row['date/time']

            planned_size = row['planned_size']
            planned_size_as_int = int(planned_size)
            duration_as_int = int(duration)
            formated_datetime = datetime.strptime(date_time, '%d.%m.%Y %H:%M:%S')
            module = CSBEvent(id=id, event_name=event_name,duration=duration_as_int,date_time=formated_datetime,planned_size=planned_size_as_int)

            event_objects.append(module)
            counter+=1

        self.objects = event_objects
