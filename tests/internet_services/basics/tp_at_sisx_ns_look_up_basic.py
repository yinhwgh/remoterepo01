#responsible: damian.latacz@globallogic.com
#location: Wroclaw
#TC0094344.001

import unicorn
import re

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.execution.internet_service_execution import InternetServiceExecution
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
    TC intention: This procedure provides the possibility of basic tests for the test and write command of At^SISX
    for parameter <service>="NsLookUp".
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.server_ipv4 = EchoServer("IPV4", "TCP")
        test.server_ipv6 = EchoServer("IPV6", "TCP")
        test.server_fqdn = test.server_ipv4.dstl_get_server_FQDN()
        test.server_address_ipv4 = test.server_ipv4.dstl_get_server_ip_address()
        test.server_address_ipv6 = test.server_ipv6.dstl_get_server_ip_address()

    def run(test):
        test.log.step("1. Execute AT^SISX command with NsLookup service. In address field type fully qualified domain "
                      "name (e.g. www.google.pl).")
        service_execution = InternetServiceExecution(test.dut, test.connection_setup.dstl_get_used_cid())
        response = str(service_execution.dstl_execute_ns_lookup(test.server_fqdn))
        test.expect(test.server_address_ipv4 in response)
        test.expect(test.server_address_ipv6 in response)
        test.expect(re.search("\\['\\d+', '\\d+'\\]", response))

        test.log.step("2. Execute AT^SISX command with NsLookup service. Use IPv4 only parameter (e.g. "
                      "AT^SISX=\"NsLookup\",1,\"www.google.pl\",4).")
        response = str(service_execution.dstl_execute_ns_lookup(test.server_fqdn, request=4))
        test.expect(test.server_address_ipv4 in response)
        test.expect(re.search("\\['\\d+'\\]", response))

        test.log.step("3. Execute AT^SISX command with NsLookup service. Use IPv6 only parameter (e.g. "
                      "AT^SISX=\"NsLookup\",1,\"www.google.pl\",6).")
        response = str(service_execution.dstl_execute_ns_lookup(test.server_fqdn, request=6))
        test.expect(test.server_address_ipv6 in response)
        test.expect(re.search("\\['\\d+'\\]", response))

    def cleanup(test):
        try:
            if not test.server_ipv4.dstl_server_close_port() or not test.server_ipv6.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")


if "__main__" == __name__:
    unicorn.main()
