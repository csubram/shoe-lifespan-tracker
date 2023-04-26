from datetime import datetime
import os
from authorization.access_token_handler import AccessTokenHandler
from activity_fetcher import ActivityFetcher
from authorization.json_utils import *
from datetime_helper import DatetimeHelper

SHOE_DESCRIPTORS = 'shoes'
MILES_PER_KM = 0.62137119

class Location():
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def __str__(self):
        return 'Latitude: {0}, Longitude: {1}'.format(self.latitude, self.longitude)

    def is_close_to(self, Location):
        tolerance = 0.005
        if (abs((self.latitude - Location.latitude) < tolerance)
            and (abs(self.longitude - Location.longitude) < tolerance)):
            return True

        return False

class Shoe():
    def __init__(self, filename, location, last_updated_date):
        self.filename = filename
        self.new_miles = 0
        self.location = location
        self.last_updated_date = last_updated_date

    def __str__(self):
        return 'Filename: {0}, New Miles: {1}, Location: {2}, Last Update: {3}'\
            .format(self.filename, self.new_miles, self.location, self.last_updated_date)

class ShoeLifetimeTracker():
    def __init__(self):
        self.token_handler = AccessTokenHandler()
        self.dt = DatetimeHelper()

    def _get_last_update_time(self, shoe_list):
        most_recently_updated_datetime = datetime.min

        for shoe in shoe_list:
            shoe_update_datetime = self.dt.string_to_datetime(shoe.last_updated_date)
            most_recently_updated_datetime = max(shoe_update_datetime, most_recently_updated_datetime)

        return most_recently_updated_datetime

    def _get_shoe_descriptors(self):
        shoe_list = []

        for shoe_file in os.listdir(SHOE_DESCRIPTORS):
            if os.path.splitext(shoe_file)[1] != '.json':
                continue
            shoe_info = read_from_json_file_named(os.path.join(SHOE_DESCRIPTORS, shoe_file))
            shoe_list.append(Shoe(
                shoe_file, 
                Location(shoe_info["Latitude"], 
                shoe_info['Longitude']), 
                shoe_info['LastUpdated']))

        return shoe_list

    def _update_shoe_descriptors(self, shoe_list, update_time):
        for shoe in shoe_list:
            if shoe.new_miles > 0:
                shoe_descriptor_file = read_from_json_file_named(os.path.join(SHOE_DESCRIPTORS, shoe.filename))
                shoe_descriptor_file['CurrentMileage'] += shoe.new_miles
                shoe_descriptor_file['LastUpdated'] = self.dt.datetime_to_string(update_time)
                shoe_descriptor_file['AtRisk'] = shoe_descriptor_file['CurrentMileage'] > 400

                write_data_to_json_file(shoe_descriptor_file, os.path.join(SHOE_DESCRIPTORS, shoe.filename))

    def _meters_to_miles(self, num_meters):
        return round(num_meters/1000 * MILES_PER_KM, 2)

    def correlate_mileage_to_shoes(self):
        available_shoes = self._get_shoe_descriptors()
        last_updated_date = self._get_last_update_time(available_shoes)
        most_recent_activity_datetime = datetime.min

        activity_fetcher = ActivityFetcher()
        relevant_activites = activity_fetcher.get_activities_since_date(last_updated_date)

        if not relevant_activites:
            return

        for activity in relevant_activites:
            most_recent_activity_datetime = max(self.dt.string_to_datetime(activity['start_date']), most_recent_activity_datetime)
            start_location = Location(activity['start_latlng'][0], activity['start_latlng'][1])
            
            for shoe in available_shoes:
                if start_location.is_close_to(shoe.location):
                    miles_to_add = self._meters_to_miles(activity['distance'])
                    shoe.new_miles += miles_to_add

                    print('Found a match for {0}, adding {1} miles'.format(shoe.filename, miles_to_add))
                    break

        self._update_shoe_descriptors(available_shoes, most_recent_activity_datetime)


if __name__ == '__main__':
    shoe_tracker = ShoeLifetimeTracker()
    shoe_tracker.correlate_mileage_to_shoes()
