#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0102403.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.network_service import register_to_network
from dstl.serial_interface import config_baudrate
from dstl.call import switch_to_command_mode
from dstl.auxiliary import check_urc
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.parser.internet_service_parser import InternetServiceParser
from dstl.auxiliary.ip_server.echo_server import EchoServer

class Test(BaseTest):

    '''
    TC0102403.001 - UdpTransferdataWithDiffBaudRate
    need add following config in local.cfg file, eg:
    echo_server_address =78.47.86.194:7
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(3)
        test.dut.dstl_register_to_network()

    def run(test):
        ipr_list=test.dut.dstl_get_supported_baudrate_list()
        for baudrate in ipr_list:
            test.log.info(f'***Start test under baudrate {baudrate}***')

            test.log.step('1. Set ipr.')
            test.expect(test.dut.dstl_set_baudrate(baudrate,test.dut.at1))
            test.log.step('2. Config udp parameters')
            connection_setup_dut = dstl_get_connection_setup_object(test.dut)
            test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())

            test.echo_server = EchoServer("IPv4", "UDP")
            client_profile = SocketProfile(test.dut, 1, connection_setup_dut.dstl_get_used_cid(), protocol="udp",
                                           etx_char=26)
            client_profile.dstl_set_parameters_from_ip_server(test.echo_server)
            client_profile.dstl_generate_address()
            test.expect(client_profile.dstl_get_service().dstl_load_profile())

            test.sleep(2)
            test.log.step('3. at^siso to open udp connection.')
            test.expect(client_profile.dstl_get_service().dstl_open_service_profile())
            test.expect(test.dut.dstl_check_urc('SISW: 1,1'))
            test.sleep(2)
            test.log.step('4. Write & Read data in non-transparent mode.')
            test.expect(client_profile.dstl_get_service().dstl_send_sisw_command_and_data(15))
            test.expect(test.dut.dstl_check_urc('SISW: 1,1'))
            if client_profile.dstl_get_urc().dstl_is_sisr_urc_appeared("1",timeout=60):
                rxc = 30
            else:
                rxc = 0
            test.sleep(2)
            test.expect(test.dut.at1.send_and_verify('at^sisi=1', 'SISI: 1,4,0,15,0,0',timeout=30))
            test.log.step('5. at^sist to enter into data mode')
            test.expect(test.dut.at1.send_and_verify('at^sist=1', 'CONNECT',wait_for='CONNECT'))
            test.sleep(1)
            test.log.step('6. Transfer data.')
            test.dut.at1.send('123456789012345', end='')
            test.sleep(5)
            test.log.step('7. quit data mode.')
            test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
            test.sleep(5)
            test.log.step('8. At^sisi check txcount, rxcount.')
            test.expect(test.dut.at1.send_and_verify('at^sisi=1', f'SISI: 1,4,{rxc},30,0,0',timeout=30))
            test.log.step('9. Close and clear service profiles for client and server')
            test.expect(client_profile.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('at^sisc=1','OK|ERROR'))
        test.expect(test.dut.dstl_set_baudrate('115200', test.dut.at1))


if "__main__" == __name__:
    unicorn.main()