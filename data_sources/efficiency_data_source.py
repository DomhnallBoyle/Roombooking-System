import pandas as pd
import os
from datetime import date

from app.models import MeterReading, Meter, Building
from data_sources import BaseDataSource


class EfficiencyDataSource(BaseDataSource):

    def __init__(self):
        super(EfficiencyDataSource, self).__init__()

    def import_data(self):
        buildings = pd.read_csv(os.path.join(self.raw_data_directory, 'FacilityBuildings.csv'))
        meters = pd.read_csv(os.path.join(self.raw_data_directory, 'FacilityMeters.csv'))
        meter_readings = pd.read_csv(os.path.join(self.raw_data_directory, 'FacilityMeterReadings.csv'))

        meter_reading_objects = []
        for index, row in meter_readings.iterrows():
            meter_id = row['fkFacilityMeterId']
            meter_reading_date = row['MeterReadingDate'].split('-')
            meter_usage_kwh = row['MeterUsageKwH']
            block_co2 = row['BlockCO2']
            block_cost = row['BlockCost']

            year = int(meter_reading_date[0])
            month = int(meter_reading_date[1])
            day = int(meter_reading_date[2])
            mr_date = date(year=year, month=month, day=day)
            meter_reading = MeterReading(meter_reading_date=mr_date,
                                         meter_usage_kwh=meter_usage_kwh,
                                         block_co2=block_co2,
                                         block_cost=block_cost,
                                         meter_id=meter_id)

            meter_reading_objects.append(meter_reading)

        meter_objects = []
        meter_counter = 1
        for index, row in meters.iterrows():
            name = row['FacilityMeterName']
            building_id = row['fkFacilityBuildingId']

            meter = Meter(id=meter_counter, name=name, building_id=building_id)

            for meter_reading_object in meter_reading_objects:
                if meter_reading_object.meter_id == meter.id:
                    meter.meter_readings.append(meter_reading_object)

            meter_objects.append(meter)
            meter_counter += 1

        building_objects = []
        building_counter = 1
        for index, row in buildings.iterrows():
            name = row['FacilityBuildingName']

            building = Building(id=building_counter, name=name)

            for meter in meter_objects:
                if meter.building_id == building.id:
                    building.meters.append(meter)

            building_objects.append(building)
            building_counter += 1

        self.objects = building_objects
