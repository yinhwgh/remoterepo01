#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0095011.001


import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.restart_module import dstl_restart
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.internet_service.parser.internet_service_parser import Command, ServiceState


class Test(BaseTest):
    """
    TC0095011.001 - TransparentTcpCharacterSequence
    This test checks whether after reset transparent connection, the module return character sequence:
    0x10 (DLE), 0x04 (EOT), S3 (CR), S4 (LF), "NOCARRIER" followed by the S3 (CR), S4 (LF).
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
        test.log.info('1. Enable URC mode for Internet Service commands.')
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_set_scfg_tcp_with_urcs(test.r1, "on")

        test.log.info('2. Define PDP context and activate it (if module doesn')
        connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        connection_setup_r1 = dstl_get_connection_setup_object(test.r1, ip_public=True)
        test.expect(connection_setup_r1.dstl_load_and_activate_internet_connection_profile())

        test.log.info('3. Define service profiles:-on DUT: TCP transparent listener;-on Remote: TCP transparent client')
        test.log.info('3.1 -on DUT: TCP transparent listener')
        test.socket_dut_at1 = SocketProfile(test.dut, test.srv_id_1, connection_setup_dut.dstl_get_used_cid(),
                                            protocol="tcp",
                                            host="listener", localport=50000, etx_char=26,autoconnect="1",connect_timeout=30)
        test.socket_dut_at1.dstl_generate_address()
        test.expect(test.socket_dut_at1.dstl_get_service().dstl_load_profile())
        test.expect(test.socket_dut_at1.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_dut_at1.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))

        test.log.info('3.2 -on Remote: TCP transparent client')
        dut_ip_address = test.socket_dut_at1.dstl_get_parser().dstl_get_service_local_address_and_port(ip_version='IPv4').split(":")[0]

        test.socket_client = SocketProfile(test.r1, test.srv_id_1, connection_setup_r1.dstl_get_used_cid(),
                                           protocol="tcp", host=dut_ip_address, port=50000)
        test.socket_client.dstl_generate_address()
        test.expect(test.socket_client.dstl_get_service().dstl_load_profile())

        test.log.info('4. First open listener and then open client service.')
        test.expect(test.socket_client.dstl_get_service().dstl_open_service_profile())

        test.log.info('5. On DUT establish connection with client.')
        test.log.info('6. Enter transparent mode on DUT side.')
        test.expect(test.dut.at1.wait_for('CONNECT'))

        test.log.info('7. Send 100 bytes data to Remote and receive it.')
        data = dstl_generate_data(100)
        test.expect(test.socket_dut_at1.dstl_get_service().dstl_send_data(data, expected=""))

        test.log.info('8. On the second interface on DUT change functionality level to "0".')
        test.expect(test.dut.at2.send_and_verify('at+cfun=0', 'OK', wait_for='\^SYSSTART AIRPLANE MODE'))

        test.log.info('9. Now check correctness character sequence (for manual perform in log file).')
        test.sleep(10)
        r_buffer = test.dut.at1.read_binary()
        test.expect(test.check_char_sequence(r_buffer))

        test.log.info('10. Return to functionality level "1".')
        test.expect(test.dut.at2.send_and_verify('at+cfun=1', 'OK',wait_for='\^SYSSTART'))
        test.sleep(5)
        dstl_enter_pin(test.dut)

        test.log.info('11. Check service state on DUT.')
        test.expect(test.socket_dut_at1.dstl_get_parser().dstl_get_service_state(at_command=Command.SISO_WRITE)
                    == ServiceState.DOWN.value)

        test.log.info('12. Close and delete services profiles on both side.')
        test.expect(test.socket_dut_at1.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_client.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify(f'at^siss={test.srv_id_1},"srvType","none"'))
        test.expect(test.r1.at1.send_and_verify(f'at^siss={test.srv_id_1},"srvType","none"'))

    def check_char_sequence(test,read_buffer):
        if b'\x10\x04\r\nNO CARRIER\r\n' in read_buffer:
            test.log.info('Correct sequence is found')
            return True
        else:
            if b'\x10' not in read_buffer:
                test.log.error('EOT not found')
            if b'\x04' not in read_buffer:
                test.log.error('DLE not found')
            if b'\r' not in read_buffer:
                test.log.error('CR sign not found')
            if b'\n' not in read_buffer:
                test.log.error('LF sign not found')
            if b'NO CARRIER' not in read_buffer:
                test.log.error('NO CARRIER not found')

            return False


if "__main__" == __name__:
    unicorn.main()
