# responsible: maciej.gorny@globallogic.com
# location: Wroclaw
# TC0094865.001, TC0094865.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.configuration.scfg_tcp_ot \
                                                import dstl_set_scfg_tcp_ot, dstl_get_scfg_tcp_ot
from dstl.internet_service.configuration.scfg_tcp_mr import dstl_set_scfg_tcp_mr
from dstl.internet_service.connection_setup_service.connection_setup_service \
                                                        import dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState
from time import time
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.profile_storage.dstl_get_siss_read_response import \
    dstl_get_siss_read_response
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """Verify the overall timeout parameter for the TCP service."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

    def run(test):
        test.log.h2("Executing script for test case: 'TC0094865.001/002 TcpOverallTimeout'")
        overall_timeout_scfg = 45
        overall_timeout_siss = 180
        overall_timeout = overall_timeout_scfg

        test.log.step("1. Configure global value for tcpMr to maximum value, tcp/OT to 45 sec")
        test.expect(dstl_set_scfg_tcp_ot(test.dut, overall_timeout_scfg))
        test.expect(dstl_set_scfg_tcp_mr(test.dut, 30))

        test.log.step("2. Activate Internet connection.")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile(),
                    critical=True)

        test.log.step("3. Define a TCP client socket service profile.")
        test.server = EchoServer("IPv4", "TCP", extended=True)
        socket = SocketProfile(test.dut, "1", connection_setup.dstl_get_used_cid(),
                               protocol="tcp", host=test.server.dstl_get_server_ip_address(),
                               port=test.server.dstl_get_server_port())
        socket.dstl_generate_address()
        test.expect(socket.dstl_get_service().dstl_load_profile())

        test.log.step("4. Open the TCP service.")
        test.expect(socket.dstl_get_service().dstl_open_service_profile())

        test.log.step("5. Send some data.")
        test.expect(socket.dstl_get_service().dstl_send_sisw_command_and_data(200))
        test.sleep(4)

        test.log.step("6. Read all data.")
        test.expect(socket.dstl_get_service().dstl_read_data(200))

        test.log.step("7. Activate firewall on server side")
        test.expect(test.server.dstl_server_block_incoming_traffic())
        test.sleep(4)
        start_time = time()

        test.log.step("8. Call send command at^sisw in a loop .")
        for iteration in range(4):
            test.expect(socket.dstl_get_service().dstl_send_sisw_command_and_data(200,
                                                                            skip_data_check=True))
            test.sleep(7)

        test.log.step("9. Wait for 'Connection timed out' URC.")
        if test.expect(socket.dstl_get_urc().dstl_is_sis_urc_appeared("0", "20",
                                "\"Connection timed out\"", 80), msg="Expected URC not appeared."):
            urc_end_time = int(time() - start_time)
            test.log.info("URC appeared after {} seconds. Expected value: {} seconds."
                                                    .format(urc_end_time, overall_timeout))
            test.expect(urc_end_time - overall_timeout < overall_timeout/2,
                                                msg="URC appeared, but not in expected time.")

        test.log.step("10. Check service state.")
        test.expect(socket.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(socket.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value)

        test.log.step("11. Close profile.")
        test.expect(socket.dstl_get_service().dstl_close_service_profile())

        test.log.step("12. Deactivate firewall on server side")
        test.expect(test.server.dstl_server_accept_incoming_traffic())

        test.log.step("13. Configure the service based value for tcpOt to 180 sec.")
        overall_timeout = overall_timeout_siss
        socket.dstl_set_tcp_ot(overall_timeout)
        test.expect(socket.dstl_get_service().dstl_write_tcpot())

        test.log.step("14. Repeat steps 4. - 12.")
        test.log.step("14.4. Open the TCP service")
        test.expect(socket.dstl_get_service().dstl_open_service_profile())

        test.log.step("14.5. Send some data.")
        test.expect(socket.dstl_get_service().dstl_send_sisw_command_and_data(200))
        test.sleep(4)

        test.log.step("14.6. Read all data.")
        test.expect(socket.dstl_get_service().dstl_read_data(200))

        test.log.step("14.7. Activate firewall on server side")
        test.expect(test.server.dstl_server_block_incoming_traffic())
        test.sleep(4)
        start_time = time()

        test.log.step("14.8. Call send command at^sisw in a loop .")
        for iteration in range(12):
            test.expect(socket.dstl_get_service().dstl_send_sisw_command_and_data(200,
                                                                            skip_data_check=True))
            test.sleep(7)

        test.log.step("14.9. Wait for 'Connection timed out' URC.")
        if test.expect(socket.dstl_get_urc().dstl_is_sis_urc_appeared("0", "20",
                                                                      "\"Connection timed out\"",
                                                                      240),
                       msg="Expected URC not appeared."):
            urc_end_time = int(time() - start_time)
            test.log.info("URC appeared after {} seconds. Expected value: {} seconds."
                          .format(urc_end_time, overall_timeout))
            test.expect(urc_end_time - overall_timeout < overall_timeout / 2,
                        msg="URC appeared, but not in expected time.")

        test.log.step("14.10. Check service state.")
        test.expect(socket.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(socket.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value)

        test.log.step("14.11. Close profile.")
        test.expect(socket.dstl_get_service().dstl_close_service_profile())

        test.log.step("14.12. Deactivate firewall on server side")
        test.expect(test.server.dstl_server_accept_incoming_traffic())

        test.log.step("15. Try to set some illegal global values for tcp/OT "
                      "and check the configured values.")
        test.expect(dstl_set_scfg_tcp_ot(test.dut, -2, expected=".*CME ERROR.*"))
        test.expect(dstl_set_scfg_tcp_ot(test.dut, 6001, expected=".*CME ERROR.*"))
        test.expect(dstl_set_scfg_tcp_ot(test.dut, "OT", expected=".*CME ERROR.*"))
        test.expect(int(dstl_get_scfg_tcp_ot(test.dut)) == overall_timeout_scfg)

        test.log.step("16. Try to set some illegal service values for tcp/OT "
                      "and check the configured values.")
        socket.dstl_set_tcp_ot("XYZ2")
        test.expect(not socket.dstl_get_service().dstl_write_tcpot())
        socket.dstl_set_tcp_ot("6002")
        test.expect(not socket.dstl_get_service().dstl_write_tcpot())
        socket.dstl_set_tcp_ot("-3")
        test.expect(not socket.dstl_get_service().dstl_write_tcpot())
        dstl_get_siss_read_response(test.dut)
        test.expect('"tcpOT","180"' in test.dut.at1.last_response)

    def cleanup(test):
        test.expect(dstl_set_scfg_tcp_ot(test.dut, 6000))
        test.expect(dstl_set_scfg_tcp_mr(test.dut, 10))
        try:
            if not test.server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            test.server.dstl_server_accept_incoming_traffic()
        except AttributeError:
            test.log.error("Object was not created.")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)


if "__main__" == __name__:
    unicorn.main()