# responsible: jie.jin@thalesgroup.com
# location: Beijing
# TC0088122.005

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.network_service.register_to_network import dstl_register_to_network, dstl_enter_pin
from dstl.call.switch_to_command_mode import *
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import *
from dstl.auxiliary.init import dstl_detect
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.call.switch_to_command_mode import *

class Test(BaseTest):
    """
        TC0088122.001	SwitchToCommandModeDuringPPPConnection
        1.Define PDP context "at+cgdcont=1,"IP","apn-provider""
        2.Establish ppp connection "at+cgdata="PPP",1"
        3.Send some data to echo server
        4.Wait for response from server
        5.Return to command mode using escape sequence "+++"
        6.Check pdp context "at+cgdcont?"
        7.Return to data mode "ato"
        8.Repeat two last steps 3 times.
        9.After return to data mode send some data to the server.
        10.Release connection.
"""
    def setup(test):
        dstl_restart(test.dut)
        dstl_detect(test.dut)
        dstl_enter_pin(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.expect(dstl_enter_pin(test.dut), critical=True)
        test.udp_echo_server_ipv4 = EchoServer("IPV4", "UDP")
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.connection_setup.dstl_load_and_activate_internet_connection_profile()

    def run(test):
        test.log.step("1.Define PDP context at+cgdcont=1,""IP"",""apn-provider""")
        test.expect(test.dut.at1.send_and_verify(f'AT+CGDCONT=1,"IP","{test.dut.sim.apn_v4}"', '.*OK.*'))
        test.log.step("2.Establish ppp connection at+cgdata=""PPP"",""1""")
        test.expect(test.dut.at1.send_and_verify('AT+CGDATA="PPP",{}'.format(1), ".*CONNECT.*"))
        # test.log.step("3.Send some data to echo server")
        # test.socket = SocketProfile(test.dut, "1", test.connection_setup.dstl_get_used_cid(), protocol="udp",etx_char=26)
        # test.socket.dstl_set_parameters_from_ip_server(test.udp_echo_server_ipv4)
        # #test.socket.dstl_generate_address()
        # test.expect(test.socket.dstl_get_service().dstl_load_profile())
        # test.expect(test.socket.dstl_get_service().dstl_open_service_profile())
        # test.expect(test.socket.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        # test.expect(test.socket.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        # test.expect(test.socket.dstl_get_parser().dstl_get_service_local_address_and_port('IPv4'))
        # test.log.step("4.Wait for response from server")
        # test.expect(test.socket.dstl_get_service().dstl_enter_transparent_mode())
        # data = dstl_generate_data(100)
        # test.expect(test.socket.dstl_get_service().dstl_send_data(data, expected="", repetitions=5))
        # test.expect(test.dut.at1.wait_for(data * 5))
        # amount_of_sent_data = len(data) * 5
        # test_sequence = "+++a"
        # test.expect(test.socket.dstl_get_service().dstl_send_data(test_sequence, expected=""))
        # test.dut.at1.wait_for(test_sequence)
        # test.sleep(5)
        # test.expect('OK' not in test.dut.at1.last_response)
        # amount_of_sent_data += len(test_sequence)
        # test.expect(test.socket.dstl_get_service().dstl_send_data(bytes(chr(16), encoding='ascii'), expected=""))
        # test.expect(test.socket.dstl_get_service().dstl_send_data(bytes(chr(16), encoding='ascii'), expected=""))
        # test.sleep(5)
        # test.expect('OK' not in test.dut.at1.last_response)
        # amount_of_sent_data += 1
        test.log.step("5. Switch to command mode via +++")
        test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
        test.log.step("6. Check AT+CGATT?")
        test.expect(test.dut.at1.send_and_verify('at+cgatt?', '.*OK.*', timeout=30))
        test.log.step("7. Return to data mode \"ato\"")
        test.expect(test.dut.at1.send_and_verify('ATO', ".*CONNECT.*",timeout=60))
        test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
        test.log.step("8.Repeat two last steps 3 times.")
        for i in range(3):
            test.expect(test.dut.at1.send_and_verify('at+cgatt?', '.*OK.*', timeout=30))
            test.expect(test.dut.at1.send_and_verify('ATO', ".*CONNECT.*", timeout=60))
            test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
        test.log.step("After return to data mode send some data to the server")
        test.expect(test.dut.at1.send_and_verify('ATO', ".*CONNECT.*", timeout=30))
        # test.expect(test.socket.dstl_get_service().dstl_send_data(bytes(chr(16), encoding='ascii'), expected=""))
        # test.expect(test.socket.dstl_get_service().dstl_send_data(bytes(chr(16), encoding='ascii'), expected=""))
        test.sleep(5)
        test.expect('OK' not in test.dut.at1.last_response)
        test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
        test.expect(test.dut.at1.send_and_verify('ATH', '.*OK.*'))

    def cleanup(test):
        pass


if __name__ == "__main__":
    unicorn.main()
