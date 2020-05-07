#!/usr/bin/python
# -*- coding: UTF-8 -*-
# unittest configuration
import os

TEST_DIR = '/home/admin/api_unittest'
TEST_DIR1 = '/usr/lib/python2.7/dist-packages/api_unittest'
TEST_DIR = TEST_DIR if os.path.exists(TEST_DIR) else TEST_DIR1
SKIP_REBOOT_CPU = True

FAN_KEY = ['AirFlow', 'HighThd', 'LowThd', 'PN', 'Present', 'Running', 'SN', 'Speed', 'Status']
#PSU_KEY = ['AirFlow', 'InputStatus', 'InputType', 'OutputStatus', 'PN', 'PowerStatus', 'Present', 'SN']
PSU_KEY = ['AirFlow', 'HighThd', 'InputStatus', 'InputType', 'LowThd', 'OutputStatus', 'PN', 'Present', 'SN', 'Speed']
SENSOR_KEY = ['HighThd', 'LowThd', 'Type', 'Value']

BMC_IMAGE_PATH = '/home/admin/img/flash-as58xx-cl'
BIOS_IMAGE_PATH = '/home/admin/img/bios.bin'
FPGA_IMAGE_PATH = '/home/admin/img/fpga.bin'
CPLD_IMAGE_PATH = '/home/admin/img'

CPLDTEST = {
    "as13-32h" : { "program" : {"CPU_BOARD_CPLD": "as13-32h_cpld_1_cpu_pwr.vme",
                                "CPU_MODULE_CPLD": "as13-32h_cpld_2_cpu_pwr.vme",
                                "MAC_BOARD_CPLD_1": "as13-32h_cpld_3_cpu_pwr.vme",
                                "MAC_BOARD_CPLD_2": "as13-32h_cpld_4_cpu_pwr.vme"},

                   "refresh" : {"CPU_BOARD_CPLD": "as13-32h_cpld_1-2_transfr_bmc.vme",
                                "CPU_MODULE_CPLD": "as13-32h_cpld_1-2_transfr_bmc.vme",
                                "MAC_BOARD_CPLD_1": "as13-32h_cpld_3_transfr_bmc.vme",
                                 "MAC_BOARD_CPLD_2": "as13-32h_cpld_4_transfr_bmc.vme"}},

    "as13-48f8h" : { "program": {"CPU_BOARD_CPLD": "as13-48f8h_cpld_1_cpu_pwr.vme",
                                 "CPU_MODULE_CPLD": "as13-48f8h_cpld_2_cpu_pwr.vme",
                                 "MAC_BOARD_CPLD_1": "as13-48f8h_cpld_3_cpu_pwr.vme",
                                 "MAC_BOARD_CPLD_2": "as13-48f8h_cpld_4_cpu_pwr.vme"},

                    "refresh": {"CPU_BOARD_CPLD": "as13-48f8h_cpld_1-2_transfr_bmc.vme",
                                "CPU_MODULE_CPLD": "as13-48f8h_cpld_1-2_transfr_bmc.vme",
                                "MAC_BOARD_CPLD_1": "as13-48f8h_cpld_3_transfr_bmc.vme",
                                "MAC_BOARD_CPLD_2": "as13-48f8h_cpld_4_transfr_bmc.vme"}},

    "as23-128h" : { "program": {"CPU_BOARD_CPLD-FAN": "as23-128h_cpld_1_main_cpu_pwr.vme",
                                "CPU_BOARD_CPLD": "as23-128h_cpld_2_main_cpu_pwr.vme",
                                "CPU_MODULE_CPLD": "as23-128h_cpld_3_main_cpu_pwr.vme",
                                "LC_CPLD1": "as23-128h_cpld_1_sub_cpu_pwr.vme",
                                "LC_CPLD2": "as23-128h_cpld_2_sub_cpu_pwr.vme"},

                    "refresh": {"CPU_BOARD_CPLD-FAN": "as23-128h_cpld_1_transfr_main_bmc.vme",
                                "CPU_BOARD_CPLD": "as23-128h_cpld_2-3_transfr_main_bmc.vme",
                                "CPU_MODULE_CPLD": "as23-128h_cpld_2-3_transfr_main_bmc.vme",
                                "LC_CPLD1": "as23-128h_cpld_1_transfr_sub_bmc.vme",
                                "LC_CPLD2": "as23-128h_cpld_2_transfr_sub_bmc.vme"}},

    "as14-128h" : { "program": {"CPU_BOARD_CPLD-FAN": "as23-128h_cpld_1_main_cpu_pwr.vme",
                                "CPU_BOARD_CPLD": "as23-128h_cpld_2_main_cpu_pwr.vme",
                                "CPU_MODULE_CPLD": "as23-128h_cpld_3_main_cpu_pwr.vme",
                                "LC_CPLD1": "as23-128h_cpld_1_sub_cpu_pwr.vme",
                                "LC_CPLD2": "as23-128h_cpld_2_sub_cpu_pwr.vme"},

                    "refresh": {"CPU_BOARD_CPLD-FAN": "as23-128h_cpld_1_transfr_main_bmc.vme",
                                "CPU_BOARD_CPLD": "as23-128h_cpld_2-3_transfr_main_bmc.vme",
                                "CPU_MODULE_CPLD": "as23-128h_cpld_2-3_transfr_main_bmc.vme",
                                "LC_CPLD1": "as23-128h_cpld_1_transfr_sub_bmc.vme",
                                "LC_CPLD2": "as23-128h_cpld_2_transfr_sub_bmc.vme"}},
    }



