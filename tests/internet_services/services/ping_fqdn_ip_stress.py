# responsible: grzegorz.dziublinski@globallogic.com
# location: Wroclaw
# TC0093656.001

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
    """ TC intention: Stress test involves ping host as FQDN with IPv4 for 4 hours. """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.ip_server = EchoServer("IPv4", "TCP")
        test.requests_number = 30
        test.timelimit = 10000
        test.execution_time_in_seconds = 14400

    def run(test):
        test.log.step("1. Enter PIN and attach module to the network.")
        test.expect(dstl_register_to_network(test.dut))

        test.log.step("2. Depends on product:\r\n- Set Connection Profile (GPRS)\r\n- Define PDP Context ")
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_define_pdp_context())

        test.log.step("3. Depends on product - Activate PDP Context.")
        test.expect(test.connection_setup.dstl_activate_internet_connection())
        test.cid = test.connection_setup.dstl_get_used_cid()

        test.log.step("4. Start ping host as FQDN for 4 hours (for example: AT^SISX=\"ping\",<conProfileId>,"
                      "<address>,30,10000 in loop).")
        ip_server_address = test.ip_server.dstl_get_server_FQDN()
        ping_execution = InternetServiceExecution(test.dut.at1, test.cid)
        end_time = time() + test.execution_time_in_seconds
        expected_statistic_row = "SISX: \"Ping\",2,{},{},(2[8-9]|30)".format(test.cid, test.requests_number)
        while time() < end_time:
            test.log.info("Remaining time :{}".format(strftime("%H:%M:%S", gmtime(end_time - time()))))
            test.expect(ping_execution.dstl_execute_ping(ip_server_address, request=test.requests_number,
                                                         timelimit=test.timelimit))
            test.expect(re.search(expected_statistic_row, test.dut.at1.last_response),
                        msg="Incorrect packet statistic row. Some ICMP Echo packets may have been lost!")
            returned_ip_address = test.dut.at1.last_response.split("^SISX: \"Ping\",1,{},\""
                                                                   .format(test.cid))[1].split("\"")[0]
            test.expect(ping_execution._check_ip_address(returned_ip_address, 4))
        else:
            test.log.info("TC0093656.001 - PingFqdnIpStress execution time has expired.")

    def cleanup(test):
        try:
            test.ip_server.dstl_server_close_port()
        except AttributeError:
            test.log.error("Server object was not created.")


if "__main__" == __name__:
    unicorn.main()
