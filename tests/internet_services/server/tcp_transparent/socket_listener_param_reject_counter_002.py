#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0094475.002, TC0094475.004

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import dstl_reset_internet_service_profiles
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_etxchar
from dstl.auxiliary.generate_data import dstl_generate_data


class Test(BaseTest):
    """ This test checks parameter of Transparent TCP Listener : reject counter
    with autoconnect option disabled and enabled. """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_set_scfg_tcp_with_urcs(test.r1, "on")
        dstl_set_scfg_urc_dst_ifc(test.r1)
        test.expect(dstl_reset_internet_service_profiles(test.dut, force_reset=True))
        test.expect(dstl_reset_internet_service_profiles(test.r1, force_reset=True))
        test.connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(test.connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        test.connection_setup_r1 = dstl_get_connection_setup_object(test.r1)
        test.expect(test.connection_setup_r1.dstl_load_and_activate_internet_connection_profile())

    def run(test):
        test.log.info("Executing script for test case: 'TC0094475.002/004 SocketListenerParamRejectCounter'")

        test.log.step("1) Define TCP transparent listener on DUT. Autoconnect disabled.")
        socket_dut = SocketProfile(test.dut, 0, test.connection_setup_dut.dstl_get_used_cid(), protocol="tcp",
                                   host="listener", localport=8888, etx_char=26, autoconnect='0', connect_timeout="90")
        socket_dut.dstl_generate_address()
        test.expect(socket_dut.dstl_get_service().dstl_load_profile())
        dut_parser = socket_dut.dstl_get_parser()
        dut_urc = socket_dut.dstl_get_urc()
        dut_socket_service = socket_dut.dstl_get_service()

        test.log.step("2) Open Listener and wait for URC: ^SIS: ,5")
        test.expect(dut_socket_service.dstl_open_service_profile())
        test.expect(dut_urc.dstl_is_sis_urc_appeared("5\r\n"))

        test.log.step("3) Define five TCP transparent clients on Remote.")
        test.dut_ip = dut_parser.dstl_get_service_local_address_and_port(ip_version='IPv4').split(":")
        test.socket_remote = []
        for profile in range(5):
            test.socket_remote.append(test.define_client_profile(profile))

        test.log.step("4) Open five clients one by one and wait for URC: ^SIS: <srvProfileId>,3,0,\"x.x.x.x:x\" "
                      "on listener side.")
        test.expect(test.socket_remote[0].dstl_get_service().dstl_open_service_profile())
        test.expect(dut_urc.dstl_is_sis_urc_appeared("3"))
        for profile in range(1, 5):
            test.expect(test.socket_remote[profile].dstl_get_service().dstl_open_service_profile(wait_for_default_urc=False))
            test.expect(test.socket_remote[profile].dstl_get_urc()
                        .dstl_is_sis_urc_appeared('0', '48', '"Remote peer has closed the connection"'))

        test.log.step("5) Close rejected clients.")
        for profile in range(1, 5):
            test.expect(test.socket_remote[profile].dstl_get_service().dstl_close_service_profile())

        test.log.step("6) Check service and socket state on Listener. Check reject counter.")
        test.expect(dut_parser.dstl_get_service_state() == ServiceState.ALERTING.value)
        test.expect(dut_parser.dstl_get_socket_state() == SocketState.SERVER.value)
        test.expect(dut_parser.dstl_get_service_reject_counter() == 4)

        test.log.step("7) Accept the connection and wait for 'OK'.")
        test.expect(dut_socket_service.dstl_open_service_profile())
        test.expect(dut_urc.dstl_is_sisw_urc_appeared("1"))

        test.log.step("8) Send data to client (3x1500 bytes).")
        test.expect(dut_socket_service.dstl_enter_transparent_mode())
        test.expect(dut_socket_service.dstl_send_data(dstl_generate_data(1500), expected="", repetitions=3))

        test.log.step("9) Read data and close client service.")
        test.expect(test.socket_remote[0].dstl_get_urc().dstl_is_sisr_urc_appeared('1'))
        test.expect(test.socket_remote[0].dstl_get_service().dstl_read_data(1500, repetitions=3))
        test.expect(test.socket_remote[0].dstl_get_service().dstl_close_service_profile())

        test.log.step('10) Wait for URC: ^SIS: ,0,48,"Remote peer has closed the connection"')
        test.expect(dut_urc.dstl_is_sis_urc_appeared('0', '48', '"Remote peer has closed the connection"'))

        test.log.step("11) Check service and socket state on Listener. Server is now available for the next request.")
        test.expect(dut_parser.dstl_get_service_state() == ServiceState.UP.value)
        test.expect(dut_parser.dstl_get_socket_state() == SocketState.LISTENER_ENDPOINT.value)

        test.log.step("12) Send request from the second client to server.")
        test.socket_remote[1].dstl_get_service().dstl_open_service_profile()

        test.log.step("13) Check service and socket state on Listener.")
        test.expect(dut_urc.dstl_is_sis_urc_appeared("3"))
        test.expect(dut_parser.dstl_get_service_state() == ServiceState.ALERTING.value)
        test.expect(dut_parser.dstl_get_socket_state() == SocketState.SERVER.value)

        test.log.step("14) Accept the connection and wait for 'OK'.")
        test.expect(dut_socket_service.dstl_open_service_profile())
        test.expect(dut_urc.dstl_is_sisw_urc_appeared("1"))

        test.log.step("15) Send data to client (3x1500 bytes).")
        test.expect(dut_socket_service.dstl_enter_transparent_mode())
        test.expect(dut_socket_service.dstl_send_data(dstl_generate_data(1500), expected="", repetitions=3))

        test.log.step("16) Read data and check reject counter.")
        test.expect(test.socket_remote[1].dstl_get_urc().dstl_is_sisr_urc_appeared('1'))
        test.expect(test.socket_remote[1].dstl_get_service().dstl_read_data(1500, repetitions=3))
        test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, 26))
        test.expect(dut_socket_service.dstl_check_if_module_in_command_mode())
        test.expect(dut_parser.dstl_get_service_reject_counter() == 0)

        test.log.step("17) Client close connection.")
        test.expect(test.socket_remote[1].dstl_get_service().dstl_close_service_profile())

        test.log.step("18) Wait for URC: ^SIS: ,0,48,\"Remote peer has closed the connection\"")
        test.expect(dut_urc.dstl_is_sis_urc_appeared('0', '48', '"Remote peer has closed the connection"'))

        test.log.step("19) Check service and socket state on Listener. Server is now available for the next request.")
        test.expect(dut_parser.dstl_get_service_state() == ServiceState.UP.value)
        test.expect(dut_parser.dstl_get_socket_state() == SocketState.LISTENER_ENDPOINT.value)

        test.log.step("20) Close Listener service.")
        test.expect(dut_socket_service.dstl_close_service_profile())

        test.log.step("21) Enable autoconnect transparent on listener.")
        socket_dut.dstl_set_autoconnect("1")
        socket_dut.dstl_set_address("")
        socket_dut.dstl_generate_address()
        test.expect(dut_socket_service.dstl_load_profile())

        test.log.step("22) Open TCP listener (service and socket state = 4,3).")
        test.expect(dut_socket_service.dstl_open_service_profile())
        test.expect(dut_urc.dstl_is_sis_urc_appeared("5"))
        test.expect(dut_parser.dstl_get_service_state() == ServiceState.UP.value)
        test.expect(dut_parser.dstl_get_socket_state() == SocketState.LISTENER_ENDPOINT.value)

        test.log.step('23) Open four clients one by one - one should be accepted, others rejected with indication '
                      '"Remote peer has closed the connection".')
        test.expect(test.socket_remote[0].dstl_get_service().dstl_open_service_profile())
        test.expect(dut_urc.dstl_is_sis_urc_appeared('3', '1'))

        for srv_id in range(1, 4):
            test.expect(test.socket_remote[srv_id].dstl_get_service().dstl_open_service_profile(wait_for_default_urc=False))
            test.expect(test.socket_remote[srv_id].dstl_get_urc().dstl_is_sis_urc_appeared(urc_cause='0', urc_info_id="48"))

        test.log.step("24) Listener service get in transparent mode automatically.")
        test.expect(dut_socket_service.dstl_enter_transparent_mode(send_command=False))

        test.log.step("25) Exchange some data.")
        test.expect(dut_socket_service.dstl_send_data(dstl_generate_data(1500), expected=""))
        test.expect(test.socket_remote[0].dstl_get_urc().dstl_is_sisr_urc_appeared('1'))
        test.expect(test.socket_remote[0].dstl_get_service().dstl_read_data(1500))

        test.log.step("26) Check reject counter.")
        test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, 26))
        test.expect(dut_socket_service.dstl_check_if_module_in_command_mode())
        test.expect(dut_parser.dstl_get_service_reject_counter() == 3)

        test.log.step("27) Client close the connection, server get proper URC and the service state change to 4.")
        test.expect(test.socket_remote[0].dstl_get_service().dstl_close_service_profile())
        test.expect(dut_urc.dstl_is_sis_urc_appeared('0', '48', '"Remote peer has closed the connection"'))
        test.expect(dut_parser.dstl_get_service_state() == ServiceState.UP.value)
        test.expect(dut_parser.dstl_get_socket_state() == SocketState.LISTENER_ENDPOINT.value)

        for srv_id in range(1, 4):
            test.expect(test.socket_remote[srv_id].dstl_get_service().dstl_close_service_profile())

        test.log.step("28) New client do request to the server, this should be accepted automatically.")
        test.expect(test.socket_remote[1].dstl_get_service().dstl_open_service_profile())
        test.expect(dut_urc.dstl_is_sis_urc_appeared('3', '1'))
        test.expect(dut_socket_service.dstl_enter_transparent_mode(send_command=False))

        test.log.step("29) Exchange some data and server releases the connection, DUT is a listener again.")
        test.expect(dut_socket_service.dstl_send_data(dstl_generate_data(1500), expected=""))
        test.expect(test.socket_remote[1].dstl_get_urc().dstl_is_sisr_urc_appeared('1'))
        test.expect(test.socket_remote[1].dstl_get_service().dstl_read_data(1500))
        test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, 26))
        test.expect(dut_socket_service.dstl_check_if_module_in_command_mode())
        test.expect(dut_socket_service.dstl_disconnect_remote_client())
        test.expect(dut_parser.dstl_get_service_state() == ServiceState.UP.value)
        test.expect(dut_parser.dstl_get_socket_state() == SocketState.LISTENER_ENDPOINT.value)

        test.log.step("30) Client close the connection.")
        test.expect(test.socket_remote[1].dstl_get_service().dstl_close_service_profile())

        test.log.step("31) Close all connection and delete profiles.")
        test.expect(dut_socket_service.dstl_close_service_profile())
        test.expect(dut_socket_service.dstl_reset_service_profile())
        for srv_id in range(5):
            test.expect(test.socket_remote[srv_id].dstl_get_service().dstl_reset_service_profile())

    def cleanup(test):
        test.expect(dstl_reset_internet_service_profiles(test.dut, force_reset=True))
        test.expect(dstl_reset_internet_service_profiles(test.r1, force_reset=True))

    def define_client_profile(test, srv_id):
        socket_remote = SocketProfile(test.r1, srv_id, test.connection_setup_r1.dstl_get_used_cid(),
                                      protocol="tcp", host=test.dut_ip[0], port=test.dut_ip[1], etx_char=26)
        socket_remote.dstl_generate_address()
        test.expect(socket_remote.dstl_get_service().dstl_load_profile())
        return socket_remote


if "__main__" == __name__:
    unicorn.main()
