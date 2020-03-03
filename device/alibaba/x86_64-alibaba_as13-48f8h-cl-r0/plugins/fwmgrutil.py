#!/usr/bin/env python
#
# fwmgrutil.py
#
# Platform-specific firmware management interface for SONiC
#

__author__ = 'Wirut G.<wgetbumr@celestica.com>'
__license__ = "GPL"
__version__ = "0.2.0"
__status__ = "Development"

import subprocess
import requests
import os
import pexpect
import base64
import time
import json
import logging
import ast
from datetime import datetime

try:
    from sonic_fwmgr.fwgmr_base import FwMgrUtilBase
except ImportError as e:
    raise ImportError("%s - required module not found" % str(e))


class FwMgrUtil(FwMgrUtilBase):

    """Platform-specific FwMgrUtil class"""

    def __init__(self):
        self.platform_name = "AS1348f8h"
        self.onie_config_file = "/host/machine.conf"
        self.bmc_info_url = "http://240.1.1.1:8080/api/bmc/info"
        self.cpld_info_url = "http://240.1.1.1:8080/api/firmware/cpldversion"
        self.bmc_raw_command_url = "http://240.1.1.1:8080/api/hw/rawcmd"
        self.fw_upgrade_url = "http://240.1.1.1:8080/api/firmware/upgrade"
        self.fw_refresh_url = "http://240.1.1.1:8080/api/firmware/refresh"
        self.bios_next_boot = "http://240.1.1.1:8080/api/firmware/biosnextboot"
        self.bmc_next_boot = "http://240.1.1.1:8080/api/bmc/nextboot"
        self.bmc_reboot_url = "http://240.1.1.1:8080/api/bmc/reboot"
        self.bios_boot_info = "http://240.1.1.1:8080/api/misc/biosbootstatus"
        self.onie_config_file = "/host/machine.conf"
        self.fw_upgrade_logger_path = "/var/log/fw_upgrade.log"
        self.cpldb_version_path = "/sys/devices/platform/%s.cpldb/getreg" % self.platform_name
        self.fpga_version_path = "/sys/devices/platform/%s.switchboard/FPGA/getreg" % self.platform_name
        self.switchboard_cpld1_path = "/sys/devices/platform/%s.switchboard/CPLD1/getreg" % self.platform_name
        self.switchboard_cpld2_path = "/sys/devices/platform/%s.switchboard/CPLD2/getreg" % self.platform_name
        self.switchboard_cpld3_path = "/sys/devices/platform/%s.switchboard/CPLD3/getreg" % self.platform_name
        self.switchboard_cpld4_path = "/sys/devices/platform/%s.switchboard/CPLD4/getreg" % self.platform_name
        self.bmc_pwd_path = "/usr/local/etc/bmcpwd"
        self.cpld_name_list = ["CPU_CPLD",  "COMBO_CPLD",
                               "SW_CPLD1", "SW_CPLD2", "TOP_LC_CPLD", "BOT_LC_CPLD"]
        self.api_time_out = 300

    def __get_register_value(self, path, register):
        cmd = "echo {1} > {0}; cat {0}".format(path, register)
        p = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        raw_data, err = p.communicate()
        if err is not '':
            return 'None'
        else:
            return raw_data.strip()

    def __update_fw_upgrade_logger(self, header, message):
        if not os.path.isfile(self.fw_upgrade_logger_path):
            cmd = "sudo touch %s && sudo chmod +x %s" % (
                self.fw_upgrade_logger_path, self.fw_upgrade_logger_path)
            subprocess.Popen(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        logging.basicConfig(filename=self.fw_upgrade_logger_path,
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%b %d %H:%M:%S',
                            level=logging.INFO)

        log_message = "%s : %s" % (header, message)
        if header != "last_upgrade_result":
            print(log_message)
        return logging.info(log_message)

    def get_bmc_pass(self):
        if os.path.exists(self.bmc_pwd_path):
            with open(self.bmc_pwd_path) as file:
                data = file.read()

            key = "bmc"
            dec = []
            enc = base64.urlsafe_b64decode(data)
            for i in range(len(enc)):
                key_c = key[i % len(key)]
                dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
                dec.append(dec_c)
            return "".join(dec)
        return False

    def get_bmc_version(self):
        """Get BMC version from SONiC
        :returns: version string

        """
        bmc_version = None
        bmc_version_key = "Version"
        bmc_info_req = requests.get(self.bmc_info_url, timeout=self.api_time_out)
        if bmc_info_req.status_code == 200:
            bmc_info_json = bmc_info_req.json()
            bmc_info = bmc_info_json.get('data')
            bmc_version = bmc_info.get(bmc_version_key)
        return str(bmc_version)

    def upload_file_bmc(self, fw_path):
        scp_command = 'sudo scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r %s root@240.1.1.1:/home/root/' % os.path.abspath(fw_path)
        child = pexpect.spawn(scp_command)
        child.timeout=self.api_time_out
        i = child.expect(["root@240.1.1.1's password:"])
        bmc_pwd = self.get_bmc_pass()
        if i == 0 and bmc_pwd:
            child.sendline(bmc_pwd)
            data = child.read()
            print(data)
            child.close
            return os.path.isfile(fw_path)
        return False

    def get_cpld_version(self):
        """Get CPLD version from SONiC
        :returns: dict like {'CPLD_1': version_string, 'CPLD_2': version_string}
        """

        CPLD_B = self.__get_register_value(self.cpldb_version_path, '0xA100')
        CPLD_C = self.__get_register_value(self.cpldb_version_path, '0xA1E0')
        CPLD_1 = self.__get_register_value(self.switchboard_cpld1_path, '0x00')
        CPLD_2 = self.__get_register_value(self.switchboard_cpld2_path, '0x00')
        CPLD_3 = self.__get_register_value(self.switchboard_cpld3_path, '0x00')
        CPLD_4 = self.__get_register_value(self.switchboard_cpld4_path, '0x00')

        fan_cpld_key = "CPLD_FAN"
        fan_cpld = None
        fan_cpld_req = requests.get(self.cpld_info_url)
        if fan_cpld_req.status_code == 200:
            fancpld_info_json = fan_cpld_req.json()
            fancpld_info_data = fancpld_info_json.get('data')
            fan_cpld = fancpld_info_data.get(fan_cpld_key)

        CPLD_B = 'None' if CPLD_B is 'None' else "{}.{}".format(
            int(CPLD_B[2], 16), int(CPLD_B[3], 16))
        CPLD_C = 'None' if CPLD_C is 'None' else "{}.{}".format(
            int(CPLD_C[2], 16), int(CPLD_C[3], 16))
        CPLD_1 = 'None' if CPLD_1 is 'None' else "{}.{}".format(
            int(CPLD_1[2], 16), int(CPLD_1[3], 16))
        CPLD_2 = 'None' if CPLD_2 is 'None' else "{}.{}".format(
            int(CPLD_2[2], 16), int(CPLD_2[3], 16))
        CPLD_3 = 'None' if CPLD_3 is 'None' else "{}.{}".format(
            int(CPLD_3[2], 16), int(CPLD_3[3], 16))
        CPLD_4 = 'None' if CPLD_4 is 'None' else "{}.{}".format(
            int(CPLD_4[2], 16), int(CPLD_4[3], 16))
        FAN_CPLD = 'None' if fan_cpld is None else fan_cpld

        cpld_version_dict = {}
        cpld_version_dict.update({'CPLD_B': CPLD_B})
        cpld_version_dict.update({'CPLD_C': CPLD_C})
        cpld_version_dict.update({'CPLD_1': CPLD_1})
        cpld_version_dict.update({'CPLD_2': CPLD_2})
        cpld_version_dict.update({'CPLD_3': CPLD_3})
        cpld_version_dict.update({'CPLD_4': CPLD_4})
        cpld_version_dict.update({'CPLD_FAN': FAN_CPLD})

        return cpld_version_dict

    def get_bios_version(self):
        """Get BIOS version from SONiC
        :returns: version string

        """
        bios_version = None

        p = subprocess.Popen(
            ["sudo", "dmidecode", "-s", "bios-version"], stdout=subprocess.PIPE)
        raw_data = str(p.communicate()[0])
        if raw_data == '':
            return str(None)
        raw_data_list = raw_data.split("\n")
        bios_version = raw_data_list[0] if len(
            raw_data_list) == 1 else raw_data_list[-2]

        return str(bios_version).strip()

    def get_onie_version(self):
        """Get ONiE version from SONiC
        :returns: version string

        """
        onie_verison = None

        onie_version_keys = "onie_version"
        onie_config_file = open(self.onie_config_file, "r")
        for line in onie_config_file.readlines():
            if onie_version_keys in line:
                onie_version_raw = line.split('=')
                onie_verison = onie_version_raw[1].strip()
                break
        onie_config_file.close()
        return str(onie_verison)

    def get_pcie_version(self):
        """Get PCiE version from SONiC
        :returns: version dict { "PCIE_FW_LOADER": "2.5", "PCIE_FW": "D102_08" }

        """
        cmd = "sudo bcmcmd 'pciephy fw version'"
        p = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        raw_data, err = p.communicate()

        pcie_version = dict()
        pcie_version["PCIE_FW_LOADER"] = 'None'
        pcie_version["PCIE_FW"] = 'None'

        if err == '':
            lines = raw_data.split('\n')
            for line in lines:
                if 'PCIe FW loader' in line:
                    pcie_version["PCIE_FW_LOADER"] = line.split(':')[1].strip()
                elif 'PCIe FW version' in line:
                    pcie_version["PCIE_FW"] = line.split(':')[1].strip()
        return pcie_version

    def get_fpga_version(self):
        """Get FPGA version from SONiC
        :returns: version string

        """
        version = self.__get_register_value(self.fpga_version_path, '0x00')
        if version is not 'None':
            version = "{}.{}".format(
                int(version[2:][1:4], 16), int(version[2:][4:], 16))
        return str(version)

    def firmware_upgrade(self, fw_type, fw_path, fw_extra=None):
        """
            @fw_type MANDATORY, firmware type, should be one of the strings: 'cpld', 'fpga', 'bios', 'bmc'
            @fw_path MANDATORY, target firmware file
            @fw_extra OPTIONAL, extra information string,

            for fw_type 'cpld' and 'fpga': it can be used to indicate specific cpld, such as 'cpld1', 'cpld2', ...
                or 'cpld_fan_come_board', etc. If None, upgrade all CPLD/FPGA firmware. for fw_type 'bios' and 'bmc',
                 value should be one of 'master' or 'slave' or 'both'
        """
        fw_type = fw_type.lower()
        bmc_pwd = self.get_bmc_pass()
        if not bmc_pwd and fw_type != "fpga":
            self.__update_fw_upgrade_logger(
                "fw_upgrade", "fail, message=BMC credential not found")
            return False

        if fw_type == 'bmc':
            fw_extra_str = str(fw_extra).lower()
            if fw_extra_str not in ["master", "slave", "both", "pingpong"]:
                return False

            self.__update_fw_upgrade_logger(
                "bmc_upgrade", "start BMC upgrade")
            # Copy BMC image file to BMC
            last_fw_upgrade = ["BMC", fw_path, fw_extra_str, "FAILED"]
            upload_file = self.upload_file_bmc(fw_path)
            if not upload_file:
                self.__update_fw_upgrade_logger(
                    "fw_upgrade", "fail, message=unable to upload BMC image to BMC")
                self.__update_fw_upgrade_logger(
                    "last_upgrade_result", str(last_fw_upgrade))
                return False

            filename_w_ext = os.path.basename(fw_path)
            json_data = dict()
            json_data["Name"] = "bmc"
            json_data["Path"] = "/home/root/%s" % filename_w_ext

            # Set flash type
            current_bmc = self.get_running_bmc()
            flash = fw_extra_str if fw_extra_str in [
                "master", "slave", "both"] else "both"
            if fw_extra_str == "pingpong":
                #flash = "master" if current_bmc == "slave" else "slave"
                flash = "slave"
            json_data["Flash"] = flash

            # Install BMC
            if flash == "both":
                self.__update_fw_upgrade_logger(
                    "bmc_upgrade", "install BMC as master mode")
                json_data["Flash"] = "master"
                r = requests.post(self.fw_upgrade_url, json=json_data)
                if r.status_code != 200 or r.json().get('status') != 'OK':
                    self.__update_fw_upgrade_logger(
                        "bmc_upgrade", "fail, message={}".format(r.json().get('messages')))
                    self.__update_fw_upgrade_logger(
                        "last_upgrade_result", str(last_fw_upgrade))
                    return False
                json_data["Flash"] = "slave"

            self.__update_fw_upgrade_logger(
                "bmc_upgrade", "install BMC as %s mode" % json_data["Flash"])
            r = requests.post(self.fw_upgrade_url, json=json_data)
            if r.status_code == 200 and r.json().get('status') == 'OK':
                if fw_extra_str == "pingpong":
                    flash = "master" if current_bmc == "slave" else "slave"
                    self.__update_fw_upgrade_logger(
                        "bmc_upgrade", "switch to boot from %s" % flash)
                    self.set_bmc_boot_flash(flash)
                    self.__update_fw_upgrade_logger(
                        "bmc_upgrade", "reboot BMC")
                    if not self.reboot_bmc():
                        return False
                else:
                    self.__update_fw_upgrade_logger(
                        "bmc_upgrade", "reboot BMC")
                    reboot_dict = {}
                    reboot_dict["reboot"] = "yes"
                    r = requests.post(self.bmc_info_url, json=reboot_dict)
                last_fw_upgrade[3] = "DONE"
            else:
                self.__update_fw_upgrade_logger(
                    "bmc_upgrade", "fail, message={}".format(r.json().get('messages')))
                self.__update_fw_upgrade_logger(
                    "last_upgrade_result", str(last_fw_upgrade))
                return False

            self.__update_fw_upgrade_logger(
                "bmc_upgrade", "done")
            self.__update_fw_upgrade_logger(
                "last_upgrade_result", str(last_fw_upgrade))
            return True

        elif fw_type == 'fpga':
            last_fw_upgrade = ["FPGA", fw_path, None, "FAILED"]
            self.__update_fw_upgrade_logger(
                "fpga_upgrade", "start FPGA upgrade")

            if not os.path.isfile(fw_path):
                self.__update_fw_upgrade_logger(
                    "fpga_upgrade", "fail, message=FPGA image not found %s" % fw_path)
                self.__update_fw_upgrade_logger(
                    "last_upgrade_result", str(last_fw_upgrade))
                return False

            command = 'fpga_prog ' + fw_path
            print("Running command : %s" % command)
            process = subprocess.Popen(
                command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break

            rc = process.returncode
            if rc != 0:
                self.__update_fw_upgrade_logger(
                    "fw_upgrade", "fail, message=unable to install FPGA")
                self.__update_fw_upgrade_logger(
                    "last_upgrade_result", str(last_fw_upgrade))
                return False

            self.__update_fw_upgrade_logger("fpga_upgrade", "done")
            last_fw_upgrade[3] = "DONE"
            self.__update_fw_upgrade_logger(
                "last_upgrade_result", str(last_fw_upgrade))
            self.firmware_refresh(["FPGA"], None, None)
            return True

        elif 'cpld' in fw_type:
            self.__update_fw_upgrade_logger(
                "cpld_upgrade", "start CPLD upgrade")
            # Check input
            fw_extra_str = str(fw_extra).upper()
            if ":" in fw_path and ":" in fw_extra_str:
                fw_path_list = fw_path.split(":")
                fw_extra_str_list = fw_extra_str.split(":")
            else:
                fw_path_list = [fw_path]
                fw_extra_str_list = [fw_extra_str]

            if len(fw_path_list) != len(fw_extra_str_list):
                self.__update_fw_upgrade_logger(
                    "cpld_upgrade", "fail, message=invalid input")
                return False

            data_list = list(zip(fw_path_list, fw_extra_str_list))
            refresh_img_path = None
            cpld_result_list = ["FAILED" for i in range(
                0, len(fw_extra_str_list))]
            last_fw_upgrade = ["CPLD", ":".join(
                fw_path_list), ":".join(fw_extra_str_list), ":".join(cpld_result_list)]
            for i in range(0, len(data_list)):
                data = data_list[i]
                fw_path = data[0]
                fw_extra_str = data[1]

                # Set fw_extra
                fw_extra_str = {
                    "TOP_LC_CPLD": "top_lc",
                    "BOT_LC_CPLD": "bottom_lc",
                    "FAN_CPLD": "fan",
                    "CPU_CPLD": "cpu",
                    "BASE_CPLD": "base",
                    "COMBO_CPLD": "combo",
                    "SW_CPLD1": "switch",
                    "SW_CPLD2": "switch",
                    "REFRESH_CPLD": "refresh"
                }.get(fw_extra_str, None)

                if fw_extra_str == "refresh":
                    refresh_img_path = fw_path
                    del cpld_result_list[i]
                    del fw_extra_str_list[i]
                    continue

                if fw_extra_str is None:
                    self.__update_fw_upgrade_logger(
                        "cpld_upgrade", "fail, message=invalid extra information string")
                    continue

                # Uploading image to BMC
                self.__update_fw_upgrade_logger(
                    "cpld_upgrade", "start %s upgrade" % data[1])
                upload_file = self.upload_file_bmc(fw_path)
                if not upload_file:
                    self.__update_fw_upgrade_logger(
                        "cpld_upgrade", "fail, message=unable to upload BMC image to BMC")
                    continue

                filename_w_ext = os.path.basename(fw_path)
                json_data = dict()
                json_data["Path"] = "/home/root/%s" % filename_w_ext
                json_data["Name"] = "cpld"

                # Call BMC api to install cpld image
                print("Installing...")
                r = requests.post(self.fw_upgrade_url, json=json_data)
                if r.status_code != 200 or r.json().get('status') != 'OK':
                    self.__update_fw_upgrade_logger(
                        "cpld_upgrade", "fail, message={}".format(r.json().get('messages')))
                    continue

                cpld_result_list[i] = "DONE"
                self.__update_fw_upgrade_logger(
                    "cpld_upgrade", "%s upgrade done" % data[1])
            last_fw_upgrade[3] = ":".join(cpld_result_list)
            self.__update_fw_upgrade_logger(
                "cpld_upgrade", "done")
            self.__update_fw_upgrade_logger(
                "last_upgrade_result", str(last_fw_upgrade))

            # Refresh CPLD
            refresh_img_str_list = []
            for fw_extra in fw_extra_str_list:
                if "BASE_CPLD" in fw_extra or "FAN_CPLD" in fw_extra:
                    refresh_img_str_list.append(refresh_img_path)
                else:
                    refresh_img_str_list.append("None")
            self.firmware_refresh(None, fw_extra_str_list,
                                  ":".join(refresh_img_str_list))

            return True

        elif 'bios' in fw_type:
            fw_extra_str = str(fw_extra).lower()
            if fw_extra_str not in ["master", "slave", "both"]:
                return False

            self.__update_fw_upgrade_logger(
                "bios_upgrade", "start BIOS upgrade")
            last_fw_upgrade = ["BIOS", fw_path, None, "FAILED"]
            fw_extra_str = str(fw_extra).lower()
            flash = fw_extra_str.lower()

            if not os.path.exists(fw_path):
                self.__update_fw_upgrade_logger(
                    "bios_upgrade", "fail, message=image not found")
                return False

            upload_file = self.upload_file_bmc(fw_path)
            if not upload_file:
                self.__update_fw_upgrade_logger(
                    "bios_upgrade", "fail, message=unable to upload image to BMC")
                self.__update_fw_upgrade_logger(
                    "last_upgrade_result", str(last_fw_upgrade))
                return False

            # json_data = dict()
            # json_data["Command"] = "/usr/bin/ipmitool -b 1 -t 0x2c raw 0x2e 0xdf 0x57 0x01 0x00 0x01"
            # r = requests.post(self.bmc_raw_command_url, json=json_data)
            # if r.status_code != 200:
            #     self.__update_fw_upgrade_logger(
            #         "bios_upgrade", "fail, message=unable to set state")
            #     self.__update_fw_upgrade_logger(
            #         "last_upgrade_result", str(last_fw_upgrade))
            #     return False

            filename_w_ext = os.path.basename(fw_path)
            json_data = dict()
            json_data["Path"] = "/home/root/%s" % filename_w_ext
            json_data["Name"] = "bios"
            json_data["Flash"] = flash

            print("Installing...")
            r = requests.post(self.fw_upgrade_url, json=json_data)
            if r.status_code != 200 or r.json().get('status') != 'OK':
                print(r.json())
                self.__update_fw_upgrade_logger(
                    "bios_upgrade", "fail, message={}".format(r.json().get('messages')))
                self.__update_fw_upgrade_logger(
                    "last_upgrade_result", str(last_fw_upgrade))
                return False

            last_fw_upgrade[3] = "DONE"
            self.__update_fw_upgrade_logger(
                "bios_upgrade", "done")
            self.__update_fw_upgrade_logger(
                "last_upgrade_result", str(last_fw_upgrade))
        else:
            self.__update_fw_upgrade_logger(
                "fw_upgrade", "fail, message=invalid firmware type")
            return False

        return True

    def get_last_upgrade_result(self):
        """
            Get last firmware upgrade information, inlcudes:
            1) FwType: cpld/fpga/bios/bmc(passed by method 'firmware_upgrade'), string
            2) FwPath: path and file name of firmware(passed by method 'firmware_upgrade'), string
            3) FwExtra: designated string, econdings of this string is determined by vendor(passed by method 'firmware_program')
            4) Result: indicates whether the upgrade action is performed and success/failure status if performed. Values should be one of: "DONE"/"FAILED"/"NOT_PERFORMED".
            list of object:
            [
                {
                    "FwType": "cpld",
                    "FwPath": "cpu_cpld.vme"
                    "FwExtra":"CPU_CPLD"
                    "Result": "DONE"
                },
                {
                    "FwType": "cpld",
                    "FwPath": "fan_cpld.vme"
                    "FwExtra": "FAN_CPLD"
                    "Result": "FAILED"
                }
            ]
        """
        last_update_list = []

        if os.path.exists(self.fw_upgrade_logger_path):
            with open(self.fw_upgrade_logger_path, 'r') as file:
                lines = file.read().splitlines()

            upgrade_txt = [i for i in reversed(
                lines) if "last_upgrade_result" in i]
            if len(upgrade_txt) > 0:
                last_upgrade_txt = upgrade_txt[0].split(
                    "last_upgrade_result : ")
                last_upgrade_list = ast.literal_eval(last_upgrade_txt[1])
                for x in range(0, len(last_upgrade_list[1].split(":"))):
                    upgrade_dict = {}
                    upgrade_dict["FwType"] = last_upgrade_list[0].lower()
                    upgrade_dict["FwPath"] = last_upgrade_list[1].split(":")[x]
                    upgrade_dict["FwExtra"] = last_upgrade_list[2].split(":")[
                        x] if last_upgrade_list[2] else "None"
                    upgrade_dict["Result"] = last_upgrade_list[3].split(":")[x]
                    last_update_list.append(upgrade_dict)

        return last_update_list

    def firmware_program(self, fw_type, fw_path, fw_extra=None):
        """
            Program FPGA and/or CPLD firmware only, but do not refresh them

            @param fw_type value can be: FPGA, CPLD
            @param fw_path a string of firmware file path, seperated by ':', it should
                        match the sequence of param @fw_type
            @param fw_extra a string of firmware subtype, i.e CPU_CPLD, BOARD_CPLD,
                            FAN_CPLD, LC_CPLD, etc. Subtypes are seperated by ':'
            @return True when all required firmware is program succefully,
                    False otherwise.

            Example:
                self.firmware_program("CPLD", "/cpu_cpld.vme:/lc_cpld", \
                                    "CPU_CPLD:LC_CPLD")
                or
                self.firmware_program("FPGA", "/fpga.bin")
        """
        fw_type = fw_type.lower()
        bmc_pwd = self.get_bmc_pass()
        if not bmc_pwd and fw_type != "fpga":
            self.__update_fw_upgrade_logger(
                "fw_upgrade", "fail, message=BMC credential not found")
            return False

        if fw_type == 'fpga':
            last_fw_upgrade = ["FPGA", fw_path, None, "FAILED"]
            self.__update_fw_upgrade_logger(
                "fpga_upgrade", "start FPGA upgrade")

            if not os.path.isfile(fw_path):
                self.__update_fw_upgrade_logger(
                    "fpga_upgrade", "fail, message=FPGA image not found %s" % fw_path)
                self.__update_fw_upgrade_logger(
                    "last_upgrade_result", str(last_fw_upgrade))
                return False

            command = 'fpga_prog ' + fw_path
            print("Running command: %s" % command)
            process = subprocess.Popen(
                command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break

            rc = process.returncode
            if rc != 0:
                self.__update_fw_upgrade_logger(
                    "fw_upgrade", "fail, message=Unable to install FPGA")
                self.__update_fw_upgrade_logger(
                    "last_upgrade_result", str(last_fw_upgrade))
                return False

            self.__update_fw_upgrade_logger("fpga_upgrade", "done")
            last_fw_upgrade[3] = "DONE"
            self.__update_fw_upgrade_logger(
                "last_upgrade_result", str(last_fw_upgrade))
            return True

        elif 'cpld' in fw_type:
            self.__update_fw_upgrade_logger(
                "cpld_upgrade", "start CPLD upgrade")

            # Check input
            fw_extra_str = str(fw_extra).upper()
            if ":" in fw_path and ":" in fw_extra_str:
                fw_path_list = fw_path.split(":")
                fw_extra_str_list = fw_extra_str.split(":")
            else:
                fw_path_list = [fw_path]
                fw_extra_str_list = [fw_extra_str]

            if len(fw_path_list) != len(fw_extra_str_list):
                self.__update_fw_upgrade_logger(
                    "cpld_upgrade", "fail, message=Invalid input")
                return False

            cpld_result_list = []
            data_list = list(zip(fw_path_list, fw_extra_str_list))
            for data in data_list:
                fw_path = data[0]
                fw_extra_str = data[1]

                # Set fw_extra
                fw_extra_str = {
                    "TOP_LC_CPLD": "top_lc",
                    "BOT_LC_CPLD": "bottom_lc",
                    "FAN_CPLD": "fan",
                    "CPU_CPLD": "cpu",
                    "BASE_CPLD": "base",
                    "COMBO_CPLD": "combo",
                    "SW_CPLD1": "switch",
                    "SW_CPLD2": "switch"
                }.get(fw_extra_str, None)

                self.__update_fw_upgrade_logger(
                    "cpld_upgrade", "start %s upgrade" % data[1])
                upgrade_result = "FAILED"
                for x in range(1, 4):
                    # Set fw_extra
                    if x > 1:
                        self.__update_fw_upgrade_logger(
                            "cpld_upgrade", "fail, message=Retry to upgrade %s" % data[1])

                    elif fw_extra_str is None:
                        self.__update_fw_upgrade_logger(
                            "cpld_upgrade", "fail, message=Invalid extra information string %s" % data[1])
                        break
                    elif not os.path.isfile(os.path.abspath(fw_path)):
                        self.__update_fw_upgrade_logger(
                            "cpld_upgrade", "fail, message=CPLD image not found %s" % fw_path)
                        break

                    # Install cpld image via ispvm tool
                    print("Installing...")
                    command = 'ispvm %s' % fw_path
                    if fw_extra_str in ["top_lc", "bottom_lc"]:
                        option = 1 if fw_extra_str == "top_lc" else 2
                        command = "ispvm -c %d %s" % (option,
                                                      os.path.abspath(fw_path))
                    print("Running command : %s" % command)
                    process = subprocess.Popen(
                        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                    while True:
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break

                    rc = process.returncode
                    if rc != 0:
                        self.__update_fw_upgrade_logger(
                            "cpld_upgrade", "fail, message=Unable to install CPLD")
                        continue

                    upgrade_result = "DONE"
                    self.__update_fw_upgrade_logger("cpld_upgrade", "done")
                    break
                cpld_result_list.append(upgrade_result)

            last_fw_upgrade = ["CPLD", ":".join(
                fw_path_list), ":".join(fw_extra_str_list), ":".join(cpld_result_list)]
            self.__update_fw_upgrade_logger(
                "last_upgrade_result", str(last_fw_upgrade))
            return "FAILED" not in cpld_result_list
        else:
            self.__update_fw_upgrade_logger(
                "fw_upgrade", "fail, message=Invalid firmware type")
            return False

        return True

    def firmware_refresh(self, fpga_list, cpld_list, fw_extra=None):
        """
            Refresh firmware and take extra action when necessary.
            @param fpga_list a list of FPGA names
            @param cpld_list a list of CPLD names
            @return True if refresh succefully and no power cycle action is taken.

            @Note extra action should be: power cycle the whole system(except BMC) when
                                        CPU_CPLD or BOARD_CPLD or FPGA is refreshed.
                                        No operation if the power cycle is not needed.

            Example:
            self.firmware_refresh(
                ["FPGA"], ["BASE_CPLD", "LC_CPLD"],"/tmp/fw/refresh.vme")
            or
            self.firmware_refresh(["FPGA"], None, None)
            or
            self.firmware_refresh(None, ["FAN_CPLD", "LC1_CPLD", "BASE_CPLD"],
                                  "/tmp/fw/fan_refresh.vme:none:/tmp/fw/base_refresh.vme")
        """
        self.__update_fw_upgrade_logger(
            "fw_refresh", "start firmware refresh")

        cpld_list = [x.lower() for x in cpld_list] if cpld_list else []
        fpga_list = [x.lower() for x in fpga_list] if fpga_list else []
        refresh_list = cpld_list + fpga_list
        fw_path_list = fw_extra.split(
            ':') if not fpga_list else fw_extra.split(':') + ["none"]

        if len(refresh_list) == 0 \
            or ((len(fpga_list) > 1 and "fpga" not in fpga_list)) \
                or (len(refresh_list) != len(fw_path_list)):
            self.__update_fw_upgrade_logger(
                "fw_refresh", "fail, message=Invalid input")
            return False

        for idx in range(0, len(cpld_list)):
            fw_path = fw_path_list[idx]
            if cpld_list[idx] in ["fan_cpld", "base_cpld"] and not self.upload_file_bmc(fw_path):
                self.__update_fw_upgrade_logger(
                    "cpld_refresh", "fail, message=Unable to upload refresh image to BMC")
                return False

        json_data = dict()
        json_data["Paths"] = fw_path_list
        json_data["Names"] = refresh_list
        r = requests.post(self.fw_refresh_url, json=json_data)
        if r.status_code != 200 or r.json().get('status') != 'OK':
            self.__update_fw_upgrade_logger(
                "cpld_refreshfw", "fail, message={}".format(r.json().get('messages')))
            return False

        self.__update_fw_upgrade_logger("fw_refresh", "done")

        return True

    def get_running_bmc(self):
        """
            Get booting flash of running BMC.
            @return a string, "master" or "slave"
        """
        running_bmc = "master"
        running_bmc_key = "Flash"
        bmc_info_req = requests.get(self.bmc_info_url, timeout=self.api_time_out)
        if bmc_info_req.status_code == 200:
            bmc_info_json = bmc_info_req.json()
            bmc_info = bmc_info_json.get('data')
            running_bmc = bmc_info.get(running_bmc_key)
        return str(running_bmc).lower()

    def set_bmc_boot_flash(self, flash):
        """
            Set booting flash of BMC
            @param flash should be "master" or "slave"
        """
        if flash.lower() not in ["master", "slave"]:
            return False
        json_data = dict()
        json_data["Flash"] = flash
        r = requests.post(self.bmc_next_boot, json=json_data)
        if r.status_code != 200:
            return False
        return True

    def reboot_bmc(self):
        """
            Reboot BMC
        """
        try:
            r = requests.post(self.bmc_reboot_url)
            if r.status_code != 200:
                return False
        except Exception as e:
            if "Connection aborted." in e.message[0]:
                return True
            return False
        return True

    def get_current_bios(self):
        """
            # Get booting bios image of current running host OS
            # @return a string, "master" or "slave"
        """
        bios_boot_info = requests.get(
            self.bios_boot_info, timeout=self.api_time_out)
        if bios_boot_info.status_code == 200:
            bios_boot_info_json = bios_boot_info.json()
            bios_boot_info_data = bios_boot_info_json.get('data')
            bios_boot = bios_boot_info_data.get("Flash")
        return str(bios_boot)

    def get_bios_next_boot(self):
        """
            # Get booting bios image of next booting host OS
            # @return a string, "master" or "slave"
        """
        bios_next_boot = "master"
        bios_next_boot_info = requests.get(
            self.bios_next_boot, timeout=self.api_time_out)
        if bios_next_boot_info.status_code == 200:
            bios_next_boot_info_json = bios_next_boot_info.json()
            bios_next_boot_info_data = bios_next_boot_info_json.get('data')
            bios_next_boot = bios_next_boot_info_data.get("Flash")
        return str(bios_next_boot)

    def set_bios_next_boot(self, flash):
        """
            # Set booting bios image of next booting host OS
            # @return a string, "master" or "slave"
        """
        if str(flash).lower() not in ['master', 'slave']:
            return False

        json_data = dict()
        json_data["Flash"] = str(flash).lower()
        r = requests.post(self.bios_next_boot, json=json_data)
        if r.status_code != 200:
            return False
        return True
