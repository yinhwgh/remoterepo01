#responsible: dominik.tanderys@globallogic.com
#location: Wroclaw
#TC0093696.001, TC0093696.002

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.parser.internet_service_parser import SocketState, ServiceState
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_etxchar
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """Check if Transparent TCP Listener Service is working correctly and it is possible to establish connection with
    auto answer mode and using addrfilter option."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_register_to_network(test.dut))
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        test.expect(dstl_restart(test.r1))
        test.expect(dstl_register_to_network(test.r1))
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_set_scfg_tcp_with_urcs(test.r1, "on")
        dstl_set_scfg_urc_dst_ifc(test.r1, device_interface="at2")

    def run(test):
        test.log.step("1) Configure and activate PDP context/define Internet Connection profile for both modules.")
        connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        dut_ip = connection_setup_dut.dstl_get_pdp_address()
        connection_setup_r1 = dstl_get_connection_setup_object(test.r1, device_interface="at2", ip_public=True)
        connection_setup_r1.dstl_load_and_activate_internet_connection_profile()
        remote_ip = connection_setup_r1.dstl_get_pdp_address()

        test.log.step("2) Configure services:"
                      "- On DUT: transparent TCP listener, enable autoconnect "
                      "     and addrfilter set to IP address of client,"
                      "- On Remote transparent TCP client.")
        test.dut_listener = SocketProfile(test.dut, "0", connection_setup_dut.dstl_get_used_cid(), protocol="tcp",
                                          host="listener", localport=8888, connect_timeout=180, etx_char=26,
                                          addr_filter=remote_ip[0], autoconnect="1")
        test.dut_listener.dstl_generate_address()
        test.expect(test.dut_listener.dstl_get_service().dstl_load_profile())

        test.remote_client = SocketProfile(test.r1, "0", connection_setup_r1.dstl_get_used_cid(),
                                           device_interface="at2", protocol="tcp", host=dut_ip[0], port=8888,
                                           etx_char=26)
        test.remote_client.dstl_generate_address()
        test.expect(test.remote_client.dstl_get_service().dstl_load_profile())

        test.log.step("3) Open listener service.")
        test.expect(test.dut_listener.dstl_get_service().dstl_open_service_profile())
        test.expect(test.dut_listener.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))

        test.log.step("4) Open client service, check if incoming connection was accepted automatically.")
        test.expect(test.remote_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.dut_listener.dstl_get_urc().dstl_is_sis_urc_appeared(urc_cause="3", urc_info_id="1"),
                    msg="no correct SIS URC appeared")

        test.log.step('5) Check if after establishing of the connection listener service takes over command line and '
                      'outputs "CONNECT" URC.')
        test.expect("CONNECT" in test.dut.at1.last_response)
        test.expect(not test.dut_listener.dstl_get_service().dstl_check_if_module_in_command_mode(),
                    msg="Module not in transparent mode")

        test.log.step("6) Switch to data mode on remote peer.")
        test.expect(test.remote_client.dstl_get_service().dstl_enter_transparent_mode(),
                    msg="Problem entering transparent mode")

        test.log.step("7) Send some data transparently from remote peer to DUT.")
        data_length = 100
        data = dstl_generate_data(data_length)
        test.expect(test.remote_client.dstl_get_service().dstl_send_data(data, expected=""))

        test.log.step("8) On remote peer side switch to command mode and release the connection.")
        test.expect(dstl_switch_to_command_mode_by_etxchar(test.r1, device_interface="at2", etx_char=26))
        test.expect(test.remote_client.dstl_get_service().dstl_close_service_profile())

        test.log.step("9) Check if listener outputs a release URC and reestablishes the command line.")
        test.expect(test.dut_listener.dstl_get_urc().dstl_is_sis_urc_appeared(urc_cause="0", urc_info_id="48",
                                                                              urc_info_text='"Remote peer has closed '
                                                                                            'the connection"'))
        test.expect(test.dut_listener.dstl_get_service().dstl_check_if_module_in_command_mode(),
                    msg="Module still in transparent mode")

        test.log.step("10) Check if service (DUT) is waiting for next connection.")
        test.expect(test.dut_listener.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        test.expect(test.dut_listener.dstl_get_parser().dstl_get_socket_state() == SocketState.LISTENER_ENDPOINT.value)

        test.log.step("11) Close listener service.")
        test.expect(test.dut_listener.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):

        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        dstl_reset_internet_service_profiles(test.r1, force_reset=True)
        dstl_set_scfg_urc_dst_ifc(test.r1)


if "__main__" == __name__:
    unicorn.main()
