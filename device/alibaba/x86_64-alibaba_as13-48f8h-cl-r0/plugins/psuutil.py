#!/usr/bin/env python

__author__ = 'Wirut G.<wgetbumr@celestica.com>'
__license__ = "GPL"
__version__ = "0.2.0"
__status__ = "Development"

import requests
import re

try:
    from sonic_psu.psu_base import PsuBase
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

NUM_PSU = 2


class PsuUtil(PsuBase):
    """Platform-specific PSUutil class"""

    def __init__(self):
        PsuBase.__init__(self)

        self.psu_info_url = "http://240.1.1.1:8080/api/psu/info"
        self.all_psu_dict = None

    def request_data(self, url):
        try:
            r = requests.get(url)
            data = r.json()
        except Exception as e:
            return {}
        return data

    def get_num_psus(self):
        """
        Retrieves the number of PSUs available on the device
        :return: An integer, the number of PSUs available on the device
        """

        all_psu_dict = self.get_all()

        return all_psu_dict.get('Number', NUM_PSU)

    def get_psu_status(self, index):
        """
        Retrieves the oprational status of power supply unit (PSU) defined
                by 1-based index <index>
        :param index: An integer, 1-based index of the PSU of which to query status
        :return: Boolean, True if PSU is operating properly, False if PSU is faulty
        """

        all_psu_dict = self.get_all()
        psu_key = 'PSU{}'.format(index)
        psu_info = all_psu_dict.get(psu_key, {})

        return psu_info.get('PowerStatus', False)

    def get_psu_presence(self, index):
        """
        Retrieves the presence status of power supply unit (PSU) defined
                by 1-based index <index>
        :param index: An integer, 1-based index of the PSU of which to query status
        :return: Boolean, True if PSU is plugged, False if not
        """
        all_psu_dict = self.get_all()
        psu_key = 'PSU{}'.format(index)
        psu_info = all_psu_dict.get(psu_key, {})

        return psu_info.get('Present', False)

    def get_psu_sn(self, index):
        """
        Get the serial number of the psu,

        :param index: An integer, 1-based index of the PSU.
        :return: Serial number
        """

        all_psu_dict = self.get_all()
        psu_key = 'PSU{}'.format(index)
        psu_info = all_psu_dict.get(psu_key, {})

        return psu_info.get('SN', False)

    def get_psu_pn(self, index):
        """
        Get the product name of the psu

        :param index: An integer, 1-based index of the PSU.
        :return: Product name
        """

        all_psu_dict = self.get_all()
        psu_key = 'PSU{}'.format(index)
        psu_info = all_psu_dict.get(psu_key, {})
        
        return psu_info.get('PN', False)

    def get_all(self):
        """
            Number: mandatory, max number of PSU, integer
            PSU1, PSU2, ...: mandatory, PSU name, string
            Present: mandatory for each PSU, present status, boolean, True for present, False for NOT present
            PowerStatus: conditional, if PRESENT is True, power status of PSU,boolean, True for powered, False for NOT powered
            PN, conditional, if PRESENT is True, PN of the PSU, string
            SN, conditional, if PRESENT is True, SN of the PSU, string
        """

        if not self.all_psu_dict:
            all_psu_dict = dict()

            psu_info_req = self.request_data(self.psu_info_url)
            psu_info_data = psu_info_req.get('data', {})
            all_psu_dict["Number"] = psu_info_data.get('Number', NUM_PSU)

            for psu_idx in range(1, all_psu_dict["Number"] + 1):
                psu_key = 'PSU{}'.format(str(psu_idx))
                psu_info = psu_info_data.get(psu_key, {})
                psu_input_info = psu_info.get('Inputs', {})
                psu_output_info = psu_info.get('Outputs', {})

                psu_info_dict = dict()
                psu_info_dict["InputType"] = psu_input_info.get("Type", "N/A")
                psu_info_dict["InputStatus"] = True if psu_input_info.get(
                    "Status") else False
                psu_info_dict["OutputStatus"] = True if psu_output_info.get(
                    "Status") else False
                psu_info_dict["PowerStatus"] = (
                    psu_info_dict["InputStatus"] and psu_info_dict["OutputStatus"])
                psu_info_dict["PN"] = psu_info.get("PN", "N/A")
                psu_info_dict["SN"] = psu_info.get("SN", "N/A")
                psu_info_dict["Present"] = True if psu_info.get("Present") == 'yes' else False
                psu_info_dict["AirFlow"] = psu_info.get("AirFlow", "N/A")

                all_psu_dict[psu_key] = psu_info_dict

            self.all_psu_dict = all_psu_dict

        return self.all_psu_dict
