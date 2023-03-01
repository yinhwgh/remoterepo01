# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0095547.001 TC0095547.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_pluses
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs


class Test(BaseTest):
    """
    TC0095547.002/001 - TransparentTcpInterfaceUrcCheck
    Intention:
    Check the behavior of URC when multiple interface are used to control service profiles

    description:
    1) Define Internet connection or PDP context (if product supports it) for DUT and Remote.
    2) On DUT define Transparent TCP Listener profile (using first tested interface, e.g. ASC0).
    3) Open Internet service profile on DUT
    4) On Remote - define Transparent TCP Client
    5) Open Internet service profile on Remote
    6) On DUT, accept connection incoming from Remote
    7) On DUT enter data mode and send 200 bytes of data to Remote.
    8) Try to open TCP Listener once again on the other ATC interface (e.g. USB ACM).
    9) Obtain Internet service information with appropriate command (e.g. AT^SISI), using second interface
        (e.g. USB ACM)
    10) Exit data mode on the Listener side using +++.
    11) Send 10 bytes of data from Remote and wait for appropriate URC on Listener ATC interface. Read exactly 10 bytes
        of data on DUT.
    12) Close the connection on the remote site and wait for appropriate URC on Listener ATC interface.
    13) Close and delete all defined profiles.

    """

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        dstl_get_imei(test.r1)
        dstl_get_imei(test.dut)
        test.dut.dstl_set_scfg_tcp_with_urcs("on")
        test.r1.dstl_set_scfg_tcp_with_urcs("on")

    def run(test):
        test.log.step('1) Define Internet connection or PDP context (if product supports it) for DUT and Remote.')
        connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())

        connection_setup_r1 = dstl_get_connection_setup_object(test.r1)
        test.expect(connection_setup_r1.dstl_load_and_activate_internet_connection_profile())

        test.log.step('2) On DUT define Transparent TCP Listener profile (using first tested interface, e.g. ASC0). ')
        test.socket_dut = SocketProfile(test.dut, "0", connection_setup_dut.dstl_get_used_cid(), protocol="tcp",
                               host="listener", localport=65100, connect_timeout=180, etx_char=26)
        test.socket_dut.dstl_generate_address()
        test.expect(test.socket_dut.dstl_get_service().dstl_load_profile())

        test.log.step('3) Open Internet service profile on DUT')
        test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))

        test.dut_ip_address = \
            test.socket_dut.dstl_get_parser().dstl_get_service_local_address_and_port(ip_version='IPv4').split(":")[0]

        test.log.step('4) On Remote - define Transparent TCP Client')
        test.socket_r1 = SocketProfile(test.r1, "0", connection_setup_r1.dstl_get_used_cid(),
                               protocol="tcp", host=test.dut_ip_address, port=65100, etx_char=26)
        test.socket_r1.dstl_generate_address()
        test.expect(test.socket_r1.dstl_get_service().dstl_load_profile())

        test.log.step('5) Open Internet service profile on Remote')
        test.expect(test.socket_r1.dstl_get_service().dstl_open_service_profile())

        test.log.step('6) On DUT, accept connection incoming from Remote')
        test.expect(test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared(urc_cause="3"))
        test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_dut.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step('7) On DUT enter data mode and send 200 bytes of data to Remote.')
        test.expect(test.socket_dut.dstl_get_service().dstl_enter_transparent_mode())

        test.socket_dut.dstl_get_service().dstl_send_data(dstl_generate_data(200), expected="")

        test.log.step('8) Try to open TCP Listener once again on the other ATC interface (e.g. USB ACM).')
        test.expect(test.dut.at2.send_and_verify("at^siso=0", "ERROR"))

        test.log.step('9) Obtain Internet service information with appropriate command (e.g. AT^SISI), using second '
                      'interface (e.g. USB ACM)')
        test.expect(test.dut.at2.send_and_verify("at^siso?", 'SISO: 0,"Socket"\r\n'))

        test.log.step('10) Exit data mode on the Listener side using +++.')
        test.expect(dstl_switch_to_command_mode_by_pluses(test.dut))

        test.log.step('11) Send 10 bytes of data from Remote and wait for appropriate URC on Listener ATC interface. '
                      'Read exactly 10 bytes of data on DUT.')
        test.expect(test.socket_r1.dstl_get_service().dstl_send_sisw_command_and_data(10))
        test.expect(test.socket_dut.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(test.socket_dut.dstl_get_service().dstl_read_data(10))

        test.log.step('12) Close the connection on the remote site and wait for appropriate URC on Listener ATC '
                      'interface.')
        test.expect(test.socket_r1.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared(urc_info_text='"Remote peer has closed the '
                                                                                          'connection"',
                                                                            urc_info_id="48", urc_cause="0"))

    def cleanup(test):
        test.log.step('13) Close and delete all defined profiles.')
        try:
            test.expect(test.socket_dut.dstl_get_service().dstl_close_service_profile())
            test.expect(test.socket_dut.dstl_get_service().dstl_reset_service_profile())
        except AttributeError:
            test.log.error("problem with connection to module")

        try:
            test.expect(test.socket_r1.dstl_get_service().dstl_close_service_profile())
            test.expect(test.socket_r1.dstl_get_service().dstl_reset_service_profile())
        except AttributeError:
            test.log.error("problem with connection to module")

if "__main__" == __name__:
    unicorn.main()
