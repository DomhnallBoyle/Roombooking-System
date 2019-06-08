import pandas as pd
import os
from datetime import datetime

from app.models import Login
from data_sources import BaseDataSource


class LoginDataSource(BaseDataSource):

    def __init__(self):
        super(LoginDataSource, self).__init__()

    def import_data(self):
        logins = pd.read_csv(os.path.join(self.raw_data_directory, 'lab_logins.csv'))

        login_objects = []
        counter = 1
        for index, row in logins.iterrows():
            id = counter
            domain = row['Domain']
            computer = row['Computer']
            login_time = row['Logon_time']
            logoff_time = row['Logoff_time']

            formated_login_datetime = datetime.strptime(login_time, '%d/%m/%Y %H:%M')
            formatted_logoff_datetime = datetime.strptime(logoff_time, '%d/%m/%Y %H:%M')

            login = Login(id=id, domain = domain, computer = computer, login_time = formated_login_datetime, logoff_time = formatted_logoff_datetime )
            login_objects.append(login)
            counter+=1

        self.objects = login_objects
