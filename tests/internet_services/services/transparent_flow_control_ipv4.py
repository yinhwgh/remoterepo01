#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0093710.001,TC0093710.002


import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.restart_module import dstl_restart
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.call import switch_to_command_mode
from dstl.internet_service.parser.internet_service_parser import Command, ServiceState
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc

class Test(BaseTest):
    """
    TC0093710.001 - TransparentFlowControl_IPv4
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_detect(test.r1)
        dstl_restart(test.dut)
        dstl_restart(test.r1)
        dstl_enter_pin(test.dut)
        dstl_enter_pin(test.r1)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_set_scfg_tcp_with_urcs(test.r1, "on", device_interface="at2")
        dstl_set_scfg_urc_dst_ifc(test.r1, device_interface="at2")
        test.srv_id_1 = 0
        test.expect(test.dut.at1.send_and_verify('AT&D2', 'OK'))

    def run(test):
        test.log.step('0. Connection profile setup')
        connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        connection_setup_r1 = dstl_get_connection_setup_object(test.r1, device_interface="at2")
        test.expect(connection_setup_r1.dstl_load_and_activate_internet_connection_profile())

        for i in range(3):
            test.log.info('Repeat all steps with 3 escaping transparent mode way.')
            test.log.step('1. Set up TCP Socket Transparent Listener on DUT and TCP Socket Transparent Client on Remote')

            test.socket_dut_at1 = SocketProfile(test.dut, test.srv_id_1, connection_setup_dut.dstl_get_used_cid(),
                                                protocol="tcp",
                                                host="listener", localport=50000, etx_char=26,
                                                autoconnect="1",connect_timeout=30)
            test.socket_dut_at1.dstl_generate_address()
            test.expect(test.socket_dut_at1.dstl_get_service().dstl_load_profile())
            test.expect(test.socket_dut_at1.dstl_get_service().dstl_open_service_profile())
            test.expect(test.socket_dut_at1.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))

            dut_ip_address = test.socket_dut_at1.dstl_get_parser().dstl_get_service_local_address_and_port(ip_version='IPv4').split(":")[0]
            test.expect(test.socket_dut_at1.dstl_get_service().dstl_close_service_profile())
            test.socket_client = SocketProfile(test.r1, test.srv_id_1,
                                               connection_setup_r1.dstl_get_used_cid(), device_interface="at2",
                                               protocol="tcp", host=dut_ip_address,etx_char=26, port=50000)

            test.socket_client.dstl_generate_address()
            test.expect(test.socket_client.dstl_get_service().dstl_load_profile())

            test.log.step('2. Verify "RTS/CTS" hardware flow control is set.')
            test.expect(test.dut.at1.send_and_verify('AT&V','Q3'))

            test.log.step('3. Open services and establish transparent connection between DUT and Remote.')
            test.expect(test.socket_dut_at1.dstl_get_service().dstl_open_service_profile())
            test.expect(test.socket_dut_at1.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))

            test.expect(test.socket_client.dstl_get_service().dstl_open_service_profile())
            test.expect(test.dut.at1.wait_for('CONNECT'))
            test.expect(test.socket_client.dstl_get_service().dstl_enter_transparent_mode())

            test.log.step('4. Send some data from DUT to Remote and from Remote to DUT.')
            data1 = 'DATA_RTS_ON'
            data2 = 'DATA_RTS_OFF'
            test.expect(test.socket_dut_at1.dstl_get_service().dstl_send_data(data1, expected=""))
            test.sleep(3)
            test.expect(test.checkbuf('r1', data1,device_interface='at2'))
            test.expect(test.socket_client.dstl_get_service().dstl_send_data(data1, expected=""))
            test.sleep(3)
            test.expect(test.checkbuf('dut', data1))
            test.log.step('5. Toggle off RTS (Request To Send) line on DUT')
            test.dut.at1.connection.setRTS(False)
            test.log.step('6. Try to send some data from Remote to DUT.')
            test.expect(test.socket_client.dstl_get_service().dstl_send_data(data2, expected=""))
            test.sleep(5)
            test.expect(test.dut.at1.connection.rts == False)
            test.expect(test.checkbuf('dut', data2) == False)
            test.log.step('7. Toggle back on RTS (Request To Send) line on DUT.')
            test.dut.at1.connection.setRTS(True)
            test.log.step('8. Try to send some data from Remote to DUT.')
            test.expect(test.socket_client.dstl_get_service().dstl_send_data(data1, expected=""))
            test.sleep(3)
            test.expect(test.checkbuf('dut', data1))
            test.log.step('9. Exit transparent mode on DUT with [ESC].')
            if i == 0:
                test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
                test.expect(test.r1.dstl_switch_to_command_mode_by_pluses(device_interface="at2"))
            elif i == 1 :
                test.expect(test.dut.dstl_switch_to_command_mode_by_etxchar(etx_char=26))
                test.expect(test.r1.dstl_switch_to_command_mode_by_pluses(device_interface="at2"))
            else:
                test.attempt(test.dut.dstl_switch_to_command_mode_by_dtr, sleep=1, retry=3)
                test.expect(test.r1.dstl_switch_to_command_mode_by_pluses(device_interface="at2"))
            test.log.step('10. Check service states on DUT and Remote and close services.')
            test.expect(test.socket_dut_at1.dstl_get_parser().dstl_get_service_state(at_command=Command.SISO_WRITE) ==ServiceState.CONNECTED.value)
            test.expect(test.socket_client.dstl_get_parser().dstl_get_service_state(at_command=Command.SISO_WRITE) ==ServiceState.UP.value)
            test.expect(test.socket_dut_at1.dstl_get_service().dstl_close_service_profile())
            test.expect(test.socket_client.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        dstl_set_scfg_urc_dst_ifc(test.r1)

    def checkbuf(test, device, text, device_interface='at1'):
        device_interface = eval("test." +device+'.'+ device_interface)
        r_buffer = device_interface.read()
        test.log.info(f'Buffer content: {r_buffer}')
        if text in r_buffer:
            test.log.info('Data recevied')
            return True
        else:
            test.log.info('Data not recevied')
            return False


if "__main__" == __name__:
    unicorn.main()
