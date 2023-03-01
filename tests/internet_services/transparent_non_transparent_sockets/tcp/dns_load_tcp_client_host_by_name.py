# responsible: maciej.gorny@globallogic.com
# location: Wroclaw
# TC0107298.001

import unicorn
from core.basetest import BaseTest
from dstl.internet_service.execution.internet_service_execution import InternetServiceExecution
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile


class Test(BaseTest):
    """ Checking that DNS can correctly discover Server address during stress TCP and HostbyName test
    Checking reported issue SRV03-2336 """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, 'on')
        test.echo_server = EchoServer('IPv4', 'TCP', test_duration=15)

    def run(test):
        test.log.info("Executing script for test case: 'TC0107298.001 DnsLoadTCPClientHostByName'")
        iterations = 3000
        data_packet_size = 1000

        test.log.step("1) Depends on Module \r\n"
                      "- define pdp context/nv bearer using CGDCONT command and activate it using SICA command \r\n"
                      "- define Connection Profile using SICS command")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step("2) Define Non-transparent TCP Client profile using FQDN address (connection to echo server)")
        fqdn_server_address = test.echo_server.dstl_get_server_FQDN()
        cid = connection_setup.dstl_get_used_cid()
        test.socket = SocketProfile(test.dut, "6", cid,  protocol="tcp", alphabet='1', host=fqdn_server_address,
                                    port=test.echo_server.dstl_get_server_port())
        test.socket.dstl_generate_address()
        test.expect(test.socket.dstl_get_service().dstl_load_profile())

        for iteration in range(1, iterations+1):
            test.log.step("3)  Open TCP Client and wait for SISW URC"
                          "\nIteration: {} of {}".format(iteration, iterations))
            test.expect(test.socket.dstl_get_service().dstl_open_service_profile())
            test.expect(test.socket.dstl_get_urc().dstl_is_sisw_urc_appeared('1'))

            test.log.step("4) Send 1000 bytes and read for echo data "
                          "\r\n Iteration: {} of {}".format(iteration, iterations))
            test.expect(test.socket.dstl_get_service().dstl_send_sisw_command_and_data(data_packet_size))
            test.expect(test.socket.dstl_get_urc().dstl_is_sisr_urc_appeared('1'))
            test.expect(test.socket.dstl_get_service().dstl_read_data(data_packet_size))

            test.log.step("5) Check service state and Tx/Rx counters using SISO command"
                          "\nIteration: {} of {}".format(iteration, iterations))
            test.expect(test.socket.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
            test.expect(test.socket.dstl_get_parser().dstl_get_service_data_counter('tx') == data_packet_size)
            test.expect(test.socket.dstl_get_parser().dstl_get_service_data_counter('rx') == data_packet_size)

            test.log.step("6) Close TCP Client"
                          "\nIteration: {} of {}".format(iteration, iterations))
            test.expect(test.socket.dstl_get_service().dstl_close_service_profile())

            test.log.step("7) Send HostByName request to FQDN website using SISX command"
                          "\nIteration: {} of {}".format(iteration, iterations))
            ping_execution = InternetServiceExecution(test.dut, cid)
            test.expect(ping_execution.dstl_execute_host_by_name(fqdn_server_address))

            test.log.step("8) Repeat steps 3) to 7) {} times"
                          "\nAlready done {} iterations".format(iterations, iteration))
            test.sleep(3)

    def cleanup(test):
        try:
            if not test.echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")
        try:
            test.expect(test.socket.dstl_get_service().dstl_close_service_profile())
            test.expect(test.socket.dstl_get_service().dstl_reset_service_profile())
        except AttributeError:
            test.log.error("Socket object was not created.")


if "__main__" == __name__:
    unicorn.main()
