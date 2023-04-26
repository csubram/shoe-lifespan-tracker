from datetime import datetime

class DatetimeHelper():
    def __init__(self):
        self.date_format = '%Y-%m-%dT%H:%M:%SZ'

    def string_to_datetime(self, input_string):
        return datetime.strptime(input_string, self.date_format)

    def datetime_to_string(self, input_datetime):
        return datetime.strftime(input_datetime, self.date_format)

    