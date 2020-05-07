__version__ = "0.0.1"

import unittest_config
import subprocess
import unittest
import requests
import shutil
import time
import imp
import os

BMCUTIL_CLASS = 'BmcUtilBase'
BMCUTIL_MODULE = 'bmcutil'
BMCUTIL_PATH = '/usr/local/etc/'
BMCUTIL_PATH1 = '/usr/local/bin/'
BMC_INFO_URL = 'http://240.1.1.1:8080/api/bmc/info'
LED_STATUS_URL = "http://240.1.1.1:8080/api/hw/locationled"
LED_STATUS = ['on', 'off']
RAW_CMD_URL = "http://240.1.1.1:8080/api/hw/rawcmd"
POWER_CYCLE = "http://240.1.1.1:8080/api/hw/powercycle"


class TestBMCUtil(unittest.TestCase):

    def setUp(self):
        self.bmc_util = self.__load_bmc_util()

    def __load_bmc_util(self):
        try:
            module_file = "/".join([BMCUTIL_PATH, BMCUTIL_MODULE + ".py"])
            module_file1 = "/".join([BMCUTIL_PATH1, BMCUTIL_MODULE + ".py"])
            module_file = module_file if os.path.exists(module_file) else module_file1
            module = imp.load_source(BMCUTIL_MODULE, module_file)
        except IOError as e:
            print("Failed to load platform module '%s': %s" % (
                BMCUTIL_MODULE, str(e)), True)
            return -1

        try:
            bmc_util_class = getattr(module, BMCUTIL_CLASS)
            bmc_util = bmc_util_class()
        except AttributeError as e:
            print("Failed to instantiate '%s' class: %s" %
                  (BMCUTIL_CLASS, str(e)), True)
            return -2

        return bmc_util

    def __wait_bmc_restful(self):
        status = 0
        time.sleep(10)
        while status != 200:
            try:
                bmc_info_req = requests.get(BMC_INFO_URL, timeout=30)
                status = bmc_info_req.status_code
            except requests.exceptions.ConnectionError as e:
                # print(e)
                pass
            time.sleep(10)

    def _get_from_bmc(self, uri):
        resp = requests.get(uri)
        if not resp:
            return None

        data = resp.json()
        if not data or "data" not in data or "status" not in data:
            return None

        if data["status"] != "OK":
            return None

        return data["data"]
    
    def _post_to_bmc(self, uri, data):
        resp = requests.post(uri, json=data)
        if not resp:
            return False

        data = resp.json()
        if "status" not in data:
            return False

        if data["status"] != "OK":
            return False

        return True

# # =================================================================== #
# # ============================ TEST CASE ============================ #
# # =================================================================== #

    def test_reboot_bmc(self):
        ret = self.bmc_util.reboot_bmc()
        self.assertEqual(ret, True)
        self.__wait_bmc_restful()

    def test_get_location_led(self):
        ret = self._get_from_bmc(LED_STATUS_URL)
        self.assertIn(ret["State"], LED_STATUS)

    def test_set_location_led(self):
        data = {}
        data["Command"] =  "error"
        ret = self._post_to_bmc(LED_STATUS_URL, data)
        self.assertEqual(ret, False)

        data = {}
        data["Command"] =  "on" 
        ret = self._post_to_bmc(LED_STATUS_URL, data)
        self.assertEqual(ret, True)
        ret = self._get_from_bmc(LED_STATUS_URL)
        self.assertEqual(ret["State"], 'on')
       
        data = {}
        data["Command"] =  "off"
        ret = self._post_to_bmc(LED_STATUS_URL, data)
        self.assertEqual(ret, True)
        ret = self._get_from_bmc(LED_STATUS_URL)
        self.assertEqual(ret["State"], 'off')

    def test_arbitrary_commands(self):
        data = {}
        data["Command"] = "ls -l /"
        ret = self._post_to_bmc(RAW_CMD_URL, data)
        self.assertEqual(ret, True)

    @unittest.skipIf(unittest_config.SKIP_REBOOT_CPU == True, "This case will cause CPU reboot")
    def test_power_cycle_cpu(self):
        data = {}
        data["Entity"] = "error"
        ret = self._post_to_bmc(POWER_CYCLE, data)
        self.assertEqual(ret, False)

        data = {}
        data["Entity"] = "cpu"
        ret = self._post_to_bmc(POWER_CYCLE, data)
        self.assertEqual(ret, True)

    @unittest.skipIf(unittest_config.SKIP_REBOOT_CPU == True, "This case will cause CPU reboot")
    def test_power_cycle_system(self):
        data = {}
        data["Entity"] = "error"
        ret = self._post_to_bmc(POWER_CYCLE, data)
        self.assertEqual(ret, False)

        data = {}
        data["Entity"] = "system"
        ret = self._post_to_bmc(POWER_CYCLE, data)
        self.assertEqual(ret, True)

