import os
import pandas as pd


class BaseDataSource(object):

    def __init__(self):
        self.objects = []
        self.current_directory = os.path.abspath(os.path.dirname(__file__))
        self.raw_data_directory = os.path.join(self.current_directory,'raw_data')
        self.import_data()

    def import_data(self):
        raise NotImplementedError('This method must be implemented.')
