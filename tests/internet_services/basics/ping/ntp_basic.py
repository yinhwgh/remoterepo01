# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0094242.001

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
    Check functionality of internet information service: Ntp with IPv4 server

    Description:
    1. Execute AT^SISX command with Ntp service. In address field use NTP IPv4 server (e.g. 91.212.242.20).
    """

    def setup(test):
        test.require_parameter('ntp_server_ipv4_address', default='91.212.242.20')
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        ''' see test.require_ above!
        default_ntp_server_ipv4_address = "91.212.242.20"
        try:
            if test.ntp_server_ipv4_address:
                test.log.info(f"Detected ntp_server_address parameter will be used: {test.ntp_server_ipv4_address}")
                test.ntp_server_ipv4 = test.ntp_server_ipv4_address
        except AttributeError:
                test.log.info("ntp_server_address was not detected, therefore the default NTP server will be used: {}"
                              .format(default_ntp_server_ipv4_address))
                test.ntp_server_ipv4 = default_ntp_server_ipv4_address
        '''
        pass

    def run(test):
        test.log.info("TC0094242.001 - NtpBasic")
        test.log.step("1. Execute AT^SISX command with Ntp service. "
                      "In address field use NTP IPv4 server (e.g. 91.212.242.20).")
        print(test.ntp_server_ipv4_address)
        service_execution = InternetServiceExecution(test.dut, test.connection_setup.dstl_get_used_cid())
        returned_time = service_execution.dstl_execute_ntp(test.ntp_server_ipv4_address)
        test.expect(re.search('\"\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2} UTC\",\"[0123]\",\"\\d{1,2}\"',
                              returned_time))
        print(" ")
        pass

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
