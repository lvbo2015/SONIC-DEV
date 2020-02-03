#!/usr/bin/env python

__author__ = 'Wirut G.<wgetbumr@celestica.com>'
__license__ = "GPL"
__version__ = "0.2.0"
__status__ = "Development"

import requests
import re

NUM_FAN_TRAY = 5
NUM_ROTER = 2


class FanUtil():
    """Platform-specific FanUtil class"""

    def __init__(self):
        self.fan_info_url = "http://240.1.1.1:8080/api/fan/info"
        self.all_fan_dict = None

    def request_data(self, url):
        try:
            r = requests.get(url)
            data = r.json()
        except Exception as e:
            return {}
        return data

    def get_num_fans(self):
        """   
            Get the number of fans
            :return: int num_fans
        """
        all_fan_dict = self.get_all()
        num_fan_tray = all_fan_dict.get('Number', NUM_FAN_TRAY)

        return num_fan_tray * NUM_ROTER

    def get_fan_speed(self, fan_name):
        """
            Get the current speed of the fan, the unit is "RPM"  
            :return: int fan_speed
        """

        all_fan_dict = self.get_all()
        fan_info = all_fan_dict.get(fan_name, {})

        return fan_info.get('Speed', 0)

    def get_fan_low_threshold(self, fan_name):
        """
            Get the low speed threshold of the fan.
            if the current speed < low speed threshold, 
            the status of the fan is not ok.
            :return: int fan_low_threshold
        """

        all_fan_dict = self.get_all()
        fan_info = all_fan_dict.get(fan_name, {})

        return fan_info.get('LowThd', 0)

    def get_fan_high_threshold(self, fan_name):
        """
            Get the hight speed threshold of the fan, 
            if the current speed > high speed threshold, 
            the status of the fan is not ok
            :return: int fan_high_threshold 
        """
        all_fan_dict = self.get_all()
        fan_info = all_fan_dict.get(fan_name, {})

        return fan_info.get('HighThd', 0)

    def get_fan_pn(self, fan_name):
        """
            Get the product name of the fan
            :return: str fan_pn
        """

        all_fan_dict = self.get_all()
        fan_info = all_fan_dict.get(fan_name, {})

        return fan_info.get('PN', 'N/A')

    def get_fan_sn(self, fan_name):
        """
            Get the serial number of the fan
            :return: str fan_sn
        """
        all_fan_dict = self.get_all()
        fan_info = all_fan_dict.get(fan_name, {})

        return fan_info.get('SN', 'N/A')

    def get_fans_name_list(self):
        """
            Get list of fan name.
            :return: list fan_names
        """
        fan_names = []

        # Get the number of fans
        n_fan = self.get_num_fans()

        # Set fan name and add to the list.
        for x in range(1, n_fan + 1):
            f_index = int(round(float(x)/2))
            pos = 1 if x % 2 else 2
            fan_name = 'FAN{}_{}'.format(f_index, pos)
            fan_names.append(fan_name)

        return fan_names

    def get_all(self):
        """
            Get all information of system FANs, returns JSON objects in python 'DICT'.
            Number, mandatory, max number of FAN, integer
            FAN1_1, FAN1_2, ... mandatory, FAN name, string
            Present, mandatory for each FAN, present status, boolean, True for present, False for NOT present, read directly from h/w
            Running, conditional, if PRESENT is True, running status of the FAN, True for running, False for stopped, read directly from h/w
            Speed, conditional, if PRESENT is True, real FAN speed, float, read directly from h/w
            LowThd, conditional, if PRESENT is True, lower bound of FAN speed, float, read from h/w
            HighThd, conditional, if PRESENT is True, upper bound of FAN speed, float, read from h/w
            PN, conditional, if PRESENT is True, PN of the FAN, string
            SN, conditional, if PRESENT is True, SN of the FAN, string)
        """

        if not self.all_fan_dict:
            all_fan_dict = dict()

            fan_info_req = self.request_data(self.fan_info_url)
            fan_info_data = fan_info_req.get('data', {})
            all_fan_dict["Number"] = fan_info_data.get('Number', NUM_FAN_TRAY)

            for fan_idx in range(1, all_fan_dict["Number"] + 1):
                num_of_roter = fan_info_data.get('Rotors', NUM_ROTER)

                for fan_pos in range(1, num_of_roter + 1):
                    fan_key = 'FAN{}'.format(str(fan_idx))
                    roter_key = 'Rotor{}'.format(str(fan_pos))

                    fan_info = fan_info_data.get(fan_key, {})
                    roter_info = fan_info.get(roter_key, {})

                    fan_info_dict = dict()
                    fan_info_dict["Present"] = True if fan_info.get(
                        "Present") == 'yes' else False
                    fan_info_dict["Speed"] = roter_info.get("Speed", "N/A")
                    fan_info_dict["Running"] = True if roter_info.get(
                        "Running") == 'yes' else False
                    fan_info_dict["HighThd"] = roter_info.get(
                        "SpeedMax", "N/A")
                    fan_info_dict["LowThd"] = roter_info.get("SpeedMin", "N/A")
                    fan_info_dict["Status"] = False if roter_info.get(
                        "HwAlarm") == 'yes' else True
                    fan_info_dict["PN"] = fan_info.get("PN", "N/A")
                    fan_info_dict["SN"] = fan_info.get("SN", "N/A")
                    fan_info_dict["AirFlow"] = fan_info.get("AirFlow", "N/A")

                    fan_name = '{}_{}'.format(fan_key, fan_pos)
                    all_fan_dict[fan_name] = fan_info_dict
                    self.all_fan_dict = all_fan_dict

        return self.all_fan_dict
