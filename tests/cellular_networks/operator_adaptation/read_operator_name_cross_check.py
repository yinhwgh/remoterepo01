#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0095518.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.network_service import register_to_network
from dstl.configuration import functionality_modes
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.call.setup_voice_call import dstl_is_voice_call_supported
from dstl.auxiliary.ip_server.echo_server import EchoServer


class Test(BaseTest):
    '''
    TC0095518.001 - ReadOperatorNamesCross
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(3)
        test.dut.dstl_register_to_network()
        test.r1.dstl_detect()
        test.r1.dstl_restart()
        test.sleep(3)
        test.r1.dstl_register_to_network()

    def run(test):
        test.log.info('1.When module in cyclic and non-cyclic sleep mode check Exec Command AT+COPN')

        # Expected copn response
        test.dut.at1.send_and_verify("AT+COPN", expect="OK", wait_for="OK")
        expected_copn = test.dut.at1.last_response
        # 1. When module in cyclic and non-cyclic sleep mode check Exec Command [AT+COPN]. -- not supported by Serval
        if test.dut.dstl_set_cyclic_sleep_mode(7):
            test.sleep(3)
            test.attempt(test.dut.at1.send_and_verify, "AT+COPN", expect="OK", append=False, timeout=1,
                         handle_errors=True, retry=10, sleep=0.5)
            response = test.dut.at1.last_response
            test.expect(expected_copn in response, msg="Expected: {}, actual: {}".format(expected_copn, response))
            test.sleep(3)
            test.dut.dstl_exit_sleep_mode(test.r1)
        if test.dut.dstl_set_cyclic_sleep_mode(9):
            test.sleep(3)
            test.attempt(test.dut.at1.send_and_verify, "AT+COPN", expect="OK", append=False, timeout=1,
                         handle_errors=True, retry=10, sleep=0.5)
            response = test.dut.at1.last_response
            test.expect(expected_copn in response, msg="Expected: {}, actual: {}".format(expected_copn, response))
            test.sleep(3)
            test.dut.dstl_exit_sleep_mode(test.r1)
        if test.dut.dstl_set_non_cyclic_sleep_mode():
            test.sleep(5)
            # Verify cannot imput commands
            test.expect(test.dut.at1.send_and_verify("AT+COPN", expect="", wait_for=".*", wait_after_send=5,
                                                     handle_errors=True))
            test.dut.dstl_exit_sleep_mode(False, test.r1)

        test.log.info('2.When start a voice call check Exec Command AT+COPN')
        if test.dut.dstl_is_voice_call_supported():
            test.dut.at1.send_and_verify('at^sm20=0', 'OK|ERROR')
            test.dut.at1.send_and_verify('atd{};'.format(test.r1.sim.nat_voice_nr), '.*')
            test.expect(test.r1.at1.wait_for('RING'))
            test.expect(test.dut.at1.send_and_verify('at+copn', 'OK'))
            test.sleep(1)
            test.dut.dstl_release_call()
        else:
            test.log.info('Not support voice call, skipped.')

        test.log.info('3. When connect TCP/UDP check Exec Command AT+COPN')

        connection_setup_dut = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        test.echo_server = EchoServer("IPv4", "UDP")
        test.client = SocketProfile(test.dut, 1, connection_setup_dut.dstl_get_used_cid(), protocol="udp")
        test.client.dstl_set_parameters_from_ip_server(test.echo_server)
        test.client.dstl_generate_address()
        test.expect(test.client.dstl_get_service().dstl_load_profile())

        test.expect(test.client.dstl_get_service().dstl_open_service_profile())
        test.dut.at1.wait_for('SISW: 1,1')
        test.expect(test.dut.at1.send_and_verify('at+copn', 'OK'))
        test.expect(test.client.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
