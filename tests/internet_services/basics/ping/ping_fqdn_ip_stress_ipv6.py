# responsible: maciej.gorny@globallogic.com
# location: Wroclaw
# TC0093657.001/002

import unicorn
import re
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.execution.internet_service_execution import InternetServiceExecution
from dstl.network_service.register_to_network import dstl_register_to_network
from time import gmtime, strftime, time


class Test(BaseTest):
    """
    Stress test involves ping host as FQDN with IPv6 for 4 hours.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.ip_server = EchoServer("IPv6", "TCP", test_duration=4)
        test.REQUESTS_NUMBER = 30
        test.TIMELIMIT = 10000
        test.EXECUTION_TIME_IN_SECONDS = 60 * 60 * 4

    def run(test):
        test.log.info("Starting execution of TC0093657.001/002- PingFqdnIpStress_IPV6.")
        test.log.step("1. Enter PIN and attach module to the network.")
        test.expect(dstl_register_to_network(test.dut))

        test.log.step("2. Depends on product:\r\n- Set Connection Profile (GPRS)\r\n- Define PDP Context ")
        connection_setup = dstl_get_connection_setup_object(test.dut, ip_version="IPv6")
        test.expect(connection_setup.dstl_define_pdp_context())

        test.log.step("3. Depends on product - Activate PDP Context.")
        test.expect(connection_setup.dstl_activate_internet_connection())
        cid = connection_setup.dstl_get_used_cid()

        test.log.step("4. Start ping host as FQDN for 4 hours (for example: AT^SISX=\"ping\",<conProfileId>,"
                      "<address>,30,10000 in loop).")
        fqdn_server_address = test.ip_server.dstl_get_server_FQDN()
        ip_server_address_to_check = test.ip_server.dstl_get_server_ip_address()
        ping_execution = InternetServiceExecution(test.dut, cid)
        end_time = time() + test.EXECUTION_TIME_IN_SECONDS
        expected_statistic_row = "SISX: \"Ping\",2,{},{},(2[5-9]|30)".format(cid, test.REQUESTS_NUMBER)
        while time() < end_time:
            test.log.info("Remaining time of test :{}".format(strftime("%H:%M:%S", gmtime(end_time - time()))))
            test.expect(ping_execution.dstl_execute_ping(fqdn_server_address, request=test.REQUESTS_NUMBER,
                                                         timelimit=test.TIMELIMIT))
            test.expect(ping_execution._check_ip_address(ip_server_address_to_check, 6))
            test.expect(re.search(expected_statistic_row, test.dut.at1.last_response),
                        msg="Incorrect packet statistic row. Some ICMP Echo packets may have been lost!")

        else:
            test.log.info("TC0093657.001/002- PingFqdnIpStress_IPV6 execution time has expired.")

    def cleanup(test):
        try:
            test.ip_server.dstl_server_close_port()
        except AttributeError:
            test.log.error("Server object was not created.")


if "__main__" == __name__:
    unicorn.main()
