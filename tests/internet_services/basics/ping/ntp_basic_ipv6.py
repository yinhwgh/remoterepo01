#responsible: tomasz.brzyk@globallogic.com
#location: Wroclaw
#TC0095166.001

import re
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.execution.internet_service_execution import InternetServiceExecution
from dstl.network_service.register_to_network import dstl_enter_pin

class Test(BaseTest):
    """
    Intention:
    Check functionality of internet information service: Ntp with IPv6 server

    Description:
    1. Execute AT^SISX command with Ntp service. In address field use NTP IPv6 server (e.g. 2001:67c:24c:1::20).
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        test.connection_setup = dstl_get_connection_setup_object(test.dut, ip_version="IPv6")
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        default_ntp_server_ipv6_address = "2001:67c:24c:1::20"

        try:
            if test.ntp_server_ipv6_address:
                test.log.info("Detected ntp_server_address parameter: {}".format(test.ntp_server_ipv6_address))
                test.ntp_server_ipv6 = test.ntp_server_ipv6_address
        except AttributeError:
                test.log.info("ntp_server_address was not detected, therefore the default NTP server will be used: {}"
                              .format(default_ntp_server_ipv6_address))
                test.ntp_server_ipv6 = default_ntp_server_ipv6_address

    def run(test):
        test.log.info("TC0095166.001 - NtpBasicIPv6")
        test.log.step("1. Execute AT^SISX command with Ntp service. In address field use NTP IPv6 server "
                      "(e.g. 2001:67c:24c:1::20).")
        service_execution = InternetServiceExecution(test.dut, test.connection_setup.dstl_get_used_cid())
        returned_time = service_execution.dstl_execute_ntp(test.ntp_server_ipv6)
        test.expect(re.search("\\d{2,4}-\\d{2}-\\d{2}\\D\\d{2}:\\d{2}:\\d{2} UTC", returned_time))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()