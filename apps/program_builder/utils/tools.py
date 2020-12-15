#! /usr/bin/env python3
# coding: utf-8
from datetime import datetime, timedelta


class Tools:
    def convert_km_into_meters(self, km):
        """
        Convert kilometers into meters
        """
        return int(km * 1000)

    def convert_seconds_into_time(self, all_seconds):
        return str(timedelta(seconds=all_seconds))

    def convert_string_time_into_int_seconds(self, string_time):
        """
        convert a string time with %H:%M:%S format into an integer which represents
        the seconds
        """
        print(string_time)
        if len(string_time.split(":")) < 3:
            string_time = f'{string_time}:00'

        print(string_time)
        result = datetime.strptime(string_time, '%H:%M:%S')
        result = result.hour * 3600 + result.minute * 60 + result.second
        return result