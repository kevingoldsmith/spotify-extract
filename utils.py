import os
import datetime


def get_monthly_filename(directory, file_prefix, file_extension, year, month):
    return os.path.join(directory, '{}-{:04d}-{:02d}.{}'.format(file_prefix, year, month, file_extension))


def datetime_from_string(utc_time_String):
    return datetime.datetime.strptime(utc_time_String, '%Y-%m-%dT%H:%M:%S.%fZ')
