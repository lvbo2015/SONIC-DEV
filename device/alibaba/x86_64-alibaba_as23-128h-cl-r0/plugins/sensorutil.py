#!/usr/bin/env python

__author__ = 'Wirut G.<wgetbumr@celestica.com>'
__license__ = "GPL"
__version__ = "0.2.0"
__status__ = "Development"

import requests


class SensorUtil():
    """Platform-specific SensorUtil class"""

    def __init__(self):
        self.sensor_info_url = "http://240.1.1.1:8080/api/sensor/info"
        self.all_sensor_dict = None

    def request_data(self, url):
        try:
            r = requests.get(url)
            data = r.json()
        except Exception as e:
            return {}
        return data

    def input_type_selector(self, unit):
        # Set input type.
        return {
            "C": "temperature",
            "V": "voltage",
            "RPM": "RPM",
            "A": "amp",
            "W": "power"
        }.get(unit, unit)

    def input_name_selector(self, raw_sensor_name):

        sensor_name_list = raw_sensor_name.split('_')
        sensor_name = sensor_name_list[0]
        input_name = '_'.join(sensor_name_list[1:])

        if sensor_name_list[0] in ["TOP", "BOTTOM"]:
            sensor_name = '_'.join(sensor_name_list[0:2])
            input_name = '_'.join(sensor_name_list[2:])

        return str(sensor_name).upper(), str(input_name).upper()

    def get_num_sensors(self):
        """
            Get the number of sensors
            :return: int num_sensors
        """

        all_sensor_dict = self.get_all()

        return len(all_sensor_dict)

    def get_sensor_input_num(self, index):
        """
            Get the number of the input items of the specified sensor
            :return: int input_num
        """

        all_sensor_dict = self.get_all()
        ss_keys = all_sensor_dict.keys()[index]
        sensor_info = all_sensor_dict.get(ss_keys, {})
        ss_if_keys = sensor_info.keys()

        return len(ss_if_keys)

    def get_sensor_name(self, index):
        """
            Get the device name of the specified sensor.
            for example "coretemp-isa-0000"
            :return: str sensor_name
        """
        all_sensor_dict = self.get_all()
        sensor_name = all_sensor_dict.keys()[index]

        return sensor_name

    def get_sensor_input_name(self, sensor_index, input_index):
        """
            Get the input item name of the specified input item of the
            specified sensor index, for example "Physical id 0"
            :return: str sensor_input_name
        """

        all_sensor_dict = self.get_all()

        ss_keys = all_sensor_dict.keys()[sensor_index]
        sensor_info = all_sensor_dict.get(ss_keys, {})
        ss_if_keys = sensor_info.keys()[input_index]

        return ss_if_keys

    def get_sensor_input_type(self, sensor_index, input_index):
        """
            Get the item type of the specified input item of the specified sensor index,
            The return value should among  "valtage","temperature"
            :return: str sensor_input_type
        """

        all_sensor_dict = self.get_all()

        ss_keys = all_sensor_dict.keys()[sensor_index]
        sensor_info = all_sensor_dict.get(ss_keys, {})

        ss_if_keys = sensor_info.keys()[input_index]
        sensor_input_info = sensor_info.get(ss_if_keys, {})

        sensor_input_type = sensor_input_info.get('Type', "N/A")
        return sensor_input_type

    def get_sensor_input_value(self, sensor_index, input_index):
        """
            Get the current value of the input item, the unit is "V" or "C"
            :return: float sensor_input_value
        """

        all_sensor_dict = self.get_all()

        ss_keys = all_sensor_dict.keys()[sensor_index]
        sensor_info = all_sensor_dict.get(ss_keys, {})

        ss_if_keys = sensor_info.keys()[input_index]
        sensor_input_info = sensor_info.get(ss_if_keys, {})

        sensor_input_value = sensor_input_info.get('Value', 0.0)
        return sensor_input_value

    def get_sensor_input_low_threshold(self, sensor_index, input_index):
        """
            Get the low threshold of the value,
            the status of this item is not ok if the current value<low_threshold
            :return: float sensor_input_low_threshold
        """

        all_sensor_dict = self.get_all()

        ss_keys = all_sensor_dict.keys()[sensor_index]
        sensor_info = all_sensor_dict.get(ss_keys, {})

        ss_if_keys = sensor_info.keys()[input_index]
        sensor_input_info = sensor_info.get(ss_if_keys, {})

        sensor_input_low_threshold = sensor_input_info.get('LowThd', 0.0)
        return sensor_input_low_threshold

    def get_sensor_input_high_threshold(self, sensor_index, input_index):
        """
            Get the high threshold of the value,
            the status of this item is not ok if the current value > high_threshold
            :return: float sensor_input_high_threshold
        """
        all_sensor_dict = self.get_all()

        ss_keys = all_sensor_dict.keys()[sensor_index]
        sensor_info = all_sensor_dict.get(ss_keys, {})

        ss_if_keys = sensor_info.keys()[input_index]
        sensor_input_info = sensor_info.get(ss_if_keys, {})

        sensor_input_high_threshold = sensor_input_info.get('HighThd', 0.0)
        return sensor_input_high_threshold

    def get_all(self):
        """
            Get all information of system sensors, returns JSON objects in python 'DICT'.
            SensorName1, SensorName2, ... optional, string
            SensorInput1, SensorInput2, ... optional, string
            Type, mandatory in SensorInput$INDEX, should be on of { "temperature", "voltage", "power", "amp", "RPM" }
            Value, mandatory in SensorInput$INDEX, float , real value
            LowThd, mandatory in SensorInput$INDEX, float , lower bound of value
            HighThd, mandatory in SensorInput$INDEX, float , upper bound of value
            Return python 'dict' objects, example:
        """

        if not self.all_sensor_dict:
            all_sensor_dict = dict()

            sensor_info_req = self.request_data(self.sensor_info_url)
            sensor_info_data = sensor_info_req.get('data', {})

            for raw_ss_name, sensor_info in sensor_info_data.items():

                sensor_name, input_name = self.input_name_selector(raw_ss_name)
                sensor_dict = all_sensor_dict.get(sensor_name, {})
                new_sensor_dict = dict()
                new_sensor_dict["Type"] = self.input_type_selector(
                    sensor_info.get('Unit', 'N/A'))
                new_sensor_dict["Value"] = float(sensor_info.get('Value', 0.0))
                new_sensor_dict["HighThd"] = float(sensor_info.get('Max', 0.0))
                new_sensor_dict["LowThd"] = float(sensor_info.get('Min', 0.0))

                if sensor_dict == {}:
                    all_sensor_dict[sensor_name] = dict()

                input_name = input_name if input_name != '' else new_sensor_dict["Type"].upper(
                )
                sensor_dict[input_name] = new_sensor_dict
                all_sensor_dict[sensor_name].update(sensor_dict)

            self.all_sensor_dict = all_sensor_dict

        return self.all_sensor_dict