CPLDTEST_CLS = {
    "as13-32h" : { "program" : {"FAN_CPLD": "as13-32h_cpld_1_cpu_pwr.vme",
                                "BASE_CPLD": "as13-32h_cpld_2_cpu_pwr.vme",
                                "CPU_CPLD": "as13-32h_cpld_3_cpu_pwr.vme",
                                "SW_CPLD1": "as13-32h_cpld_4_cpu_pwr.vme",
                                "SW_CPLD2": "as13-32h_cpld_5_cpu_pwr.vme"},

                   "refresh" : {"FAN_CPLD": "as13-32h_cpld_1_transfr_bmc.vme",
                                "BASE_CPLD": "as13-32h_cpld_2_transfr_bmc.vme",
                                "CPU_CPLD": "None",
                                "SW_CPLD1": "None",
                                "SW_CPLD2": "None"}},

    "as13-48f8h" : { "program": {"FAN_CPLD": "as13-48f8h_cpld_1_cpu_pwr.vme",
                                "BASE_CPLD": "as13-48f8h_cpld_2_cpu_pwr.vme",
                                "CPU_CPLD": "as13-48f8h_cpld_3_cpu_pwr.vme",
                                "SW_CPLD1": "as13-48f8h_cpld_4_cpu_pwr.vme",
                                "SW_CPLD2": "as13-48f8h_cpld_5_cpu_pwr.vme"},

                    "refresh": {"FAN_CPLD": "as13-48f8h_cpld_1_transfr_bmc.vme",
                                "BASE_CPLD": "as13-48f8h_cpld_2_transfr_bmc.vme",
                                "CPU_CPLD": "None",
                                "SW_CPLD1": "None",
                                "SW_CPLD2": "None"}},

    "as23-128h" : { "program": {"FAN_CPLD": "as23-128h_cpld_1_main_cpu_pwr.vme",
                                "BASE_CPLD": "as23-128h_cpld_2_main_cpu_pwr.vme",
                                "CPU_CPLD": "as23-128h_cpld_3_main_cpu_pwr.vme",
                                "TOP_LC_CPLD": "as23-128h_cpld_1_sub_cpu_pwr.vme",
                                "BOT_LC_CPLD": "as23-128h_cpld_2_sub_cpu_pwr.vme"},

                    "refresh": {"FAN_CPLD": "as23-128h_cpld_1_transfr_main_bmc.vme",
                                "BASE_CPLD": "as23-128h_cpld_2_transfr_main_bmc.vme",
                                "CPU_CPLD": "None",
                                "TOP_LC_CPLD": "None",
                                "BOT_LC_CPLD": "None"}},
}
