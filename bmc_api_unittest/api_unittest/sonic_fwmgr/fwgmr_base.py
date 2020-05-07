try:
    import abc
except ImportError as e:
    raise ImportError (str(e) + " - required module not found")

class FwMgrUtilBase(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_bmc_version(self):
        """Get BMC version from SONiC
        :returns: version string

        """
        return '0.0.0'

    @abc.abstractmethod
    def get_cpld_version(self):
        """Get CPLD version from SONiC
        :returns: version string

        """
        return '0.0.0'

    @abc.abstractmethod
    def get_bios_version(self):
        """Get BIOS version from SONiC
        :returns: version string

        """
        return '0.0.0'

    @abc.abstractmethod
    def get_onie_version(self):
        """Get ONiE version from SONiC
        :returns: version string

        """
        return '0.0.0'

    @abc.abstractmethod
    def get_pcie_version(self):
        """Get PCiE version from SONiC
        :returns: version string

        """
        return '0.0.0'

    @abc.abstractmethod
    def get_fpga_version(self):
        """Get FPGA version from SONiC
        :returns: TODO

        """
        return '0.0.0'
