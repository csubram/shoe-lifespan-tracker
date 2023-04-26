import sys
import os
import re
from datetime import datetime
from argparse import ArgumentParser
from authorization.json_utils import *

SHOE_DESCRIPTORS = 'shoes'
SHOE_TEMPLATE = 'shoe_template.json'

class ShoeFactory():
    def __init__(self):
        self.shoe_info = read_from_json_file_named(SHOE_TEMPLATE)

    def _create_filename(self, model, current_time):
        return '{0}_{1}.json'.format(datetime.strftime(current_time, '%Y_%m'), re.sub(r'\s+', '_', model, flags=re.UNICODE))

    def _add_timestamps(self, current_time):
        self.shoe_info['DateAcquired'] = datetime.strftime(current_time, '%Y-%m-%dT%H:%M:%SZ')
        self.shoe_info['LastUpdated'] = self.shoe_info['DateAcquired']

    def add_shoe(self, model_name: str, latitude: float, longitude: float):        
        self.shoe_info['Model'] = model_name
        self.shoe_info['Latitude'] = latitude
        self.shoe_info['Longitude'] = longitude

        current_time = datetime.now()
        self._add_timestamps(current_time)
        write_data_to_json_file(self.shoe_info, os.path.join(SHOE_DESCRIPTORS, self._create_filename(model_name, current_time)))

    def copy_shoe_from_file(self, model_name: str, copy_location_from: str):
        copy_from = read_from_json_file_named(os.path.join(SHOE_DESCRIPTORS, copy_location_from))
        self.add_shoe(model_name, copy_from['Latitude'], copy_from['Longitude'])

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--model', required=True, help='Model name of shoes (e.g. Brooks Adrenaline)')
    parser.add_argument('--latitude', type=float, help='Latitude of shoes; include 5 digits of precision for best results')
    parser.add_argument('--longitude', type=float, help='Longitude of shoes; include 5 digits of precision for best results')
    parser.add_argument('--from_filename', help='Copy shoe location from an existing shoe by filename')

    args = parser.parse_args()
    shoe_factory = ShoeFactory()

    if args.from_filename:
        shoe_factory.copy_shoe_from_file(args.model, args.from_filename)
    elif args.latitude and args.longitude:
        shoe_factory.add_shoe(args.model, args.latitude, args.longitude)
    else:
        raise Exception('Error: must provide latitude/longitude pair or filename as arguments')