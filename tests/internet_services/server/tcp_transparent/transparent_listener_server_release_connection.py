# responsible: damian.latacz@globallogic.com
# Wroclaw
# TC0087968.001

import unicorn
import re

from core.basetest import BaseTest
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.auxiliary.init import dstl_detect
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_dtr
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
       TC intention: Server releases the connection with at^sish / at&d2.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_enter_pin(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(test.dut.at1.send_and_verify("AT&D2"))
        dstl_detect(test.r1)
        dstl_enter_pin(test.r1)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.r1, "on", device_interface="at2"))
        test.expect(dstl_set_scfg_urc_dst_ifc(test.r1, device_interface="at2"))

    def run(test):
        test.log.step("1. Define and activate PDP context/GPRS connection.")
        test.connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(test.connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        test.connection_setup_r1 = dstl_get_connection_setup_object(test.r1, device_interface="at2")
        test.expect(test.connection_setup_r1.dstl_load_and_activate_internet_connection_profile())
        cid = test.connection_setup_dut.dstl_get_used_cid()

        test.log.step("2. Define socket transparent listener on DUT and transparent client on Remote.")
        srv_profile_id = 0
        test.socket_dut = SocketProfile(test.dut, srv_profile_id, cid, protocol="tcp", host="listener", localport=65000,
                                        etx_char=26)
        test.socket_dut.dstl_generate_address()
        test.expect(test.socket_dut.dstl_get_service().dstl_load_profile())
        test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))
        dut_ip = \
        test.socket_dut.dstl_get_parser().dstl_get_service_local_address_and_port(ip_version='IPv4').split(":")[0]
        test.socket_r1 = SocketProfile(test.r1, srv_profile_id, test.connection_setup_r1.dstl_get_used_cid(),
                                       device_interface="at2", protocol="tcp", host=dut_ip, port=65000, etx_char=26)
        test.socket_r1.dstl_generate_address()
        test.expect(test.socket_r1.dstl_get_service().dstl_load_profile())

        test.log.step("3. Open defined profiles: first listener, then client.")
        test.log.info("Listener profile has been opened in previous step to get IP address.")
        test.expect(test.socket_r1.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_r1.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("4. Wait for SIS URC: ^SIS:x,3,0,\"x.x.x.x\" (^SIS:proId,incomingClient,infoId,remoteAddress).")
        test.expect(test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("3", "0"))
        test.expect("-1" not in test.socket_dut.dstl_get_urc().dstl_get_sis_urc_client_ip_address())

        test.log.step("5. Accept the connection with at^siso or at^sist (if applicable).")
        test.log.info("For {} connection will be accepted using AT^SISO.".format(test.dut.project))
        test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_dut.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("6. Server send 1024 bytes in transparent mode.")
        test.log.info("Entering the transparent mode.")
        test.expect(test.socket_dut.dstl_get_service().dstl_enter_transparent_mode())
        test.expect(test.socket_r1.dstl_get_service().dstl_enter_transparent_mode())
        test.log.info("Sending 1024 bytes of data from DUT to Remote")
        test.socket_dut.dstl_get_service().dstl_send_data(dstl_generate_data(1024), expected="")
        test.sleep(5)

        test.log.step("7. Switch to command mode.")
        test.expect(dstl_switch_to_command_mode_by_dtr(test.dut))
        test.expect(test.dut.dstl_switch_to_command_mode_by_dtr())
        test.expect(test.socket_dut.dstl_get_service().dstl_check_if_module_in_command_mode())
        test.expect(dstl_switch_to_command_mode_by_dtr(test.r1, device_interface="at2"))
        test.expect(test.socket_r1.dstl_get_service().dstl_check_if_module_in_command_mode())

        test.log.step("8. Check service state, socket state and amount of data.")
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_state() == ServiceState.CONNECTED.value)
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_socket_state() == SocketState.SERVER.value)
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_data_counter("tx") ==
                    test.socket_r1.dstl_get_parser().dstl_get_service_data_counter("rx"))

        test.log.step("9. Release the connection with at^sish.")
        test.expect(test.socket_dut.dstl_get_service().dstl_disconnect_remote_client())
        test.expect(test.socket_r1.dstl_get_urc().dstl_is_sis_urc_appeared("0", "48",
                                                                           "\"Remote peer has closed the connection\""))

        test.log.step("10. Check service and socket state.")
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_socket_state() == SocketState.LISTENER_ENDPOINT.value)

        test.log.step("11. Close listener and check state.")
        test.expect(test.socket_dut.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_state() == ServiceState.ALLOCATED.value)
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_socket_state() == SocketState.NOT_ASSIGNED.value)

        test.log.step("Repeat the testcase but release the connection with DTR toggle (at&d2) (if applicable).")
        test.log.info("Connection release using DTR toggle does not apply to {} - TC is completed.".format(test.dut.
                                                                                                           project))

    def cleanup(test):
        test.expect(test.socket_dut.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_r1.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_dut.dstl_get_service().dstl_reset_service_profile())
        test.expect(test.socket_r1.dstl_get_service().dstl_reset_service_profile())


if "__main__" == __name__:
    unicorn.main()
