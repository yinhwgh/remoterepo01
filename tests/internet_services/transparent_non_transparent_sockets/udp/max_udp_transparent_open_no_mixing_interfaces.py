#responsible: dominik.tanderys@globallogic.com
#location: Wroclaw
#TC0095077.003

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_etxchar
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.parser.internet_service_parser import ServiceState


class Test(BaseTest):
    """Intention:
    Check maximum number of Transparent UDP clients.
    Check that open services are allowed using other interface and check services state is not allowed (IPIS100314819).

    description:
    1. Prepare and activate PDP context.
    2. Set maximum UDP transparent client sockets (10 UDP clients are available) using first interface.
    3. Open client sockets using first interface.
    4. Exchange data in transparent mode using first interface - repeat for all service profiles one after another.
    5. Check service state on client using first interface.
    6. Try to check service state using second interface - not allowed.
    7. Close all services using first interface.
    8. Open and close clients using second interface.
    9. For some service profiles define UDP transparent client sockets using second interface.
    10. Open and close services defined in previous step using first interface.
    11. Open all socket services on both interfaces (each on that interface it was last used).
    12. Exchange data in transparent mode on two profiles - using both interfaces.
    13. Close all services using proper interface."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.expect(dstl_enter_pin(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT&D2"))
        test.ip_server = EchoServer("IPv4", "UDP")

    def run(test):

        test.log.step("1. Prepare and activate PDP context.")

        test.connection_setup_dut = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup_dut.dstl_load_and_activate_internet_connection_profile())

        test.log.step("2. Set maximum UDP transparent client sockets (10 UDP clients are available) "
                      "using first interface.")
        test.socket_dut = [SocketProfile(test.dut, 0, test.connection_setup_dut.dstl_get_used_cid(),
                                            protocol="udp", ip_server=test.ip_server, etx_char=26)]
        test.socket_dut[0].dstl_set_parameters_from_ip_server()
        test.socket_dut[0].dstl_generate_address()
        test.expect(test.socket_dut[0].dstl_get_service().dstl_load_profile())
        for srv_id in range(1, 10):
            test.socket_dut.append(SocketProfile(test.dut, srv_id, test.connection_setup_dut.dstl_get_used_cid(),
                                                protocol="udp", ip_server=test.ip_server, etx_char=26))
            test.socket_dut[srv_id].dstl_set_parameters_from_ip_server()
            test.socket_dut[srv_id].dstl_generate_address()
            test.expect(test.socket_dut[srv_id].dstl_get_service().dstl_load_profile())

        test.log.step("3. Open client sockets using first interface.")

        for service in test.socket_dut:
            test.expect(service.dstl_get_service().dstl_open_service_profile())

        test.log.step("4. Exchange data in transparent mode using first interface - repeat for all service profiles one"
                      " after another.")

        test.data = "test data 0123456789"
        for service in test.socket_dut:
            test.expect(service.dstl_get_service().dstl_enter_transparent_mode())
            test.expect(service.dstl_get_service().dstl_send_data(test.data, expected=test.data))
            dstl_switch_to_command_mode_by_etxchar(test.dut, etx_char=26)

        test.log.step("5. Check service state on client using first interface.")
        for service in test.socket_dut:
            test.expect(service.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value,
                        msg="Wrong service state")

        test.log.step("6. Try to check service state using second interface - not allowed.")
        test.socket_dut_asc1 = [SocketProfile(test.dut, 0, test.connection_setup_dut.dstl_get_used_cid(),
                                         protocol="udp", ip_server=test.ip_server, etx_char=26, device_interface="at2")]
        test.socket_dut_asc1[0].dstl_set_parameters_from_ip_server()
        test.socket_dut_asc1[0].dstl_generate_address()
        test.expect(not test.socket_dut_asc1[0].dstl_get_parser().dstl_get_service_state(),
                    msg="checking service state should not be possible")

        for srv_id in range(1, 10):
            test.socket_dut_asc1.append(SocketProfile(test.dut, srv_id, test.connection_setup_dut.dstl_get_used_cid(),
                                             protocol="udp", ip_server=test.ip_server, etx_char=26,
                                             device_interface="at2"))
            test.socket_dut_asc1[srv_id].dstl_set_parameters_from_ip_server()
            test.socket_dut_asc1[srv_id].dstl_generate_address()
            test.expect(not test.socket_dut_asc1[srv_id].dstl_get_parser().dstl_get_service_state(),
                        msg="checking service state should not be possible")

        test.log.step("7. Close all services using first interface.")
        for service in test.socket_dut:
            test.expect(service.dstl_get_service().dstl_close_service_profile())

        test.log.step("8. Open and close clients using second interface.")
        for service in test.socket_dut_asc1:
            test.expect(service.dstl_get_service().dstl_open_service_profile())
            test.expect(service.dstl_get_service().dstl_close_service_profile())

        test.log.step("9. For some service profiles define UDP transparent client sockets using second interface.")
        for srv_id in range(3, 6):
            test.expect(test.socket_dut_asc1[srv_id].dstl_get_service().dstl_load_profile())

        test.log.step("10. Open and close services defined in previous step using first interface.")
        for srv_id in range(3, 6):
            test.expect(test.socket_dut[srv_id].dstl_get_service().dstl_open_service_profile())
            test.expect(test.socket_dut[srv_id].dstl_get_service().dstl_close_service_profile())

        test.log.step("11. Open all socket services on both interfaces (each on that interface it was last used).")
        for srv_id in range(0, 10):
            if (srv_id < 3) or (srv_id > 5):
                test.expect(test.socket_dut_asc1[srv_id].dstl_get_service().dstl_open_service_profile())
            else:
                test.expect(test.socket_dut[srv_id].dstl_get_service().dstl_open_service_profile())

        test.log.step("12. Exchange data in transparent mode on two profiles - using both interfaces.")
        test.expect(test.socket_dut[4].dstl_get_service().dstl_enter_transparent_mode())
        test.expect(test.socket_dut[4].dstl_get_service().dstl_send_data(test.data, expected=test.data))

        test.expect(test.socket_dut_asc1[2].dstl_get_service().dstl_enter_transparent_mode())
        test.expect(test.socket_dut_asc1[2].dstl_get_service().dstl_send_data(test.data, expected=test.data))

        test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, etx_char=26))
        test.expect(test.socket_dut[4].dstl_get_service().dstl_check_if_module_in_command_mode(),
                    msg="problem leaving transparent mode")

        test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, etx_char=26, device_interface="at2"))
        test.expect(test.socket_dut_asc1[2].dstl_get_service().dstl_check_if_module_in_command_mode(),
                    msg="problem leaving transparent mode")

        test.log.step("13. Close all services using proper interface.")
        for srv_id in range(0, 10):
            if (srv_id < 3) or (srv_id > 5):
                test.expect(test.socket_dut_asc1[srv_id].dstl_get_service().dstl_close_service_profile())
            else:
                test.expect(test.socket_dut[srv_id].dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        try:
            test.ip_server.dstl_server_close_port()
        except AttributeError:
            test.log.error("Server object was not created.")


if "__main__" == __name__:
    unicorn.main()
