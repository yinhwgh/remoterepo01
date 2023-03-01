# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0092653.001, TC0092653.003

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.parser.internet_service_parser import Command, ServiceState, SocketState
from dstl.packet_domain.ps_attach_detach import dstl_ps_detach, dstl_ps_attach


class Test(BaseTest):
    """	Check if it is possible to read data from the internal buffer after detach from PS."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.udp_server = EchoServer("IPV4", "UDP")

    def run(test):
        test.log.info("Execution of script for TC0092653.003/001 - "
                      "SocketUdpEndpointReadAfterPsDetach")

        test.log.step("1) Log-on to the network with used modules")
        test.expect(test.dut.dstl_register_to_network())

        test.log.step("2) Depend on product: "
                      "- Setup Internet Connection Profile "
                      "or "
                      "-  Setup appropriate PDP context and activate it")
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step("3) Setup Internet Service Profile for used modules – UDP endpoint "
                      "(different ports – e.g. 65301 and 65311)")
        socket = SocketProfile(test.dut, "0", test.connection_setup.dstl_get_used_cid(),
                               protocol="udp", port="8888")
        socket.dstl_generate_address()
        test.expect(socket.dstl_get_service().dstl_load_profile())

        test.log.step("4) Open service profiles"
                      "- Check for correct Service and Socket state. Use also AT^SISI if "
                      "product support it")
        test.expect(socket.dstl_get_service().dstl_open_service_profile())
        test.expect(socket.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        test.expect(socket.dstl_get_parser().dstl_get_socket_state() == SocketState.
                    LISTENER_ENDPOINT.value)

        test.expect(socket.dstl_get_parser().dstl_get_service_state(at_command=
                                                                    Command.SISI_READ) ==
                    ServiceState.UP.value)

        test.log.step("5) Send some data from  DUT to remote in few packets")
        server_address = "{}:{}".format(test.udp_server.dstl_get_server_ip_address(),
                                        test.udp_server.dstl_get_server_port())
        test.expect(socket.dstl_get_service().
                    dstl_send_sisw_command_and_data_UDP_endpoint(1460, server_address,
                                                                 eod_flag='0'))
        test.expect(socket.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(socket.dstl_get_service().
                    dstl_send_sisw_command_and_data_UDP_endpoint(1460, server_address, eod_flag='0',
                                                                 repetitions=4))
        test.sleep(10)  # Sleep to make sure all data had time to be transferred

        test.log.step("6) Wait for proper URC on remote side - read and compare data")
        test.log.info("comparing data will be done in step 11 as echo server was used as remote")

        test.log.step("7) Send some data from remote to DUT in few packets")
        test.log.info("done automatically in step 5 as echo server is used instead of remote")

        test.log.step("8) Wait for proper URC – do not read data")
        test.log.info("Done in previous step.")

        test.log.step("9) Detach DUT from PS domain")
        dstl_ps_detach(test.dut)
        test.sleep(10)  # Sleep so urc does not interfere with reading data

        test.log.step("10) Check for correct Service and Socket state. Use also AT^SISI if product "
                      "support it.")
        test.expect(socket.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        test.expect(socket.dstl_get_parser().dstl_get_socket_state() == SocketState.
                    LISTENER_ENDPOINT.value)
        test.expect(socket.dstl_get_parser().dstl_get_service_state(at_command=Command.SISI_READ)
                    == ServiceState.UP.value)

        test.log.step("11) DUT: read and compare data")
        test.log.info("comparing will be done in next step by comapring amount of data "
                      "sent/received")
        test.expect(socket.dstl_get_service().dstl_read_all_data(1500, expect_urc_eod=False))

        test.log.step("12) Check for correct Service and Socket state. Check RX and TX on both "
                      "sides")
        test.expect(socket.dstl_get_parser().dstl_get_service_data_counter("rx") >= 1460 * 4)
        test.expect(socket.dstl_get_parser().dstl_get_service_data_counter("tx") == 1460 * 5)
        test.expect(socket.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(socket.dstl_get_parser().dstl_get_socket_state() == SocketState.
                    LISTENER_ENDPOINT.value)

        test.log.step("13) Close services and check for correct Socket and Service state")
        test.expect(socket.dstl_get_service().dstl_close_service_profile())
        test.expect(socket.dstl_get_parser().dstl_get_service_data_counter("rx") == 0)
        test.expect(socket.dstl_get_parser().dstl_get_service_data_counter("tx") == 0)
        test.expect(socket.dstl_get_parser().dstl_get_service_state() == ServiceState.ALLOCATED.
                    value)
        test.expect(socket.dstl_get_parser().dstl_get_socket_state() == SocketState.NOT_ASSIGNED.
                    value)


    def cleanup(test):
        try:
            if not test.udp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")
        dstl_ps_attach(test.dut)
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)


if "__main__" == __name__:
    unicorn.main()
