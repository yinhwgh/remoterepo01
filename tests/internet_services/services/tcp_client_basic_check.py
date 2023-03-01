#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0103578.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.network_service import register_to_network

from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.parser.internet_service_parser import InternetServiceParser
from dstl.auxiliary.ip_server.echo_server import EchoServer

class Test(BaseTest):

    '''
    TC0103578.001 - TcpClientBasic

    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(3)
        test.log.step('1. Module register to the network')
        test.dut.dstl_register_to_network()

    def run(test):
        test.log.step('2. Define socket profile for the TCP client.')
        connection_setup_dut = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        test.echo_server = EchoServer("IPv4", "TCP")
        client_profile = SocketProfile(test.dut, 1, connection_setup_dut.dstl_get_used_cid(), protocol="tcp")

        client_profile.dstl_set_parameters_from_ip_server(test.echo_server)
        client_profile.dstl_generate_address()
        test.expect(client_profile.dstl_get_service().dstl_load_profile())
        test.sleep(2)

        test.log.step('3. Open client service for DUT')
        test.expect(client_profile.dstl_get_service().dstl_open_service_profile())
        test.dut.at1.wait_for('SISW: 1,1')
        test.sleep(2)

        test.log.step('4. Send 15 bytes from client,wait for the feedback from the echo server.(repeat 50 times)')
        for i in range(50):
            test.log.info('********loop {} *******'.format(i+1))
            test.expect(client_profile.dstl_get_service().dstl_send_sisw_command_and_data(15))
            test.sleep(2)

        test.log.step('5. Check amount of sent and received data')
        test.expect(test.dut.at1.send_and_verify('at^sisi=1', 'SISI: 1,4,0,{},{},0'.format(15*50,15*50)))
        test.expect(test.dut.at1.send_and_verify('at^sisr=1,750', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^sisi=1', 'SISI: 1,4,{},{},{},0'.format(15 * 50, 15 * 50,15 * 50)))
        test.log.step('6. Close and clear service profiles for client and server')
        test.expect(client_profile.dstl_get_service().dstl_close_service_profile())

        test.log.step('7. Check the state with at^sisi again')
        test.expect(test.dut.at1.send_and_verify('at^sisi=1','SISI: 1,2,0,0,0,0'))

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('at^sisc=1','OK|ERROR'))


if "__main__" == __name__:
    unicorn.main()
