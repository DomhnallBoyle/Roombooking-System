import os
import pandas as pd
from datetime import datetime

from app.models import Timeslot, Timetable, Class
from . import BaseDataSource


class TimetableDataSource(BaseDataSource):

    def __init__(self):
        super(TimetableDataSource, self).__init__()

    def import_data(self):
        timetable_list = []
        classes = pd.read_csv(os.path.join(self.raw_data_directory, 'classes.csv'))
        for i in range(1, 5):
            timetable = pd.read_csv(os.path.join(self.raw_data_directory, 'timetable{}.csv'.format(i)))
            timeslots = []
            mod_code_list = []
            for index, row in timetable.iterrows():
                day = row['day']
                start_time = row['start_time'].split(':')
                end_time = row['end_time'].split(':')
                module_code = row['module_code']

                class_ = classes.loc[classes['mod_code']==module_code]


                class_row = class_.iloc[0]
                #print(class_row)
                name = class_row['name']

                number_taking = int(class_row['number_taking'])
                class_id = int(class_row['id'])

                class_object = Class(mod_name=name, mod_code = module_code, number_taking = number_taking)



                start_time_hour = int(start_time[0])

                end_time_hour = int(end_time[0])


                st_time = datetime(year = 2017, day =1 , month =1,hour=start_time_hour)
                end_time = datetime(year = 2017, day =1 , month =1,hour=end_time_hour)

                timeslot = Timeslot(day=day, start_time=st_time, end_time = end_time, module_code = module_code, class_ = class_object )
                timeslots.append(timeslot)

            #timetable = Timetable(id=id, timeslots = timeslots)
            timetable = Timetable(timeslots = timeslots)
            timetable_list.append(timetable)


        self.objects = timetable_list