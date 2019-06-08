import pandas as pd
import os

from app.models import Class
from data_sources import BaseDataSource


class ClassesDataSource(BaseDataSource):

    def __init__(self):
        super(ClassesDataSource, self).__init__()

    def import_data(self):

        classes = pd.read_csv(os.path.join(self.raw_data_directory, 'classes.csv'))

        class_objects = []
        for index, row in classes.iterrows():
            id = row['id']
            mod_code = row['mod_code']
            name = row['name']
            number_taking = (row['number_taking'])
            num_taking = int(number_taking)
            module = Class(id=id, mod_code=mod_code,mod_name=name,number_taking=num_taking)

            class_objects.append(module)

        self.objects = class_objects
