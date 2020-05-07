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
TEST_PLAT_VAR = 'BMC_TEST_PLATFORM'
CEL_PLAT_VAL = 'CEL'


class TestFirmwareRefreshUtil(unittest.TestCase):

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
            except requests.exceptions.ConnectionError as e:
                # print(e)
                pass
            time.sleep(10)

    def __get_environment_var(self, variable):
        return os.getenv(variable, None)

    def __get_cpld_config(self):
        return unittest_config.CPLDTEST if not self.__get_environment_var(TEST_PLAT_VAR) == CEL_PLAT_VAL else unittest_config.CPLDTEST_CLS

# # =================================================================== #
# # ============================ TEST CASE ============================ #
# # =================================================================== #
    @unittest.skipIf(unittest_config.SKIP_REBOOT_CPU == True, "This case will cause CPU reboot")
    def test_firmware_refresh_bios(self):
        #ret = self.platform_fwmgrutil.firmware_program("bios", unittest_config.BIOS_IMAGE_PATH, "both")
        #self.assertEqual(ret, True)
        ret = self.platform_fwmgrutil.firmware_refresh(["BIOS"], None, None)
        self.assertEqual(ret, True)
       
    @unittest.skipIf(unittest_config.SKIP_REBOOT_CPU == True, "This case will cause CPU reboot")
    def test_firmware_refresh_fpga(self):
        ret = self.platform_fwmgrutil.firmware_program("FPGA", unittest_config.FPGA_IMAGE_PATH, "FPGA")
        self.assertEqual(ret, True)
        ret = self.platform_fwmgrutil.firmware_refresh(["FPGA"], None, None)
        self.assertEqual(ret, True)

    @unittest.skipIf(unittest_config.SKIP_REBOOT_CPU == True, "This case will cause CPU reboot")
    def test_firmware_refresh_base_cpld(self):
        cpld_list = self.__get_cpld_config()
        hwsku = self.hwsku.lower()
        cpld_flag = ""
        if "CPU_BOARD_CPLD" in cpld_list[hwsku]["program"]:
            cpld_flag = "CPU_BOARD_CPLD"
        elif "BASE_CPLD" in cpld_list[hwsku]["program"]:
            cpld_flag = "BASE_CPLD"
        else:
            return

        program_firmware_file = "/".join([unittest_config.CPLD_IMAGE_PATH, cpld_list[hwsku]["program"][cpld_flag]])
        ret = os.path.exists(program_firmware_file)
        self.assertEqual(ret, True)
        ret = self.platform_fwmgrutil.firmware_program("cpld", program_firmware_file, cpld_flag)
        self.assertEqual(ret, True)
        
        refresh_firmware_file = "/".join([unittest_config.CPLD_IMAGE_PATH, cpld_list[hwsku]["refresh"][cpld_flag]])
        ret = os.path.exists(refresh_firmware_file)
        self.assertEqual(ret, True)
        ret = self.platform_fwmgrutil.firmware_refresh(None, [cpld_flag], refresh_firmware_file)
        self.assertEqual(ret, True)

    @unittest.skipIf(unittest_config.SKIP_REBOOT_CPU == True, "This case will cause CPU reboot")
    def test_firmware_refresh_cpu_cpld(self):
        cpld_list = self.__get_cpld_config()
        hwsku = self.hwsku.lower()
        cpld_flag = ""
        if "CPU_MODULE_CPLD" in cpld_list[hwsku]["program"]:
            cpld_flag = "CPU_MODULE_CPLD"
        elif "CPU_CPLD" in cpld_list[hwsku]["program"]:
            cpld_flag = "CPU_CPLD"
        else:
            return

        program_firmware_file = "/".join([unittest_config.CPLD_IMAGE_PATH, cpld_list[hwsku]["program"][cpld_flag]])
        ret = os.path.exists(program_firmware_file)
        self.assertEqual(ret, True)
        ret = self.platform_fwmgrutil.firmware_program("cpld", program_firmware_file, cpld_flag)
        self.assertEqual(ret, True)
        
        refresh_firmware_file = 'None'
        if cpld_list[hwsku]["refresh"][cpld_flag].lower() != 'none':
            refresh_firmware_file = "/".join([unittest_config.CPLD_IMAGE_PATH, cpld_list[hwsku]["refresh"][cpld_flag]])
            ret = os.path.exists(refresh_firmware_file)
            self.assertEqual(ret, True)
        ret = self.platform_fwmgrutil.firmware_refresh(None, [cpld_flag], refresh_firmware_file)
        self.assertEqual(ret, True)
        
    @unittest.skipIf(unittest_config.SKIP_REBOOT_CPU == True, "This case will cause CPU reboot")
    def test_firmware_refresh_fan_cpld(self):
        cpld_list = self.__get_cpld_config()
        hwsku = self.hwsku.lower()
        if "CPU_BOARD_CPLD-FAN" in cpld_list[hwsku]["program"]:
            cpld_flag = "CPU_BOARD_CPLD-FAN"
        elif "FAN_CPLD" in cpld_list[hwsku]["program"]:
            cpld_flag = "FAN_CPLD"
        else:
            return

        program_firmware_file = "/".join([unittest_config.CPLD_IMAGE_PATH, cpld_list[hwsku]["program"][cpld_flag]])
        ret = os.path.exists(program_firmware_file)
        self.assertEqual(ret, True)
        ret = self.platform_fwmgrutil.firmware_program("cpld", program_firmware_file, cpld_flag)
        self.assertEqual(ret, True)
        
        refresh_firmware_file = "/".join([unittest_config.CPLD_IMAGE_PATH, cpld_list[hwsku]["refresh"][cpld_flag]])
        ret = os.path.exists(refresh_firmware_file)
        self.assertEqual(ret, True)
        ret = self.platform_fwmgrutil.firmware_refresh(None, [cpld_flag], refresh_firmware_file)
        self.assertEqual(ret, True)
        
    @unittest.skipIf(unittest_config.SKIP_REBOOT_CPU == True, "This case will cause CPU reboot")
    def test_firmware_refresh_cpld1(self):
        cpld_list = self.__get_cpld_config()
        hwsku = self.hwsku.lower()
        cpld_flag = ""
        if "MAC_BOARD_CPLD_1" in cpld_list[hwsku]["program"]:
            cpld_flag = "MAC_BOARD_CPLD_1"
        elif "LC_CPLD1" in cpld_list[hwsku]["program"]:
            cpld_flag = "LC_CPLD1"
        elif "SW_CPLD1" in cpld_list[hwsku]["program"]:
            cpld_flag = "SW_CPLD1"
        elif "TOP_LC_CPLD" in cpld_list[hwsku]["program"]:
            cpld_flag = "TOP_LC_CPLD"
        else:
            return

        program_firmware_file = "/".join([unittest_config.CPLD_IMAGE_PATH, cpld_list[hwsku]["program"][cpld_flag]])
        ret = os.path.exists(program_firmware_file)
        self.assertEqual(ret, True)
        ret = self.platform_fwmgrutil.firmware_program("cpld", program_firmware_file, cpld_flag)
        self.assertEqual(ret, True)
        
        refresh_firmware_file = 'None'
        if cpld_list[hwsku]["refresh"][cpld_flag].lower() != 'none':
            refresh_firmware_file = "/".join([unittest_config.CPLD_IMAGE_PATH, cpld_list[hwsku]["refresh"][cpld_flag]])
            ret = os.path.exists(refresh_firmware_file)
            self.assertEqual(ret, True)
        ret = self.platform_fwmgrutil.firmware_refresh(None, [cpld_flag], refresh_firmware_file)
        self.assertEqual(ret, True)
        
    @unittest.skipIf(unittest_config.SKIP_REBOOT_CPU == True, "This case will cause CPU reboot")
    def test_firmware_refresh_cpld2(self):
        cpld_list = self.__get_cpld_config()
        hwsku = self.hwsku.lower()
        cpld_flag = ""
        if "MAC_BOARD_CPLD_2" in cpld_list[hwsku]["program"]:
            cpld_flag = "MAC_BOARD_CPLD_2"
        elif "LC_CPLD2" in cpld_list[hwsku]["program"]:
            cpld_flag = "LC_CPLD2"
        elif "SW_CPLD2" in cpld_list[hwsku]["program"]:
            cpld_flag = "SW_CPLD2"
        elif "BOT_LC_CPLD" in cpld_list[hwsku]["program"]:
            cpld_flag = "BOT_LC_CPLD"
        else:
            return

        program_firmware_file = "/".join([unittest_config.CPLD_IMAGE_PATH, cpld_list[hwsku]["program"][cpld_flag]])
        ret = os.path.exists(program_firmware_file)
        self.assertEqual(ret, True)
        ret = self.platform_fwmgrutil.firmware_program("cpld", program_firmware_file, cpld_flag)
        self.assertEqual(ret, True)
        
        refresh_firmware_file = 'None'
        if cpld_list[hwsku]["refresh"][cpld_flag].lower() != 'none':
            refresh_firmware_file = "/".join([unittest_config.CPLD_IMAGE_PATH, cpld_list[hwsku]["refresh"][cpld_flag]])
            ret = os.path.exists(refresh_firmware_file)
            self.assertEqual(ret, True)
        ret = self.platform_fwmgrutil.firmware_refresh(None, [cpld_flag], refresh_firmware_file)
        self.assertEqual(ret, True)
        
    @unittest.skipIf(unittest_config.SKIP_REBOOT_CPU == True, "This case will cause CPU reboot")
    def test_firmware_refresh_cpld(self):
        cpld_list = self.__get_cpld_config()
        hwsku = self.hwsku.lower()
        cpld_type_str = ""
        cpld_file_str = ""
        for key, values in cpld_list[hwsku]["program"].items():
            program_firmware_file = "/".join([unittest_config.CPLD_IMAGE_PATH, values])
            ret = os.path.exists(program_firmware_file)
            self.assertEqual(ret, True)

            cpld_type_str += key + ":"
            cpld_file_str += program_firmware_file + ":"

        cpld_file_str = cpld_file_str[:-1]
        cpld_type_str = cpld_type_str[:-1]
        ret = self.platform_fwmgrutil.firmware_program("cpld", cpld_file_str, cpld_type_str)
        self.assertEqual(ret, True)

        cpld_type_list = []
        cpld_file_str = ""
        for key, values in cpld_list[hwsku]["refresh"].items():
            refresh_firmware_file = "/".join(
                    [unittest_config.CPLD_IMAGE_PATH, values])
            if str(values).lower() != "none":
                ret = os.path.exists(refresh_firmware_file)
                self.assertEqual(ret, True)

            cpld_type_list.append(key)
            cpld_file_str += refresh_firmware_file + ":"

        cpld_file_str = cpld_file_str[:-1]
        ret = self.platform_fwmgrutil.firmware_refresh(None, cpld_type_list, cpld_file_str)
        self.assertEqual(ret, True) 
