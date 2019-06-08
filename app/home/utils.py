# app/home/utils.py

from datetime import date, time, datetime
import math
import requests


class OccupancyDisplay:
    def __init__(self,load):
        """
        Codes load (0-1) to green-to-red hsla scale 
        """
        if load < 0:
            load = 0
        if load > 1:
            load = 1 

        self.load = int(load * 100)
        self.h = round( 138 * (1 - load) )
        self.s = round( 82 - 10 * load )
        self.l = round( 46 - 3 * load )
        self.a = 0.75


class Weather:
    def __init__(self):
        """
        Fetches current weather around CSB
        """
        API_KEY = "f44c8e86895f7c7aa3a0fa342ac7e6be"
        options = "units=uk2&exclude=minutely,daily,alerts"
        latitude = str(54.581767)
        longitude = str(-5.937355)

        date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        response = requests.get("https://api.darksky.net/forecast/"+API_KEY +
                                "/"+latitude+","+longitude+","+date+"?"+options)
        json_res = response.json()

        self.summary = json_res['hourly']['summary']
        self.icon = json_res['currently']['icon']
        self.temp = round( json_res['currently']['apparentTemperature'] , 1)

        precip_type = None
        self.rain = None
        if'precipProbability' in json_res['currently'] and 'precipType' in json_res['currently']:
            precip_type = json_res['currently']['precipType']
            self.rain = json_res['currently']['precipProbability']
        if (self.rain != None and precip_type == 'rain'):
            self.rain = round(100*self.rain)
        else:
            self.rain = 0


class Chart:

    def __init__(self, day, min_time, max_time, data):
        """
        Plots avg occupancy from min_time to max_time
        data is always accessed from 0 to (max-min-1)!
        """

        self.legend = 'Average Occupation'
        # self.day = calendar.day_name[date.today().weekday()]
        self.day = day

        self.x = [time(hour=h, minute=0, second=0)
                  for h in range(min_time, max_time+1)]
        self.y = data

        self.max_y = self.roundup(max(data))

        curr_hour = datetime.now().hour                 
        if curr_hour in range(min_time, max_time+1):
            try:
                self.dot = data[curr_hour-min_time]
            except IndexError:
                self.dot = -1
        else:
            self.dot = -1 

    def roundup(self, x):
        return int(math.ceil(x / 100.0)) * 100
