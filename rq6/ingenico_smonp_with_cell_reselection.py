# responsible hongwei.yin@thalesgroup.com
#location: Dalian
#TC0108064.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.network_service import check_cell_monitor_parameters

class Test(BaseTest):
    """
     TC0108064.001-Ingenico_Smonp_With_Cell_Reselection
    """
    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        test.log.step("1. Register module to LTE network.")
        test.expect(test.dut.dstl_register_to_lte(), critical=True)
        test.log.step("2. Monitoring Neighbour Cells.")
        test.expect(test.dut.at1.send_and_verify("AT^SMONP", "4G:.*\d+,-?\d+,-?\d+,\d+,\d+,"))

    def cleanup(test):
        try:
            test.dut.at1.send_and_verify("AT+COPS=2")
            test.dut.at1.send_and_verify("AT+COPS=0")
        except Exception:
            test.expect(test.dut.dstl_restart())


if "__main__" == __name__:
    unicorn.main()