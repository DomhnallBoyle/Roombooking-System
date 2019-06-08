import pandas as pd
import os

from app.models import Room, Building
from data_sources import BaseDataSource


class RoomDataSource(BaseDataSource):

    def __init__(self):
        super(RoomDataSource, self).__init__()

    def import_data(self):
        room_coords = pd.read_csv(os.path.join(self.raw_data_directory, 'room_coords.csv'))

        building = Building(id=0, name='CSB')
        for index, row in room_coords.iterrows():
            floor_level = row['floor_level']
            top = row['top']
            left = row['left']
            text = row['text']

            building.rooms.append(Room(name=text, floor_level=floor_level, coord_top=top, coord_left=left))

        self.objects.append(building)
