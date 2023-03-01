#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0092324.002, TC0092324.004

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import dstl_reset_internet_service_profiles
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState, Command


class Test(BaseTest):
    """Testing states of socket connection profiles using "mode" parameter from command AT^SISO."""

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
        test.log.h2("Executing script for test case: 'TC0092324.002/004 StatusRequestPerService'")
        test.dut_sockets = []

        test.log.step("1) Enter PIN and attach both modules to the network.")
        test.log.info('This will be done together with next step')

        test.log.step("2) Define PDP context and activate it. If module doesn't support PDP contexts, "
                      "define connection profile.")
        test.conn_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(test.conn_setup_dut.dstl_load_and_activate_internet_connection_profile())
        test.conn_setup_r1 = dstl_get_connection_setup_object(test.r1)
        test.expect(test.conn_setup_r1.dstl_load_and_activate_internet_connection_profile())

        test.log.step("3) Define service profiles: socket Non Transparent TCP Server on DUT, "
                      "socket Transparent TCP Listener on DUT.")
        test.dut_sockets.append(SocketProfile(test.dut, 0, test.conn_setup_dut.dstl_get_used_cid(), protocol="tcp",
                                              host="listener", localport=8888))
        test.dut_sockets[0].dstl_generate_address()
        test.expect(test.dut_sockets[0].dstl_get_service().dstl_load_profile())

        test.dut_sockets.append(test.define_transp_tcp_listener('1'))

        test.log.step("4) Open connection on Non Transparent TCP Server. Define service profiles: "
                      "socket Non Transparent TCP Client on Remote, socket Transparent TCP Client on Remote.")
        test.expect(test.dut_sockets[0].dstl_get_service().dstl_open_service_profile())
        test.expect(test.dut_sockets[0].dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))
        dut_ip_address_and_port = test.dut_sockets[0].dstl_get_parser()\
            .dstl_get_service_local_address_and_port(ip_version='IPv4').split(":")

        test.non_transp_tcp_client = SocketProfile(test.r1, 0, test.conn_setup_r1.dstl_get_used_cid(), protocol="tcp",
                                      host=dut_ip_address_and_port[0], port=dut_ip_address_and_port[1])
        test.non_transp_tcp_client.dstl_generate_address()
        test.expect(test.non_transp_tcp_client.dstl_get_service().dstl_load_profile())

        test.transp_tcp_client = SocketProfile(test.r1, 1, test.conn_setup_r1.dstl_get_used_cid(), protocol="tcp",
                                      host=dut_ip_address_and_port[0], port=7980, etx_char=26)
        test.transp_tcp_client.dstl_generate_address()
        test.expect(test.transp_tcp_client.dstl_get_service().dstl_load_profile())

        test.log.step("5) On DUT check individual status of each defined profile with Internet Service Open command.")
        test.check_service_states(ServiceState.CONNECTING.value, ServiceState.ALLOCATED.value)

        test.log.step("6) Close Non Transparent TCP Server.")
        test.expect(test.dut_sockets[0].dstl_get_service().dstl_close_service_profile())

        test.log.step("7) Open Transparent TCP Listener.")
        test.expect(test.dut_sockets[1].dstl_get_service().dstl_open_service_profile())
        test.expect(test.dut_sockets[1].dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))

        test.log.step("8) On DUT check individual status of each defined profile with Internet Service Open command.")
        test.check_service_states(ServiceState.ALLOCATED.value, ServiceState.UP.value)

        test.log.step("9) Open connection on Non Transparent TCP Server.")
        test.expect(test.dut_sockets[0].dstl_get_service().dstl_open_service_profile())
        test.expect(test.dut_sockets[0].dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))
        test.dut.at1.read()

        test.log.step("10) Establish connection between client and Non Transparent TCP Server.")
        test.expect(test.non_transp_tcp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.non_transp_tcp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        test.expect(test.dut_sockets[0].dstl_get_urc().dstl_is_sis_urc_appeared("1"))
        dynamic_profile_id = test.dut_sockets[0].dstl_get_urc().dstl_get_sis_urc_info_id()

        test.dut_sockets.append(SocketProfile(test.dut, dynamic_profile_id, test.conn_setup_dut.dstl_get_used_cid()))
        test.expect(test.dut_sockets[2].dstl_get_service().dstl_open_service_profile())
        test.expect(test.dut_sockets[2].dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("11) On DUT check individual status of each defined profile with Internet Service Open command.")
        test.check_service_states(ServiceState.CONNECTING.value, ServiceState.UP.value, ServiceState.UP.value)

        test.log.step("12) Close client connection to server.")
        test.expect(test.non_transp_tcp_client.dstl_get_service().dstl_close_service_profile())
        test.expect(test.dut_sockets[2].dstl_get_urc().dstl_is_sis_urc_appeared('0', '48', '"Remote peer has closed the connection"'))

        test.log.step("13) On DUT check individual status of each defined profile with Internet Service Open command.")
        test.check_service_states(ServiceState.CONNECTING.value, ServiceState.UP.value, ServiceState.DOWN.value)

        test.log.step("14) Close Non Transparent TCP Server.")
        test.expect(test.dut_sockets[0].dstl_get_service().dstl_close_service_profile())

        test.log.step("15) On DUT check individual status of each defined profile with Internet Service Open command.")
        test.check_service_states(ServiceState.ALLOCATED.value, ServiceState.UP.value, ServiceState.DOWN.value)

        test.log.step("16) Establish connection between client and Transparent TCP Listener.")
        test.expect(test.transp_tcp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.transp_tcp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        test.expect(test.dut_sockets[1].dstl_get_urc().dstl_is_sis_urc_appeared("3"))

        test.expect(test.dut_sockets[1].dstl_get_service().dstl_open_service_profile())
        test.expect(test.dut_sockets[1].dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("17) On DUT check individual status for each active connection with Internet Service Open command.")
        test.check_service_states(ServiceState.ALLOCATED.value, ServiceState.CONNECTED.value, ServiceState.DOWN.value)

        test.log.step("18) Define maximum number of Transparent TCP Listeners on DUT.")
        for profile in range(3, 10):
            test.dut_sockets.append(test.define_transp_tcp_listener(profile))

        test.log.step("19) Open all defined Transparent TCP Listeners on DUT.")
        for profile in range(3, 10):
            test.expect(test.dut_sockets[profile].dstl_get_service().dstl_open_service_profile())
            test.expect(test.dut_sockets[profile].dstl_get_urc().dstl_is_sis_urc_appeared("5"))

        test.log.step("20) On DUT check individual status for each defined profile with Internet Service Open command.")
        test.check_service_states(ServiceState.ALLOCATED.value, ServiceState.CONNECTED.value,
                                  ServiceState.DOWN.value, ServiceState.UP.value)

        test.log.step("21) Compare each response from point 20 with Internet Service Open read command.")
        for profile in range(10):
            test.expect(test.dut_sockets[profile].dstl_get_parser().dstl_get_service_state(Command.SISO_WRITE)
                        == test.dut_sockets[profile].dstl_get_parser().dstl_get_service_state(Command.SISO_READ))

        test.log.step("22) Close all opened profiles.")
        for profile in range(10):
            test.expect(test.dut_sockets[profile].dstl_get_service().dstl_close_service_profile())
        test.expect(test.transp_tcp_client.dstl_get_service().dstl_close_service_profile())
        test.expect(test.non_transp_tcp_client.dstl_get_service().dstl_close_service_profile())

        test.log.step("23) On DUT check individual status for each defined profile with Internet Service Open command.")
        test.check_service_states(ServiceState.ALLOCATED.value, ServiceState.ALLOCATED.value,
                                  ServiceState.ALLOCATED.value, ServiceState.ALLOCATED.value)

    def cleanup(test):
        test.expect(dstl_reset_internet_service_profiles(test.dut, force_reset=True))
        test.expect(dstl_reset_internet_service_profiles(test.r1, force_reset=True))

    def define_transp_tcp_listener(test, srv_id):
        transp_tcp_listener = SocketProfile(test.dut, srv_id, test.conn_setup_dut.dstl_get_used_cid(), protocol="tcp",
                                            host="listener", localport=7979+int(srv_id), etx_char=26)
        transp_tcp_listener.dstl_generate_address()
        test.expect(transp_tcp_listener.dstl_get_service().dstl_load_profile())
        return transp_tcp_listener

    def check_service_states(test, non_transp_listener_state, transp_listener_state,
                             dynamic_profile_state=None, transp_listeners_state=None):
        test.expect(test.get_service_state(0) == non_transp_listener_state)
        test.expect(test.get_service_state(1) == transp_listener_state)
        if dynamic_profile_state:
            test.expect(test.get_service_state(2) == dynamic_profile_state)
        if transp_listeners_state:
            for profile in range(3, 10):
                test.expect(test.get_service_state(profile) == transp_listeners_state)

    def get_service_state(test, profile):
        return test.dut_sockets[profile].dstl_get_parser().dstl_get_service_state(Command.SISO_WRITE)


if "__main__" == __name__:
    unicorn.main()
