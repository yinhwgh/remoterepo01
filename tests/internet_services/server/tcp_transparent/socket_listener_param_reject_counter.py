#responsible: dominik.tanderys@globallogic.com
#location: Wroclaw
#TC0094475.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_dtr
from dstl.auxiliary.generate_data import dstl_generate_data


class Test(BaseTest):
    """Intention:
    Testing UDP data transfer (client - endpoint; endpoint - client))

    description:
    1) Define TCP transparent listener on DUT. Autoconnect disabled.
    2) Open Listener and wait for URC: ^SIS: ,5
    3) Define five TCP transparent clients on Remote.
    4) Open five clients one by one and wait for URC: ^SIS: <srvProfileId>,3,0,"x.x.x.x:x" on listener side.
    5) Close rejected clients.
    6) Check service and socket state on Listener. Check reject counter.
    7) Accept the connection and wait for 'OK'. Switch to transparent mode on listener.
    8) Check service and socket state on Listener. Check reject counter.
    9) Switch to transparent mode on listener.
    10) Send data to client (3x1500 bytes).
    11) Read data and close client service.
    12) Wait for URC: ^SIS: ,0,48,"Remote peer has closed the connection"
    13) Check service and socket state on Listener. Server is now available for the next request.
    14) Send request from the second client to server.
    15) Check service and socket state on Listener.
    16) Accept the connection and wait for 'OK'. Switch to transparent mode on listener.
    17) Send data to client (3x1500 bytes).
    18) Read data and close client service.
    19) Wait for URC: ^SIS: ,0,48,"Remote peer has closed the connection"
    20) Check service and socket state on Listener. Server is now available for the next request.
    21) Close Listener service.
    22) Enable autoconnect transparent on listener.
    23) Open TCP listener.
    24) Open four clients one by one - one should be accepted, others rejected with indication "Remote peer has closed the connection".
    25) Listener service get in transparent mode automatically.
    26) Exchange some data.
    27) Switch to command mode on listener.
    28) Check service and socket state on Listener. Check reject counter.
    29) Listener closes the connection, the service state change to 4.
    30) Client close the connection.
    31) Close all connection and delete profiles."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_set_scfg_tcp_with_urcs(test.r1, "on")
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_register_to_network(test.r1))
        test.expect(test.dut.at1.send_and_verify("AT&D2"))

    def run(test):

        test.log.step("1) Define TCP transparent listener on DUT. Autoconnect disabled.")

        test.connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(test.connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        test.connection_setup_r1 = dstl_get_connection_setup_object(test.r1)
        test.expect(test.connection_setup_r1.dstl_load_and_activate_internet_connection_profile())

        test.socket_dut = SocketProfile(test.dut, 0, test.connection_setup_dut.dstl_get_used_cid(), protocol="tcp",
                                        host="listener", localport=8888, etx_char=26, autoconnect=0,
                                        connect_timeout="90")

        test.socket_dut.dstl_generate_address()
        test.expect(test.socket_dut.dstl_get_service().dstl_load_profile())

        test.log.step("2) Open Listener and wait for URC: ^SIS: ,5")
        test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))

        test.log.step("3) Define five TCP transparent clients on Remote.")
        test.expect(dstl_set_scfg_urc_dst_ifc(test.r1))
        dut_ip = test.socket_dut.dstl_get_parser().dstl_get_service_local_address_and_port(ip_version='IPv4').split(":")

        test.socket_remote = [SocketProfile(test.r1, 0, test.connection_setup_r1.dstl_get_used_cid(),
                                       protocol="tcp", host=dut_ip[0], port=dut_ip[1], etx_char=26)]
        test.socket_remote[0].dstl_generate_address()
        test.expect(test.socket_remote[0].dstl_get_service().dstl_load_profile())
        for srv_id in range(1, 5):
            test.socket_remote.append(SocketProfile(test.r1, srv_id, test.connection_setup_r1.dstl_get_used_cid(),
                                       protocol="tcp", host=dut_ip[0], port=dut_ip[1], etx_char=26))
            test.socket_remote[srv_id].dstl_generate_address()
            test.expect(test.socket_remote[srv_id].dstl_get_service().dstl_load_profile())

        test.log.step("4) Open five clients one by one and wait for URC: ^SIS: <srvProfileId>,3,0,\"x.x.x.x:x\" "
                      "on listener side.")
        for profile in test.socket_remote:
            test.expect(profile.dstl_get_service().dstl_open_service_profile(wait_for_default_urc=False))

        test.expect(test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("3"))

        test.log.step("5) Close rejected clients.")
        for srv_id in range(1, 5):
            test.expect(test.socket_remote[srv_id].dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
            test.expect(test.socket_remote[srv_id].dstl_get_service().dstl_close_service_profile())

        test.log.step("6) Check service and socket state on Listener. Check reject counter.")
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_socket_state() == SocketState.SERVER.value)
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_state() == ServiceState.ALERTING.value)
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_reject_counter() == 4)

        test.log.step("7) Accept the connection and wait for 'OK'. Switch to transparent mode on listener.")
        test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_dut.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        test.expect(test.socket_dut.dstl_get_service().dstl_enter_transparent_mode())

        test.log.step("8) Check service and socket state on Listener. Check reject counter.")
        test.expect(dstl_switch_to_command_mode_by_dtr(test.dut))
        test.expect(test.socket_dut.dstl_get_service().dstl_check_if_module_in_command_mode())
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_socket_state() == SocketState.SERVER.value)
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_state() == ServiceState.CONNECTED.value)
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_reject_counter() == 4)

        test.log.step("9) Switch to transparent mode on listener.")
        test.expect(test.socket_dut.dstl_get_service().dstl_enter_transparent_mode())

        test.log.step("10) Send data to client (3x1500 bytes).")
        for i in range(0, 3):
            test.expect(test.socket_dut.dstl_get_service().dstl_send_data(dstl_generate_data(1500), expected=""))

        test.log.step("11) Read data and close client service.")
        for i in range(0, 3):
            test.expect(test.socket_remote[0].dstl_get_service().dstl_read_data(1500))
        test.expect(test.socket_remote[0].dstl_get_service().dstl_close_service_profile())

        test.log.step("12) Wait for URC: ^SIS: ,0,48,\"Remote peer has closed the connection\"")
        test.expect(test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("0", "48",
                                                                            "\"Remote peer has closed the connection\""))

        test.log.step("13) Check service and socket state on Listener. Server is now available for the next request.")
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_socket_state() == SocketState.LISTENER_ENDPOINT.value)
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

        test.log.step("14) Send request from the second client to server.")
        test.socket_remote[1].dstl_get_service().dstl_open_service_profile()

        test.log.step("15) Check service and socket state on Listener.")
        test.expect(test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("3"))
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_socket_state() == SocketState.SERVER.value)
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_state() == ServiceState.ALERTING.value)

        test.log.step("16) Accept the connection and wait for 'OK'. Switch to transparent mode on listener.")
        test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_dut.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        test.expect(test.socket_dut.dstl_get_service().dstl_enter_transparent_mode())

        test.log.step("17) Send data to client (3x1500 bytes).")
        for i in range(0, 3):
            test.expect(test.socket_dut.dstl_get_service().dstl_send_data(dstl_generate_data(1500), expected=""))

        test.log.step("18) Read data and close client service.")
        for i in range(0, 3):
            test.expect(test.socket_remote[1].dstl_get_service().dstl_read_data(1500))

        test.expect(test.socket_remote[1].dstl_get_service().dstl_close_service_profile())

        test.log.step("19) Wait for URC: ^SIS: ,0,48,\"Remote peer has closed the connection\"")
        test.expect(test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("0", "48",
                                                                            "\"Remote peer has closed the connection\""))

        test.log.step("20) Check service and socket state on Listener. Server is now available for the next request.")
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_socket_state() == SocketState.LISTENER_ENDPOINT.value)
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

        test.log.step("21) Close Listener service.")
        test.expect(test.socket_dut.dstl_get_service().dstl_close_service_profile())

        test.log.step("22) Enable autoconnect transparent on listener.")
        test.socket_dut.dstl_set_autoconnect("1")
        test.socket_dut.dstl_set_address("")
        test.socket_dut.dstl_generate_address()
        test.expect(test.socket_dut.dstl_get_service().dstl_load_profile())

        test.log.step("23) Open TCP listener.")
        test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())

        test.log.step("24) Open four clients one by one - one should be accepted, others rejected with indication "
                      "\"Remote peer has closed the connection\".")
        test.expect(test.socket_remote[0].dstl_get_service().dstl_open_service_profile())
        test.expect(test.dut.at1.wait_for(".*CONNECT.*"))
        for srv_id in range(1, 4):
            test.expect(test.socket_remote[srv_id].dstl_get_service().dstl_open_service_profile(wait_for_default_urc=False))
            test.expect(test.socket_remote[srv_id].dstl_get_urc().dstl_is_sis_urc_appeared(urc_cause='0', urc_info_id="48"))

        test.log.step("25) Listener service get in transparent mode automatically.")
        test.expect(not test.socket_dut.dstl_get_service().dstl_check_if_module_in_command_mode())

        test.log.step("26) Exchange some data.")
        test.socket_dut.dstl_get_service().dstl_send_data(dstl_generate_data(1500), expected="")

        test.log.step("27) Switch to command mode on listener.")
        test.expect(dstl_switch_to_command_mode_by_dtr(test.dut))
        test.expect(test.socket_dut.dstl_get_service().dstl_check_if_module_in_command_mode())

        test.log.step("28) Check service and socket state on Listener. Check reject counter.")
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_socket_state() == SocketState.SERVER.value)
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_state() == ServiceState.CONNECTED.value)
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_reject_counter() == 3)

        test.log.step("29) Listener closes the connection, the service state change to 4.")
        test.expect(test.socket_dut.dstl_get_service().dstl_disconnect_remote_client())
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

    def cleanup(test):

        test.log.step("30) Client close the connection.")
        try:
            for profile in test.socket_remote:
                test.expect(profile.dstl_get_service().dstl_close_service_profile())
        except AttributeError:
            test.log.error("one of remote profile objects was not created.")

        test.log.step("31) Close all connection and delete profiles.")
        try:
            test.expect(test.socket_dut.dstl_get_service().dstl_close_service_profile())
        except AttributeError:
            test.log.error("one of dut profile objects was not created.")

        try:
            test.expect(test.dut.at1.send_and_verify("at^sips=all,reset", "OK"))
        except AttributeError:
            test.log.error("could not send at command to remote")

        try:
            test.expect(test.r1.at1.send_and_verify("at^sips=all,reset", "OK"))
        except AttributeError:
            test.log.error("could not send at command to dut")


if "__main__" == __name__:
    unicorn.main()
