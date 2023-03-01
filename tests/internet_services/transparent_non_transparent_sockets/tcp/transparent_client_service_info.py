# responsible: grzegorz.dziublinski@globallogic.com
# location: Wroclaw
# TC0096183.001, TC0096183.002

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.parser.internet_service_parser import Command, ServiceState
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_etxchar


class Test(BaseTest):
    """Testing states of transparent TCP service profiles and DCD line state."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.expect(dstl_register_to_network(test.dut))
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        test.expect(dstl_enter_pin(test.r1))
        test.expect(dstl_register_to_network(test.r1))
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_set_scfg_tcp_with_urcs(test.r1, "on", device_interface="at2")
        dstl_set_scfg_urc_dst_ifc(test.r1, device_interface="at2")

    def run(test):
        test.log.info("Executing script for test case: 'TransparentClientServiceInfo'")

        test.log.step("1. define and activate IPv4 PDP contexts for both modules")
        test.connection_setup_dut = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        test.connection_setup_r1 = dstl_get_connection_setup_object(test.r1, ip_public=True,
                                                                    device_interface="at2")
        test.expect(test.connection_setup_r1.dstl_load_and_activate_internet_connection_profile())

        test.log.step("2. activate DCD line for internet service (at&c=2)")
        test.expect(test.dut.at1.send_and_verify("AT&C2"))

        test.log.step("3. remote: define 10 service profiles for transparent TCP listener")
        test.sockets_remote = []
        for i in range(10):
            test.sockets_remote.append(test.define_transparent_tcp_listener(test, i))

        test.log.step("4. remote: open all profiles")
        for i in range(10):
            test.expect(test.sockets_remote[i].dstl_get_service().dstl_open_service_profile())
            test.expect(test.sockets_remote[i].dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))
        test.log.info("Checking IP address for Remote.")
        test.remote_ip_address = \
            test.sockets_remote[0].dstl_get_parser().dstl_get_service_local_address_and_port(
                ip_version='IPv4').split(":")[0]

        test.log.step("5. dut: define 8 service profiles for transparent TCP client")
        test.sockets_dut = []
        for i in range(8):
            test.sockets_dut.append(test.define_transparent_tcp_client(test, i))

        test.log.step("6. dut: check service states with at^siso and DCD line state")
        for i in range(8):
            test.expect(test.sockets_dut[i].dstl_get_parser().dstl_get_service_state(
                at_command=Command.SISO_WRITE) == ServiceState.ALLOCATED.value)
        test.log.info("Checking DCD line state.")
        test.expect(not test.dut.at1.connection.cd)
        test.log.step("7. dut: open all 8 profiles")
        test.r1.at2.read()
        for i in range(6):
            test.expect(test.sockets_dut[i].dstl_get_service().dstl_open_service_profile())
            test.expect(test.sockets_dut[i].dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
            test.expect(test.sockets_remote[i].dstl_get_urc().dstl_is_sis_urc_appeared("3", "0"))
        for i in range(6, 8):
            test.expect(test.sockets_dut[i].dstl_get_service().
                        dstl_open_service_profile(wait_for_default_urc=False))
            test.expect(test.sockets_dut[i].dstl_get_urc().dstl_is_sis_urc_appeared("0"))

        test.log.step("8. dut: check service states with at^siso and DCD line state")
        for i in range(6):
            test.expect(test.sockets_dut[i].dstl_get_parser().dstl_get_service_state(
                at_command=Command.SISO_WRITE) == ServiceState.UP.value)
        for i in range(6, 8):
            test.expect(test.sockets_dut[i].dstl_get_parser().dstl_get_service_state(
                at_command=Command.SISO_WRITE) == ServiceState.DOWN.value)
        test.log.info("Checking DCD line state.")
        test.expect(test.dut.at1.connection.cd)

        test.log.step("9. remote: accept 6 clients requests")
        for i in range(6):
            test.expect(test.sockets_remote[i].dstl_get_service().dstl_open_service_profile())
            test.expect(test.sockets_remote[i].dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("10. dut: check service states with at^siso")
        for i in range(6):
            test.expect(test.sockets_dut[i].dstl_get_parser().dstl_get_service_state(
                at_command=Command.SISO_WRITE) == ServiceState.UP.value)
        for i in range(6, 8):
            test.expect(test.sockets_dut[i].dstl_get_parser().dstl_get_service_state(
                at_command=Command.SISO_WRITE) == ServiceState.DOWN.value)

        test.log.step("11. dut: close rejected service profiles")
        for i in range(6, 8):
            test.expect(test.sockets_dut[i].dstl_get_service().dstl_close_service_profile())

        test.log.step("12. dut: check service states with at^siso")
        for i in range(6):
            test.expect(test.sockets_dut[i].dstl_get_parser().dstl_get_service_state(
                at_command=Command.SISO_WRITE) == ServiceState.UP.value)
        for i in range(6, 8):
            test.expect(test.sockets_dut[i].dstl_get_parser().dstl_get_service_state(
                at_command=Command.SISO_WRITE) == ServiceState.ALLOCATED.value)

        test.log.step("13. remote: close and reset two listener services")
        for i in range(8, 10):
            test.expect(test.sockets_remote[i].dstl_get_service().dstl_close_service_profile())
            test.expect(test.sockets_remote[i].dstl_get_service().dstl_reset_service_profile())

        test.log.step("14. dut: open again 2 recently rejected service profiles")
        for i in range(6, 8):
            test.expect(test.sockets_dut[i].dstl_get_service().dstl_open_service_profile())
            test.expect(test.sockets_dut[i].dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
            test.expect(test.sockets_remote[i].dstl_get_urc().dstl_is_sis_urc_appeared("3", "0"))

        test.log.step("15. dut: check service states with at^siso")
        test.dut.at1.read()
        for i in range(8):
            test.expect(test.sockets_dut[i].dstl_get_parser().dstl_get_service_state(
                at_command=Command.SISO_WRITE) == ServiceState.UP.value)

        test.log.step("16. remote: accept client requests")
        for i in range(6, 8):
            test.expect(test.sockets_remote[i].dstl_get_service().dstl_open_service_profile())
            test.expect(test.sockets_remote[i].dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("17. switch to transparent mode on both modules")
        test.expect(test.sockets_dut[0].dstl_get_service().dstl_enter_transparent_mode())
        test.expect(test.sockets_remote[0].dstl_get_service().dstl_enter_transparent_mode())

        test.log.step("18. dut: check DCD line state")
        test.expect(test.dut.at1.connection.cd)

        test.log.step("19. exchange data from client to server and vice versa")
        test.sockets_dut[0].dstl_get_service().dstl_send_data(dstl_generate_data(100), expected="")
        test.sockets_remote[0].dstl_get_service().dstl_send_data(dstl_generate_data(100), expected="")
        test.sleep(3)

        test.log.step("20. switch back to command mode on both modules")
        test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, 26))
        test.expect(dstl_switch_to_command_mode_by_etxchar(test.r1, 26, device_interface="at2"))

        test.log.step("21. dut: check service states with at^siso and DCD line state")
        test.dut.at1.read()
        for i in range(8):
            test.expect(test.sockets_dut[i].dstl_get_parser().dstl_get_service_state(
                at_command=Command.SISO_WRITE) == ServiceState.UP.value)
        test.log.info("Checking DCD line state.")
        test.expect(test.dut.at1.connection.cd)

        test.log.step("22. dut: close all profiles")
        for i in range(8):
            test.expect(test.sockets_dut[i].dstl_get_service().dstl_close_service_profile())

        test.log.step("23. dut: check service states with at^siso and DCD line state")
        for i in range(8):
            test.expect(test.sockets_dut[i].dstl_get_parser().dstl_get_service_state(
                at_command=Command.SISO_WRITE) == ServiceState.ALLOCATED.value)
        test.log.info("Checking DCD line state.")
        test.expect(not test.dut.at1.connection.cd)

        test.log.step("24. remote: close all profiles")
        for i in range(8):
            test.expect(test.sockets_remote[i].dstl_get_service().dstl_close_service_profile())

    @staticmethod
    def define_transparent_tcp_listener(test, srv_id):
        socket = SocketProfile(test.r1, srv_id, test.connection_setup_r1.dstl_get_used_cid(),
                               device_interface="at2", protocol="tcp", host="listener",
                               localport=65100+int(srv_id), connect_timeout=180, etx_char=26)
        socket.dstl_generate_address()
        test.expect(socket.dstl_get_service().dstl_load_profile())
        return socket

    @staticmethod
    def define_transparent_tcp_client(test, srv_id):
        socket = SocketProfile(test.dut, srv_id, test.connection_setup_dut.dstl_get_used_cid(),
                               protocol="tcp", host=test.remote_ip_address, port=65100+int(srv_id),
                               etx_char=26)
        socket.dstl_generate_address()
        test.expect(socket.dstl_get_service().dstl_load_profile())
        return socket

    def cleanup(test):
        try:
            for i in range(10):
                test.expect(test.sockets_remote[i].dstl_get_service().
                            dstl_close_service_profile(expected="O"))
            for i in range(8):
                test.expect(test.sockets_dut[i].dstl_get_service().dstl_close_service_profile())
        except (AttributeError, IndexError):
            test.log.error("Object was not created.")
        dstl_set_scfg_urc_dst_ifc(test.r1)


if "__main__" == __name__:
    unicorn.main()
