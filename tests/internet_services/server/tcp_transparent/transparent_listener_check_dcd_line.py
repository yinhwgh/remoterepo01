#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0087971.001


import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.restart_module import dstl_restart
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_pluses
from dstl.internet_service.parser.internet_service_parser import Command, ServiceState

class Test(BaseTest):
    """
    TC0087971.001 - TransparentListenerCheckDCDLine
    This test is provided to verify the behavior of the ME's of the DCD line.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_detect(test.r1)
        dstl_restart(test.dut)
        dstl_restart(test.r1)
        dstl_enter_pin(test.dut)
        dstl_enter_pin(test.r1)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_set_scfg_tcp_with_urcs(test.r1, "on")
        test.srv_id_1 = 0

    def run(test):

        test.log.step('1. Enable DCD line detection for IP services (AT&C2)')
        test.expect(test.dut.at1.send_and_verify("AT&C2"))
        test.expect(test.dut.at1.send_and_verify("AT&V", ".*&C2.*"))

        test.log.step('2. Defined and activated internet connection on both side.')
        connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        connection_setup_r1 = dstl_get_connection_setup_object(test.r1, ip_public=True)
        test.expect(connection_setup_r1.dstl_load_and_activate_internet_connection_profile())

        test.log.step('3. Configure a Transparent TCP Listener on DUT with parameters: autoconnect=1,connecttimeout=30.')
        test.socket_dut_at1 = SocketProfile(test.dut, test.srv_id_1, connection_setup_dut.dstl_get_used_cid(),
                                            protocol="tcp",
                                            host="listener", localport=50000, etx_char=26,autoconnect="1",connect_timeout=30)
        test.socket_dut_at1.dstl_generate_address()
        test.expect(test.socket_dut_at1.dstl_get_service().dstl_load_profile())
        test.expect(test.socket_dut_at1.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_dut_at1.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))

        test.log.step('4. Configure Transparent TCP client on Remote.')
        dut_ip_address = test.socket_dut_at1.dstl_get_parser().dstl_get_service_local_address_and_port(ip_version='IPv4').split(":")[0]
        test.expect(test.socket_dut_at1.dstl_get_service().dstl_close_service_profile())
        test.socket_client = SocketProfile(test.r1, test.srv_id_1, connection_setup_r1.dstl_get_used_cid(),
                                           protocol="tcp", host=dut_ip_address, port=50000)

        test.socket_client.dstl_generate_address()
        test.expect(test.socket_client.dstl_get_service().dstl_load_profile())

        test.log.step('5. Open service on DUT.')
        test.expect(test.socket_dut_at1.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_dut_at1.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))

        test.log.step('6. Check service state and DCD line on DUT side.')
        test.expect(test.socket_dut_at1.dstl_get_parser().dstl_get_service_state(at_command=Command.SISO_WRITE)
                    == ServiceState.UP.value)
        test.expect(test.dut.at1.connection.cd)

        test.log.step('7. Send request from client and accept the connection on DUT.')
        test.expect(test.socket_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.dut.at1.wait_for('CONNECT'))
        test.attempt(test.dut.dstl_switch_to_command_mode_by_pluses, sleep=1, retry=3)

        test.log.step('8. Check service state and DCD line on DUT side.')
        test.expect(test.socket_dut_at1.dstl_get_parser().dstl_get_service_state(at_command=Command.SISO_WRITE)
                    == ServiceState.CONNECTED.value)
        test.expect(test.dut.at1.connection.cd)

        test.log.step('9. Client releases connection.')
        test.expect(test.socket_client.dstl_get_service().dstl_close_service_profile())

        test.log.step('10. Check service state and DCD line on DUT side.')
        test.expect(test.dut.at1.wait_for('.*SIS: 0,0,48.*'))
        test.expect(test.socket_dut_at1.dstl_get_parser().dstl_get_service_state(at_command=Command.SISO_WRITE)
                    == ServiceState.UP.value)
        test.expect(test.dut.at1.connection.cd)

        test.log.step('11. Close the service on DUT.')
        test.expect(test.socket_dut_at1.dstl_get_service().dstl_close_service_profile())

        test.log.step('12. Check service state and DCD line on DUT side.')
        test.expect(test.socket_dut_at1.dstl_get_parser().dstl_get_service_state(at_command=Command.SISO_WRITE)
                    == ServiceState.ALLOCATED.value)
        test.expect(not test.dut.at1.connection.cd)

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify(f'at^siss={test.srv_id_1},"srvType","none"'))
        test.expect(test.r1.at1.send_and_verify(f'at^siss={test.srv_id_1},"srvType","none"'))


if "__main__" == __name__:
    unicorn.main()
