#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0092356.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.network_service import register_to_network
from dstl.auxiliary.ip_server.echo_server import EchoServer

from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.call import switch_to_command_mode


class Test(BaseTest):
    """
    TC0092356.002 - TsWriteTranspData_woURC_2nd_AtInterface - TestCase
    Intention: Transparent TCP Socket connection without URCs on 2nd Interace.
    Subscriber: 1
    Precondtion:
    1.need add following config in local.cfg file, eg: echo_server_address =78.47.86.194:7
    2.need config two DUT at interface (at1 and at2)
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.dut.dstl_register_to_network()

    def run(test):
        test.log.step('0. disable URC for Internet service commands')
        test.expect(test.dut.at1.send_and_verify("at&f"))
        test.expect(test.dut.dstl_set_scfg_tcp_with_urcs("off"))
        test.expect(test.dut.dstl_set_scfg_tcp_with_urcs("off",device_interface="at2"))
        test.log.step('1. Set PDP context')
        connection_setup_dut = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        test.log.step('2. Set service profile for Transparent Connection')

        test.echo_server = EchoServer("IPv4", "TCP")
        client_profile = SocketProfile(test.dut, 1, connection_setup_dut.dstl_get_used_cid(), protocol="tcp",
                                       etx_char=26)
        client_profile.dstl_set_parameters_from_ip_server(test.echo_server)
        client_profile.dstl_generate_address()
        test.expect(client_profile.dstl_get_service().dstl_load_profile())
        test.sleep(2)
        test.log.step('3. Open service')
        test.expect(client_profile.dstl_get_service().dstl_open_service_profile())
        test.sleep(10)

        test.log.step('4. Enter in transparent mode')
        test.expect(test.dut.at1.send_and_verify('at^sist=1', 'CONNECT', wait_for='CONNECT'))
        test.sleep(1)
        test.log.step('5. Transfer some data in transparent mode')
        data = dstl_generate_data(1495)
        test.expect(client_profile.dstl_get_service().dstl_send_data(data, expected=""))
        test.sleep(5)
        test.log.step('6. Escape from transparent mode')
        test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify('at^sisi=1', 'SISI: 1,4,1495,1495,1495,0', timeout=30))
        test.log.step('7. Close profile.')
        test.expect(client_profile.dstl_get_service().dstl_close_service_profile())

        test.log.step('8. On second interface open same service profile which was open on first interface')
        test.expect(test.dut.at2.send_and_verify('at^siso=1', 'OK'))
        test.sleep(10)
        test.log.step('9. Enter in transparent mode')
        test.expect(test.dut.at2.send_and_verify('at^sist=1', 'CONNECT', wait_for='CONNECT'))
        test.sleep(1)
        test.log.step('10. Transfer some data in transparent mode')
        test.dut.at2.send(data, end='')
        test.sleep(5)
        test.log.step('11. Escape from transparent mode')
        test.expect(test.dut.dstl_switch_to_command_mode_by_pluses(device_interface='at2'))
        test.sleep(5)
        test.expect(test.dut.at2.send_and_verify('at^sisi=1', 'SISI: 1,4,1495,1495,1495,0', timeout=30))
        test.log.step('12. Close service.')
        test.expect(test.dut.at2.send_and_verify('at^sisc=1', 'OK'))


    def cleanup(test):
        test.expect(test.dut.dstl_set_scfg_tcp_with_urcs("on"))
        test.expect(test.dut.dstl_set_scfg_tcp_with_urcs("on", device_interface="at2"))

if "__main__" == __name__:
    unicorn.main()
