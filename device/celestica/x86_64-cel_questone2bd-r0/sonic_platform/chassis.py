#!/usr/bin/env python

#############################################################################
# Celestica
#
# Module contains an implementation of SONiC Platform Base API and
# provides the Chassis information which are available in the platform
#
#############################################################################

try:
    import json
    import os
    import re
    import sys
    import subprocess
    import time
    from sonic_platform_base.chassis_base import ChassisBase
    from helper import APIHelper
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

NUM_FAN_TRAY = 4
NUM_FAN = 2
NUM_PSU = 2
NUM_THERMAL = 11
NUM_SFP = 56
NUM_COMPONENT = 7

SFP_PORT_START = 1
SFP_PORT_END = 48
QSFP_PORT_START = 49
QSFP_PORT_END = 56

REBOOT_CAUSE_REG = "0xA106"
TLV_EEPROM_I2C_BUS = 0
TLV_EEPROM_I2C_ADDR = 56
BASE_CPLD_PLATFORM = "questone2bd.cpldb"
BASE_GETREG_PATH = "/sys/devices/platform/{}/getreg".format(BASE_CPLD_PLATFORM)

SWITCH_BRD_PLATFORM = "questone2bd.switchboard"
PORT_INFO_PATH = "/sys/devices/platform/{}/SFF".format(SWITCH_BRD_PLATFORM)
PATH_INT_SYSFS = "{0}/{port_name}/{type_prefix}_isr_flags"
PATH_INTMASK_SYSFS = "{0}/{port_name}/{type_prefix}_isr_mask"
PATH_PRS_SYSFS = "{0}/{port_name}/{prs_file_name}"

