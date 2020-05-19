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
FW_MODULE_NAME = 'fwmgrutil'
FW_CLASS_NAME = 'FwMgrUtil'
PYTHON_DIST = '/usr/lib/python2.7/dist-packages/'
BMC_INFO_URL = 'http://240.1.1.1:8080/api/bmc/info'


class TestFirmwareUtil(unittest.TestCase):

    def setUp(self):
        self.platform, self.hwsku = self.__get_platform_and_hwsku()
        self.platform_fwmgrutil = self.__load_platform_util(
            FW_MODULE_NAME, FW_CLASS_NAME)

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

    def __wait_bmc_restful(self):
        status = 0
        time.sleep(10)
        while status != 200:
            try:
                bmc_info_req = requests.get(BMC_INFO_URL, timeout=30)
                status = bmc_info_req.status_code
            except Exception as e:
                # print(e)
                pass
            time.sleep(10)

# # =================================================================== #
# # ============================ TEST CASE ============================ #
# # =================================================================== #

    def test_get_bmc_version(self):
        ret = self.platform_fwmgrutil.get_bmc_version()
        self.assertIsNotNone(ret, "BMC version is None")
        self.assertNotIn("N/A", ret)

    def test_get_running_bmc(self):
        ret = self.platform_fwmgrutil.get_running_bmc()
        self.assertIsNotNone(ret, "Running BMC is None")
        self.assertIn(ret, ['master', 'slave'])

    def test_get_cpld_version(self):
        ret = self.platform_fwmgrutil.get_cpld_version()
        self.assertIsNotNone(ret, "CPLD version is None")
        self.assertEquals(type(ret), dict)
        for cpld_name in ret:
            self.assertNotEqual("", ret[cpld_name])
            #self.assertIn(".", ret[cpld_name])

    def test_get_bios_version(self):
        ret = self.platform_fwmgrutil.get_bios_version()
        self.assertIsNotNone(ret, "BIOS version is None")
        self.assertIn(".", ret)

    def test_set_bmc_boot_flash(self):
        ret = self.platform_fwmgrutil.set_bmc_boot_flash("test")
        self.assertEqual(ret, False)

        ret = self.platform_fwmgrutil.set_bmc_boot_flash("slave")
        self.assertEqual(ret, True)
        self.platform_fwmgrutil.reboot_bmc()
        self.__wait_bmc_restful()
        ret = self.platform_fwmgrutil.get_running_bmc()
        self.assertEqual(ret, 'slave')

        ret = self.platform_fwmgrutil.set_bmc_boot_flash("master")
        self.assertEqual(ret, True)
        self.platform_fwmgrutil.reboot_bmc()
        self.__wait_bmc_restful()
        ret = self.platform_fwmgrutil.get_running_bmc()
        self.assertEqual(ret, 'master')

    def test_program_bmc_master(self):
        # switch to master bmc
        ret = self.platform_fwmgrutil.set_bmc_boot_flash("master")
        self.assertEqual(ret, True)
        if not ret:
            return

        self.platform_fwmgrutil.reboot_bmc()
        self.__wait_bmc_restful()

        ret = self.platform_fwmgrutil.get_running_bmc()
        self.assertEqual(ret, 'master')

        ret = self.platform_fwmgrutil.firmware_upgrade(
            "bmc", '/tmp/notthing', "master")
        self.assertEqual(ret, False)
        ret = self.platform_fwmgrutil.firmware_upgrade(
            "bmc", unittest_config.BMC_IMAGE_PATH, "test")
        self.assertEqual(ret, False)

        # master install master
        ret = self.platform_fwmgrutil.firmware_upgrade(
            "bmc", unittest_config.BMC_IMAGE_PATH, "master")
        self.assertEqual(ret, True)
        self.__wait_bmc_restful()

        # master install slave
        ret = self.platform_fwmgrutil.firmware_upgrade(
            "bmc", unittest_config.BMC_IMAGE_PATH, "slave")
        self.assertEqual(ret, True)
        self.__wait_bmc_restful()

        # master install both
        ret = self.platform_fwmgrutil.firmware_upgrade(
            "bmc", unittest_config.BMC_IMAGE_PATH, "both")
        self.assertEqual(ret, True)
        self.__wait_bmc_restful()

        # switch to master bmc
        ret = self.platform_fwmgrutil.set_bmc_boot_flash("master")
        self.assertEqual(ret, True)
        if not ret:
            return

        self.platform_fwmgrutil.reboot_bmc()
        self.__wait_bmc_restful()

        ret = self.platform_fwmgrutil.get_running_bmc()
        self.assertEqual(ret, 'master')
        # master pingpong mode
        ret = self.platform_fwmgrutil.firmware_upgrade(
            "bmc", unittest_config.BMC_IMAGE_PATH, "pingpong")
        self.assertEqual(ret, True)
        self.__wait_bmc_restful()
        ret = self.platform_fwmgrutil.get_running_bmc()
        self.assertEqual(ret, 'slave')

    def test_program_bmc_slave(self):
        # switch to slave bmc
        ret = self.platform_fwmgrutil.set_bmc_boot_flash("slave")
        self.assertEqual(ret, True)
        if not ret:
            return

        self.platform_fwmgrutil.reboot_bmc()
        self.__wait_bmc_restful()

        ret = self.platform_fwmgrutil.get_running_bmc()
        self.assertEqual(ret, 'slave')

        # slave install slave
        ret = self.platform_fwmgrutil.firmware_upgrade(
            "bmc", unittest_config.BMC_IMAGE_PATH, "slave")
        self.assertEqual(ret, True)
        self.__wait_bmc_restful()

        # slave install master
        ret = self.platform_fwmgrutil.firmware_upgrade(
            "bmc", unittest_config.BMC_IMAGE_PATH, "master")
        self.assertEqual(ret, True)
        self.__wait_bmc_restful()

        # master install both
        ret = self.platform_fwmgrutil.firmware_upgrade(
            "bmc", unittest_config.BMC_IMAGE_PATH, "both")
        self.assertEqual(ret, True)
        self.__wait_bmc_restful()

        # switch to slave bmc
        ret = self.platform_fwmgrutil.set_bmc_boot_flash("slave")
        self.assertEqual(ret, True)
        if not ret:
            return

        self.platform_fwmgrutil.reboot_bmc()
        self.__wait_bmc_restful()

        ret = self.platform_fwmgrutil.get_running_bmc()
        self.assertEqual(ret, 'slave')
        # slave pingpong mode
        ret = self.platform_fwmgrutil.firmware_upgrade(
            "bmc", unittest_config.BMC_IMAGE_PATH, "pingpong")
        self.assertEqual(ret, True)
        self.__wait_bmc_restful()
        ret = self.platform_fwmgrutil.get_running_bmc()
        self.assertEqual(ret, 'master')

    def test_get_bios_next_boot(self):
        ret = self.platform_fwmgrutil.get_bios_next_boot()
        self.assertIn(ret, ['master', 'slave'])

    def test_set_bios_next_boot(self):
        ret = self.platform_fwmgrutil.set_bios_next_boot("test")
        self.assertEqual(ret, False)

        ret = self.platform_fwmgrutil.set_bios_next_boot("slave")
        self.assertEqual(ret, True)
        ret = self.platform_fwmgrutil.get_bios_next_boot()
        self.assertEqual(ret, 'slave')

        ret = self.platform_fwmgrutil.set_bios_next_boot("master")
        self.assertEqual(ret, True)
        ret = self.platform_fwmgrutil.get_bios_next_boot()
        self.assertEqual(ret, 'master')

    def test_program_bios_master(self):
        # reboot to master bios
        #self.platform_fwmgrutil.set_bios_next_boot("master")
        #self.platform_fwmgrutil.reboot_bmc()
        #self.__wait_bmc_restful()

        #ret = self.platform_fwmgrutil.get_current_bios()
        #self.assertEqual(ret, 'master')

        # master install master
        ret = self.platform_fwmgrutil.firmware_upgrade(
            "bios", unittest_config.BIOS_IMAGE_PATH, "master")
        self.assertEqual(ret, True)
        self.__wait_bmc_restful()

        # master install slave
        ret = self.platform_fwmgrutil.firmware_upgrade(
            "bios", unittest_config.BIOS_IMAGE_PATH, "slave")
        self.assertEqual(ret, True)
        self.__wait_bmc_restful()

        # master install both
        ret = self.platform_fwmgrutil.firmware_upgrade(
            "bios", unittest_config.BIOS_IMAGE_PATH, "both")
        self.assertEqual(ret, True)
        self.__wait_bmc_restful()

    def test_program_bios_slave(self):
        # reboot to slave bios
        #self.platform_fwmgrutil.set_bios_next_boot("slave")
        #self.platform_fwmgrutil.reboot_bmc()
        #self.__wait_bmc_restful()

        #ret = self.platform_fwmgrutil.get_current_bios()
        #self.assertEqual(ret, 'slave')

        # slave install slave
        ret = self.platform_fwmgrutil.firmware_upgrade(
            "bios", unittest_config.BIOS_IMAGE_PATH, "slave")
        self.assertEqual(ret, True)
        self.__wait_bmc_restful()

        # slave install master
        ret = self.platform_fwmgrutil.firmware_upgrade(
            "bios", unittest_config.BIOS_IMAGE_PATH, "master")
        self.assertEqual(ret, True)
        self.__wait_bmc_restful()

        # master install both
        ret = self.platform_fwmgrutil.firmware_upgrade(
            "bios", unittest_config.BIOS_IMAGE_PATH, "both")
        self.assertEqual(ret, True)
        self.__wait_bmc_restful()

    def tearDown(self):
        pass
