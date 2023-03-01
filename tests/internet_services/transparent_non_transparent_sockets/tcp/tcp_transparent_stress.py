#responsible: wen.liu@thalesgroup.com
#location: Dalian
#TC0092724.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service import register_to_network
from dstl.call import switch_to_command_mode
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.ip_server.echo_server import EchoServer


class Test(BaseTest):
    '''
    TC0092724.001 - TpTcpTransparentStress
    Intention: Check whether COM port works properly each time after opening TCP connection, entering transparent mode and closing TCP connection for long period of time (+4h)
    Subscriber: 1
    Duration: at least 4h
    need add following config in local.cfg file, eg : tcp_echo_server_address = 78.47.86.194 and tcp_echo_server_port = 7
    '''


    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='OK'))
        test.dut.dstl_register_to_network()


    def run(test):
        test.log.step('1. Define socket profile for the TCP client.')
        connection_setup_dut = test.dut.dstl_get_connection_setup_object()
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        test.echo_server = EchoServer("IPv4", "TCP")
        socket_client = SocketProfile(test.dut, 1, connection_setup_dut.dstl_get_used_cid(), protocol="tcp", empty_etx=True)
        socket_client.dstl_set_parameters_from_ip_server(test.echo_server)
        socket_client.dstl_generate_address()
        test.expect(socket_client.dstl_get_service().dstl_load_profile())
        test.log.info('2.Enter and exit transparent mode')
        test.expect(socket_client.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        test.sleep(2)
        test.expect(socket_client.dstl_get_service().dstl_enter_transparent_mode())
        test.sleep(2)
        test.dut.dstl_switch_to_command_mode_by_pluses()
        test.log.info('3. Check if COM port works properly')
        test.expect(test.dut.at1.send_and_verify('at', expect='OK'))
        test.expect(socket_client.dstl_get_service().dstl_close_service_profile())
        test.expect(socket_client.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        test.sleep(2)
        test.expect(socket_client.dstl_get_service().dstl_close_service_profile())
        for i in range(1500):
            test.log.info('Test loop {}'.format(i))
            test.log.info('Enter and exit transparent mode')
            test.expect(socket_client.dstl_get_service().dstl_open_service_profile())
            test.expect(socket_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
            test.sleep(2)
            test.expect(socket_client.dstl_get_service().dstl_enter_transparent_mode())
            test.sleep(2)
            test.dut.dstl_switch_to_command_mode_by_pluses()
            test.log.info('Check if COM port works properly')
            test.expect(test.dut.at1.send_and_verify('at', expect='OK'))
            test.expect(socket_client.dstl_get_service().dstl_close_service_profile())
            test.expect(socket_client.dstl_get_service().dstl_open_service_profile())
            test.expect(socket_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
            test.sleep(2)
            test.expect(socket_client.dstl_get_service().dstl_close_service_profile())


    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('at^sisc=1','OK|ERROR'))


if '__main__' == __name__:
    unicorn.main()