class Chassis(ChassisBase):
    """Platform-specific Chassis class"""

    def __init__(self):
        ChassisBase.__init__(self)
        self._api_helper = APIHelper()
        self.sfp_module_initialized = False
        self.__initialize_eeprom()
        self.POLL_INTERVAL = 1

        if not self._api_helper.is_host():
            self.__initialize_fan()
            self.__initialize_psu()
            self.__initialize_thermals()
            self.__initialize_interrupts()
        else:
            self.__initialize_components()

    def __initialize_sfp(self):
        from sonic_platform.sfp import Sfp
        for index in range(0, NUM_SFP):
            sfp = Sfp(index)
            self._sfp_list.append(sfp)
        self.sfp_module_initialized = True

    def __initialize_psu(self):
        from sonic_platform.psu import Psu
        for index in range(0, NUM_PSU):
            psu = Psu(index)
            self._psu_list.append(psu)

    def __initialize_fan(self):
        from sonic_platform.fan import Fan
        for fant_index in range(0, NUM_FAN_TRAY):
            for fan_index in range(0, NUM_FAN):
                fan = Fan(fant_index, fan_index)
                self._fan_list.append(fan)

    def __initialize_thermals(self):
        from sonic_platform.thermal import Thermal
        for index in range(0, NUM_THERMAL):
            thermal = Thermal(index)
            self._thermal_list.append(thermal)

    def __initialize_eeprom(self):
        from sonic_platform.eeprom import Eeprom
        self._eeprom = Eeprom(TLV_EEPROM_I2C_BUS, TLV_EEPROM_I2C_ADDR)

    def __initialize_components(self):
        from sonic_platform.component import Component
        for index in range(0, NUM_COMPONENT):
            component = Component(index)
            self._component_list.append(component)

    def __initialize_interrupts(self):
        # Initial Interrupt MASK for QSFP, SFP
        sfp_info_obj = {}

        present_en = 0x10
        Rxlos_IntL_en = 0x01
        event_mask = present_en

        for index in range(NUM_SFP):
            port_num = index + 1
            if port_num in range(SFP_PORT_START, SFP_PORT_END+1):
                port_name = "SFP{}".format(str(port_num - SFP_PORT_START + 1))
                port_type = "sfp"
                sysfs_prs_file = "{}_modabs".format(port_type)
            elif port_num in range(QSFP_PORT_START, QSFP_PORT_END+1):
                port_name = "QSFP{}".format(str(port_num - QSFP_PORT_START + 1))
                port_type = "qsfp"
                sysfs_prs_file = "{}_modprs".format(port_type)

            sfp_info_obj[index] = {}
            sfp_info_obj[index]['intmask_sysfs'] = PATH_INTMASK_SYSFS.format(
                PORT_INFO_PATH,
                port_name = port_name,
                type_prefix = port_type)

            sfp_info_obj[index]['int_sysfs'] = PATH_INT_SYSFS.format(
                PORT_INFO_PATH,
                port_name = port_name,
                type_prefix = port_type)

            sfp_info_obj[index]['prs_sysfs'] = PATH_PRS_SYSFS.format(
                PORT_INFO_PATH,
                port_name = port_name,
                prs_file_name = sysfs_prs_file)

            self._api_helper.write_file(
                sfp_info_obj[index]["intmask_sysfs"], hex(event_mask))

        self.sfp_info_obj = sfp_info_obj

    def get_base_mac(self):
        """
        Retrieves the base MAC address for the chassis
        Returns:
            A string containing the MAC address in the format
            'XX:XX:XX:XX:XX:XX'
        """
        return self._eeprom.get_mac()

    def get_serial_number(self):
        """
        Retrieves the hardware serial number for the chassis
        Returns:
            A string containing the hardware serial number for this chassis.
        """
        return self._eeprom.get_serial()

    def get_system_eeprom_info(self):
        """
        Retrieves the full content of system EEPROM information for the chassis
        Returns:
            A dictionary where keys are the type code defined in
            OCP ONIE TlvInfo EEPROM format and values are their corresponding
            values.
        """
        return self._eeprom.get_eeprom()

    def get_reboot_cause(self):
        """
        Retrieves the cause of the previous reboot
        Returns:
            A tuple (string, string) where the first element is a string
            containing the cause of the previous reboot. This string must be
            one of the predefined strings in this class. If the first string
            is "REBOOT_CAUSE_HARDWARE_OTHER", the second string can be used
            to pass a description of the reboot cause.
        """
        hx_cause = self._api_helper.get_register_value(
            BASE_GETREG_PATH, REBOOT_CAUSE_REG)

        return {
            "0x00": (self.REBOOT_CAUSE_HARDWARE_OTHER, 'Unknown'),
            "0x11": (self.REBOOT_CAUSE_POWER_LOSS, 'The last reset is Power on reset'),
            "0x22": (self.REBOOT_CAUSE_HARDWARE_OTHER, 'The last reset is soft-set CPU warm reset'),
            "0x33": (self.REBOOT_CAUSE_HARDWARE_OTHER, 'The last reset is soft-set CPU cold reset'),
            "0x44": (self.REBOOT_CAUSE_HARDWARE_OTHER, 'The last reset is CPU warm reset'),
            "0x55": (self.REBOOT_CAUSE_HARDWARE_OTHER, 'The last reset is CPU cold reset'),
            "0x66": (self.REBOOT_CAUSE_WATCHDOG, 'The last reset is watchdog reset'),
            "0x77": (self.REBOOT_CAUSE_HARDWARE_OTHER, 'The last reset is power cycle reset'),
        }.get(hx_cause.lower(), (self.REBOOT_CAUSE_HARDWARE_OTHER, 'Unknown'))

    ##############################################################
    ######################## SFP methods #########################
    ##############################################################

    def get_num_sfps(self):
        """
        Retrieves the number of sfps available on this chassis
        Returns:
            An integer, the number of sfps available on this chassis
        """
        if not self.sfp_module_initialized:
            self.__initialize_sfp()

        return len(self._sfp_list)

    def get_all_sfps(self):
        """
        Retrieves all sfps available on this chassis
        Returns:
            A list of objects derived from SfpBase representing all sfps
            available on this chassis
        """
        if not self.sfp_module_initialized:
            self.__initialize_sfp()

        return self._sfp_list

    def get_sfp(self, index):
        """
        Retrieves sfp represented by (1-based) index <index>
        Args:
            index: An integer, the index (1-based) of the sfp to retrieve.
            The index should be the sequence of a physical port in a chassis,
            starting from 1.
            For example, 1 for Ethernet0, 2 for Ethernet4 and so on.
        Returns:
            An object dervied from SfpBase representing the specified sfp
        """
        sfp = None
        if not self.sfp_module_initialized:
            self.__initialize_sfp()

        try:
            # The index will start from 1
            sfp = self._sfp_list[index-1]
        except IndexError:
            sys.stderr.write("SFP index {} out of range (1-{})\n".format(
                             index, len(self._sfp_list)))
        return sfp

    ##############################################################
    ####################### Other methods ########################
    ##############################################################

    def get_watchdog(self):
        """
        Retreives hardware watchdog device on this chassis
        Returns:
            An object derived from WatchdogBase representing the hardware
            watchdog device
        """
        if self._watchdog is None:
            from sonic_platform.watchdog import Watchdog
            self._watchdog = Watchdog()

        return self._watchdog

    ##############################################################
    ###################### Device methods ########################
    ##############################################################

    def get_name(self):
        """
        Retrieves the name of the device
            Returns:
            string: The name of the device
        """
        return self._api_helper.hwsku

    def get_presence(self):
        """
        Retrieves the presence of the PSU
        Returns:
            bool: True if PSU is present, False if not
        """
        return True

    def get_model(self):
        """
        Retrieves the model number (or part number) of the device
        Returns:
            string: Model/part number of device
        """
        return self._eeprom.get_pn()

    def get_serial(self):
        """
        Retrieves the serial number of the device
        Returns:
            string: Serial number of device
        """
        return self.get_serial_number()

    def get_status(self):
        """
        Retrieves the operational status of the device
        Returns:
            A boolean value, True if device is operating properly, False if not
        """
        return True

    ##############################################################
    ###################### Event methods #########################
    ##############################################################

    def __is_port_device_present(self, port_idx):
        prs_path = self.sfp_info_obj[port_idx]["prs_sysfs"]
        is_present = 1 - int(self._api_helper.read_txt_file(prs_path))
        return is_present

    def __update_port_event_object(self, interrup_devices):
        port_dict = {}
        event_obj = {'sfp':port_dict}
        for port_idx in interrup_devices:
            device_id = str(port_idx + 1)
            port_dict[device_id] = str(self.__is_port_device_present(port_idx))

        if len(port_dict):
            event_obj['sfp'] = port_dict

        return event_obj

    def __check_all_port_interrupt_event(self):
        interrupt_devices = {}
        for i in range(NUM_SFP):
            int_sysfs = self.sfp_info_obj[i]["int_sysfs"]
            interrupt_flags = self._api_helper.read_txt_file(int_sysfs)
            if interrupt_flags != '0x00':
                interrupt_devices[i] = 1
        return interrupt_devices

    def get_change_event(self, timeout=0):
        """
        Returns a nested dictionary containing all devices which have
        experienced a change at chassis level
        Args:
            timeout: Timeout in milliseconds (optional). If timeout == 0,
                this method will block until a change is detected.
        Returns:
            (bool, dict):
                - True if call successful, False if not;
                - A nested dictionary where key is a device type,
                  value is a dictionary with key:value pairs in the
                  format of {'device_id':'device_event'},
                  where device_id is the device ID for this device and
                        device_event,
                             status='1' represents device inserted,
                             status='0' represents device removed.
                  Ex. {'fan':{'0':'0', '2':'1'}, 'sfp':{'11':'0'}}
                      indicates that fan 0 has been removed, fan 2
                      has been inserted and sfp 11 has been removed.
        """
        if timeout == 0:
            timer = self.POLL_INTERVAL
            while True:
                interrupt_devices = self.__check_all_port_interrupt_event()
                if len(interrupt_devices):
                    break
                else:
                    time.sleep(timer)
            events_dict = self.__update_port_event_object(interrupt_devices)
            return (True, events_dict)
        else:
            timeout = timeout / float(1000)
            timer = min(timeout, self.POLL_INTERVAL)

            while True:
                start_time = time.time()
                interrupt_devices = self.__check_all_port_interrupt_event()
                if len(interrupt_devices):
                    break

                if timeout <= 0:
                    break
                else:
                    time.sleep(timer)
                elasped_time = time.time() - start_time
                timeout = round(timeout - elasped_time, 3)
            events_dict = self.__update_port_event_object(interrupt_devices)
            return (True, events_dict)
