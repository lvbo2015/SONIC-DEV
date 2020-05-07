__version__ = "0.0.1"

import unittest_config
import subprocess
import unittest
import requests
import shutil
import time
import imp
import os

PLATFORM_ROOT_PATH = '/usr/share/sonic/device'
SONIC_CFGGEN_PATH = '/usr/local/bin/sonic-cfggen'
PLATFORM_KEY = 'DEVICE_METADATA.localhost.platform'
HWSKU_KEY = 'DEVICE_METADATA.localhost.hwsku'

FAN_MODULE_NAME = 'fanutil'
FAN_CLASS_NAME = 'FanUtil'
PSU_MODULE_NAME = 'psuutil'
PSU_CLASS_NAME = 'PsuUtil'
SENSOR_MODULE_NAME = 'sensorutil'
SENSOR_CLASS_NAME = 'SensorUtil'


class TestPlatformUtil(unittest.TestCase):

    def setUp(self):
        self.platform, self.hwsku = self.__get_platform_and_hwsku()

        self.platform_fanutil = self.__load_platform_util(
            FAN_MODULE_NAME, FAN_CLASS_NAME)

        self.platform_psuutil = self.__load_platform_util(
            PSU_MODULE_NAME, PSU_CLASS_NAME)

        self.platform_sensorutil = self.__load_platform_util(
            SENSOR_MODULE_NAME, SENSOR_CLASS_NAME)

    def __get_platform_and_hwsku(self):
        try:
            proc = subprocess.Popen([SONIC_CFGGEN_PATH, '-H', '-v', PLATFORM_KEY],
                                    stdout=subprocess.PIPE,
                                    shell=False,
                                    stderr=subprocess.STDOUT)
            stdout = proc.communicate()[0]
            proc.wait()
            platform = stdout.rstrip('\n')

            proc = subprocess.Popen([SONIC_CFGGEN_PATH, '-d', '-v', HWSKU_KEY],
                                    stdout=subprocess.PIPE,
                                    shell=False,
                                    stderr=subprocess.STDOUT)
            stdout = proc.communicate()[0]
            proc.wait()
            hwsku = stdout.rstrip('\n')
        except OSError as e:
            raise OSError("Cannot detect platform")

        return (platform, hwsku)

    def __load_platform_util(self, FW_MODULE_NAME, FW_CLASS_NAME):

        (platform, hwsku) = (self.platform, self.hwsku)
        platform_path = "/".join([PLATFORM_ROOT_PATH, platform])

        try:
            module_file = "/".join([platform_path,
                                    "plugins", FW_MODULE_NAME + ".py"])
            module = imp.load_source(FW_MODULE_NAME, module_file)
        except IOError as e:
            print("Failed to load platform module '%s': %s" % (
                FW_MODULE_NAME, str(e)), True)
            return -1

        try:
            platform_util_class = getattr(module, FW_CLASS_NAME)
            platform_util = platform_util_class()
        except AttributeError as e:
            print("Failed to instantiate '%s' class: %s" %
                  (FW_CLASS_NAME, str(e)), True)
            return -2

        return platform_util


# # =================================================================== #
# # ============================ TEST CASE ============================ #
# # =================================================================== #

    def test_fan_info(self):
        all_fan_data = self.platform_fanutil.get_all()
        self.assertIsNotNone(all_fan_data, "Fan data is None")
        self.assertIn("Number", all_fan_data.keys())
        self.assertNotIn("None", all_fan_data.keys())

        all_fan_data.pop("Number", None)
        for fan_name in all_fan_data:
            keys = all_fan_data[fan_name].keys()
            keys.sort()
            self.assertEqual(keys, unittest_config.FAN_KEY)

    def test_psu_info(self):
        all_psu_data = self.platform_psuutil.get_all()
        self.assertIsNotNone(all_psu_data, "PSU data is None")
        self.assertIn("Number", all_psu_data.keys())
        self.assertNotIn("None", all_psu_data.keys())

        all_psu_data.pop("Number", None)
        for psu_name in all_psu_data:
            keys = all_psu_data[psu_name].keys()
            keys.sort()
            self.assertEqual(keys, unittest_config.PSU_KEY)

    def test_sensor_info(self):
        all_ss_data = self.platform_sensorutil.get_all()
        self.assertIsNotNone(all_ss_data, "Sensor data is None")
        self.assertNotIn("None", all_ss_data.keys())
        for ss_name in all_ss_data:
            for ss_input in all_ss_data[ss_name]:
                keys = all_ss_data[ss_name][ss_input].keys()
                keys.sort()
                self.assertEqual(keys, unittest_config.SENSOR_KEY)

    def tearDown(self):
        pass
