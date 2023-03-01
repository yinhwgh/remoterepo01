#responsible: damian.latacz@globallogic.com
#location: Wroclaw
#TC0094343.001

import unicorn

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
    for parameter <service>="HostByName".
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.ip_server = EchoServer("IPV4", "TCP")

    def run(test):
        test.log.step("1. Execute AT^SISX command for parameter <service>= HostByName.")
        service_execution = InternetServiceExecution(test.dut, test.connection_setup.dstl_get_used_cid())
        returned_ip_addresses = service_execution.dstl_execute_host_by_name(test.ip_server.dstl_get_server_FQDN())
        test.expect(test.ip_server.dstl_get_server_ip_address() in returned_ip_addresses)

    def cleanup(test):
        try:
            if not test.ip_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")


if "__main__" == __name__:
    unicorn.main()
