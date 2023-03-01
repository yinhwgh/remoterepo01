# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0102385.001, TC0102385.002

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.auxiliary.init import dstl_detect
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.identification.get_imei import dstl_get_imei
from dstl.packet_domain.select_printing_ip_address_format import \
    dstl_select_printing_ip_address_format


class Test(BaseTest):
    """Check packet fragmentation mechanism for IPv6"""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.echo_server = EchoServer("IPv6", "UDP", extended=True)
        test.timeout = 60
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        dstl_select_printing_ip_address_format(test.dut, 1)

    def run(test):
        test.log.step("1. Set UDP client on DUT, use IPv6")
        connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_version="IPv6",
                                                                ip_public=True)
        test.expect(connection_setup_dut.
                    dstl_load_and_activate_internet_connection_profile())
        test.socket_dut = SocketProfile(test.dut, "0", connection_setup_dut.dstl_get_used_cid(),
                                        protocol="UDP", bufsize=1460, etx_char=26,
                                        ip_version="IPv6")
        test.socket_dut.dstl_set_parameters_from_ip_server(test.echo_server)
        test.socket_dut.dstl_generate_address()
        test.expect(test.socket_dut.dstl_get_service().dstl_load_profile())
        test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())
        test.expect(
            test.socket_dut.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

        test.log.step("2. Set MTU on echo server to ~1400 (but no less than 1280 as it is minimal "
                      "value for IPv6)")
        test.echo_server_thread = test.thread(test.echo_server.dstl_server_execute_linux_command,
                                          "ifconfig")
        test.echo_server_thread.join()
        response = test.echo_server.linux_server_response
        test.interface = response[0: int(response.index(":"))]
        test.current_mtu = response[int(response.index("mtu "))+4:int(response.index("mtu "))+8]
        test.echo_server_thread = test.thread(test.echo_server.dstl_server_execute_linux_command,
                                          "sudo ifconfig {} mtu 1400".format(test.interface))
        test.echo_server_thread.join()

        test.log.step("3. Enable packet capturing using tcpdump or other such tool")
        dut_ip_address = test.socket_dut.dstl_get_parser() \
            .dstl_get_service_local_address_and_port('IPv6').split(']:')[0][1:]
        test.tcpdump_thread = test.thread(test.echo_server.dstl_server_execute_linux_command,
                                          "sudo timeout {0} tcpdump host {1} -A -i ens3 -c 20 "
                                          "-vv".
                                          format(test.timeout, dut_ip_address),
                                          timeout=test.timeout)

        test.log.step("4. Send data packets bigger and smaller than MTU (e.g. 1200 and 1460 bytes)")
        test.expect(test.socket_dut.dstl_get_service().
                    dstl_send_sisw_command_and_data(1450, repetitions=10))
        test.tcpdump_thread.join()
        test.log.info("TCPDUMP RESPONSE:")
        test.log.info(test.echo_server.linux_server_response)
        test.expect(test.socket_dut.dstl_get_service().dstl_read_all_data(1500,
                                                                          expect_urc_eod=False))
        test.expect("next-header Fragment" in test.echo_server.linux_server_response)
        data_amount = 1450*10
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_data_counter("rx") >=
                    data_amount)

        test.tcpdump_thread = test.thread(test.echo_server.dstl_server_execute_linux_command,
                                          "sudo timeout {0} tcpdump host {1} -A -i ens3 -c 20 "
                                          "-vv".
                                          format(test.timeout, dut_ip_address),
                                          timeout=test.timeout)
        test.expect(test.socket_dut.dstl_get_service().
                    dstl_send_sisw_command_and_data(500, repetitions=10))

        test.tcpdump_thread.join()
        test.log.info("TCPDUMP RESPONSE:")
        test.log.info(test.echo_server.linux_server_response)
        test.expect(test.socket_dut.dstl_get_service().dstl_read_all_data(1500,
                                                                          expect_urc_eod=False))
        data_amount = data_amount+(500*10)
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_data_counter("rx") >=
                    data_amount)
        test.expect("next-header Fragment" not in test.echo_server.linux_server_response)

        test.log.step("5. Read echoed data")
        test.log.info("Data read in previous step")

        test.log.step("6. Check in capture file if bigger packet was fragmented")
        test.log.info("Checked in step 4")

    def cleanup(test):
        try:
            test.echo_server.dstl_server_close_port()
            test.echo_server_thread = \
                test.thread(test.echo_server.dstl_server_execute_linux_command,
                            "sudo ifconfig {} mtu {}".format(test.interface, test.current_mtu))
            test.echo_server_thread.join()
        except AttributeError:
            test.log.error("Server object was not created.")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True, profile_id="0")


if "__main__" == __name__:
    unicorn.main()
