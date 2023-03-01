#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0093550.001, TC0093550.002

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import dstl_reset_internet_service_profiles
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState, Command


class Test(BaseTest):
    """Check the behaviour of module when listener don't have any free profile."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_set_scfg_tcp_with_urcs(test.r1, "on")
        test.expect(dstl_set_scfg_urc_dst_ifc(test.r1))
        test.expect(dstl_reset_internet_service_profiles(test.dut, force_reset=True))

    def run(test):
        test.log.step("1) Enter PIN and attach both modules to the network.")
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_register_to_network(test.r1))

        test.log.step("2) Define PDP context and activate it. "
                      "If module doesn't support PDP contexts, define connection profile.")
        conn_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(conn_setup_dut.dstl_load_and_activate_internet_connection_profile())
        conn_setup_r1 = dstl_get_connection_setup_object(test.r1)
        test.expect(conn_setup_r1.dstl_load_and_activate_internet_connection_profile())

        test.log.step("3) Define service profiles:\r\n - socket Non Transparent TCP listener on DUT"
                      "\r\n - socket Non Transparent TCP client on Remote")
        test.socket_listener = SocketProfile(test.dut, 0, conn_setup_dut.dstl_get_used_cid(),
                                             protocol="tcp", host="listener", localport=8888)
        test.socket_listener.dstl_generate_address()
        test.expect(test.socket_listener.dstl_get_service().dstl_load_profile())
        test.sockets_dut = [test.socket_listener]
        test.log.info("Client profile will be defined after opening listener profile.")

        test.log.step("4) Open connection on listener.")
        test.expect(test.socket_listener.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))
        dut_ip_address_and_port = test.socket_listener.dstl_get_parser().\
            dstl_get_service_local_address_and_port(ip_version='IPv4').split(":")

        test.socket_remote = SocketProfile(test.r1, 0, conn_setup_r1.dstl_get_used_cid(), protocol="tcp",
                                           host=dut_ip_address_and_port[0], port=dut_ip_address_and_port[1])
        test.socket_remote.dstl_generate_address()
        test.expect(test.socket_remote.dstl_get_service().dstl_load_profile())

        for profile_id in range(1, 10):
            test.log.step("5) Open connection on client.")
            test.expect(test.socket_remote.dstl_get_service().dstl_open_service_profile())
            test.expect(test.socket_remote.dstl_get_urc().dstl_is_sisw_urc_appeared('1'))

            test.log.step("6) Wait for URC on listener, then accept connection from client.")
            test.expect(test.socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared('1'))
            new_srv_id = test.socket_listener.dstl_get_urc().dstl_get_sis_urc_info_id()

            test.sockets_dut.append(SocketProfile(test.dut, new_srv_id, conn_setup_dut.dstl_get_used_cid()))
            test.expect(test.sockets_dut[profile_id].dstl_get_service().dstl_open_service_profile())
            test.expect(test.sockets_dut[profile_id].dstl_get_urc().dstl_is_sisw_urc_appeared('1'))

            test.log.step("7) Check service and socket states on DUT.")
            test.check_service_and_socket_states(profile_id, ServiceState.UP.value)

            test.log.step("8) On client close established connection with listener.")
            test.expect(test.socket_remote.dstl_get_service().dstl_close_service_profile())
            test.expect(test.sockets_dut[profile_id].dstl_get_urc().
                        dstl_is_sis_urc_appeared('0', '48', '"Remote peer has closed the connection"'))

            test.log.step("9) Check service and socket states on DUT.")
            test.check_service_and_socket_states(profile_id, ServiceState.DOWN.value)

            test.log.step("Repeat steps <5-9> 8 times (at the end all profiles on listener should be busy)."
                          "\r\nAlready repeated {} times.".format(profile_id-1))

        test.log.step("10) Try to open connection on client.")
        test.expect(test.socket_remote.dstl_get_service().dstl_open_service_profile(wait_for_default_urc=False))
        test.expect(test.socket_remote.dstl_get_urc().
                    dstl_is_sis_urc_appeared('0', '48', '"Remote peer has closed the connection"'))
        test.expect(test.socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared('2'))

    def cleanup(test):
        test.log.step("11) Close all connections on client and listener.")
        test.expect(test.socket_remote.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_remote.dstl_get_service().dstl_reset_service_profile())
        for socket in test.sockets_dut:
            test.expect(socket.dstl_get_service().dstl_close_service_profile())
            test.expect(socket.dstl_get_service().dstl_reset_service_profile())

    def check_service_and_socket_states(test, last_profile, last_profile_state):
        test.expect(test.socket_listener.dstl_get_parser().
                    dstl_get_service_state(at_command=Command.SISO_WRITE) == ServiceState.CONNECTING.value)
        test.expect(test.socket_listener.dstl_get_parser().
                    dstl_get_socket_state(at_command=Command.SISO_WRITE) == SocketState.LISTENER_ENDPOINT.value)
        for profile in range(1, last_profile):
            test.expect(test.sockets_dut[profile].dstl_get_parser().
                        dstl_get_service_state(at_command=Command.SISO_WRITE) == ServiceState.DOWN.value)
            test.expect(test.sockets_dut[profile].dstl_get_parser().
                        dstl_get_socket_state(at_command=Command.SISO_WRITE) == SocketState.SERVER.value)
        test.expect(test.sockets_dut[last_profile].dstl_get_parser().
                    dstl_get_service_state(at_command=Command.SISO_WRITE) == last_profile_state)
        test.expect(test.sockets_dut[last_profile].dstl_get_parser().
                    dstl_get_socket_state(at_command=Command.SISO_WRITE) == SocketState.SERVER.value)


if "__main__" == __name__:
    unicorn.main()
