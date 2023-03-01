#responsible: damian.latacz@globallogic.com
#location: Wroclaw
#TC0094540.001

import unicorn
import re

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.execution.internet_service_execution import InternetServiceExecution
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
    TC intention: This procedure provides the possibility of basic tests for the test and write command of At^SISX
    for parameter <service>="Ntp".
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        default_ntp_server = "ntp1.pl"
        try:
            if test.ntp_server_address:
                test.log.info("Detected ntp_server_address parameter will be used: {}".format(test.ntp_server_address))
                test.ntp_server = test.ntp_server_address
        except AttributeError:
                test.log.info("ntp_server_address was not detected, therefore the default NTP server will be used: {}"
                              .format(default_ntp_server))
                test.ntp_server = default_ntp_server

    def run(test):
        test.log.step("1. Execute AT^SISX command with Ntp service. In address field use NTP server (e.g. ntp1.pl).")
        service_execution = InternetServiceExecution(test.dut, test.connection_setup.dstl_get_used_cid())
        returned_time = service_execution.dstl_execute_ntp(test.ntp_server)
        test.expect(re.search("\\d{2,4}-\\d{2}-\\d{2}\\D\\d{2}:\\d{2}:\\d{2} UTC", returned_time))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
