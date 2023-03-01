#responsible maciej.gorny@globallogic.com
#location Wroclaw
#corresponding Test Case TC 0094239.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.execution.internet_service_execution import InternetServiceExecution
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect


class Test(BaseTest):
    """
        Short description: 	Check functionality of internet information service: HostByName

        Detailed description:
        1. Execute AT^SISX command with HostByName service. In address field type fully
        qualified domain name (e.g. www.google.pl).
        2. Execute AT^SISX command with HostByName service. Use IPv4 only parameter
         (e.g. AT^SISX="HostByName",1,"www.google.pl",4).
        3. Execute AT^SISX command with HostByName service. Use IPv6 only parameter
         (e.g. AT^SISX="HostByName",1,"www.google.pl",6).
       """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)

    def run(test):

        test.log.h2("Executing script for test case: TC0094239.001 HostByNameBasic")
        test.echo_server = EchoServer("IPv4", "TCP",  test_duration=1)

        test.log.info("Preconditions - Activation of PDP context ")
        connection_setup_object = dstl_get_connection_setup_object(test.dut, ip_version="IPV4")
        test.expect(connection_setup_object.dstl_load_and_activate_internet_connection_profile())
        ping_execution = InternetServiceExecution(test.dut, connection_setup_object.dstl_get_used_cid())

        test.log.step("1). Execute AT^SISX command with HostByName service. In address field type fully "
                      "qualified domain name (e.g. www.google.pl).")
        test.expect(ping_execution.dstl_execute_host_by_name(test.echo_server.dstl_get_server_FQDN()))

        test.log.step("2). Execute AT^SISX command with HostByName service. Use IPv4 only parameter "
                      "(e.g. AT^SISX=HostByName,1,www.google.pl,4)")
        test.expect(ping_execution.dstl_execute_host_by_name(test.echo_server.dstl_get_server_FQDN(), 4))

        test.log.step("3). Execute AT^SISX command with HostByName service. Use IPv6 only parameter "
                      "(e.g. AT^SISX=HostByName,1,www.google.pl,6).")
        test.expect(ping_execution.dstl_execute_host_by_name(test.echo_server.dstl_get_server_FQDN(), 6))

    def cleanup(test):
        try:
            if not test.echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Object was not created.")

if "__main__" == __name__:
    unicorn.main()
