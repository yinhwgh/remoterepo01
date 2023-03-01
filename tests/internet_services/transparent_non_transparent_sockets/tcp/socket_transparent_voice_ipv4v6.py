#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0093260.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.network_service import register_to_network

from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_pluses
from dstl.call.setup_voice_call import dstl_release_call

class Test(BaseTest):

    '''
    TC0093260.002 - SocketTransparentVoiceOneInterface_ipv4_ipv6

    '''

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.r1.dstl_register_to_network()

    def run(test):
        loop=10

        test.log.step('0. Preparation: set proper scfg settings for Ringline.')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/ActiveTime","2"'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline","local"'))
        test.dut.dstl_restart()
        test.sleep(3)
        test.dut.dstl_register_to_network()
        test.set_up_service('IPV4')
        test.log.info('Close other module URC and open mctest Ringline URC')
        test.dut.at1.send_and_verify('AT+CREG=0', 'OK')
        test.dut.at1.send_and_verify('AT+CEREG=0', 'OK')
        test.dut.devboard.send_and_verify('MC:URC=RING')
        #loop step3-12
        for j in range(loop):
            test.log.info(f'*****Start IPV4 loop {j+1}*****')
            test.step3to12()
            test.log.info(f'*****End IPV4 loop {j + 1}*****')
        test.expect(test.dut.at1.send_and_verify('AT^SICA=0,1'))
        test.set_up_service('IPV6')
        # loop step3-12
        for j in range(loop):
            test.log.info(f'*****Start IPV6 loop {j + 1}*****')
            test.step3to12()
            test.log.info(f'*****End IPV6 loop {j + 1}*****')

    def cleanup(test):
        test.dut.at1.send_and_verify('at^sisc=1', 'O')

    def set_up_service(test, ipver):
        test.log.step('1. Define PDP context and activate it.')
        test.connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_version=ipver)
        test.expect(test.connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        test.log.step('2. Set TCP transparent client service profile, etx = 26.')
        test.echo_server = EchoServer(ipver, "TCP")
        test.client_profile = SocketProfile(test.dut, 1, test.connection_setup_dut.dstl_get_used_cid(),
                                       protocol="tcp",alphabet=1, ip_version=ipver,etx_char="26")

        test.client_profile.dstl_set_parameters_from_ip_server(test.echo_server)
        test.client_profile.dstl_generate_address()
        test.expect(test.client_profile.dstl_get_service().dstl_load_profile())
        test.expect(test.connection_setup_dut.dstl_load_internet_connection_profile())
        test.expect(test.connection_setup_dut.dstl_activate_internet_connection(), critical=True)

    def call_and_check_ringline(test):

        test.dut.devboard.read()
        test.r1.at1.send_and_verify(f'atd{test.dut.sim.nat_voice_nr};')
        test.expect(test.dut.devboard.wait_for('URC:  RINGline: 0'))
        test.log.step('7. Switch to command mode and accept the call.')
        test.attempt(test.dut.dstl_switch_to_command_mode_by_pluses, sleep=1, retry=3)
        test.expect(test.dut.at1.wait_for('RING'))
        test.dut.at1.send_and_verify('ATA', 'OK')
        test.log.step('8. After 10 sec. release the call.')
        test.sleep(10)
        test.dut.dstl_release_call()

    def step3to12(test):
        data_block_size=1000
        data_all = 50000
        test.log.step('3. Estabish socket transparent connection.')
        test.expect(test.client_profile.dstl_get_service().dstl_open_service_profile())
        test.dut.at1.wait_for('SISW: 1,1')
        test.sleep(2)
        test.log.step('4. Switch to data mode.')
        test.expect(test.client_profile.dstl_get_service().dstl_enter_transparent_mode(),
                    critical=True)
        test.log.step('5. Client sends 1000 characters x 50.')
        data_to_send = dstl_generate_data(data_block_size)
        for i in range(25):
            test.expect(test.client_profile.dstl_get_service().dstl_send_data(data_to_send,
                                                                              expected=data_to_send))
            test.sleep(1)
        test.log.step(
            '6.During sending data perform incoming voice call to DUT and check for RING LINE.')
        test.call_and_check_ringline()

        test.log.step('9. Switch to transparent mode and send the rest of data.')
        test.expect(test.client_profile.dstl_get_service().dstl_enter_transparent_mode(),
                    critical=True)
        for i in range(25):
            test.expect(test.client_profile.dstl_get_service().dstl_send_data(data_to_send,
                                                                              expected=data_to_send))
            test.sleep(1)
        test.log.step('10. check socket state and amount of data (50000).')
        test.attempt(test.dut.dstl_switch_to_command_mode_by_pluses, sleep=1, retry=3)
        test.expect(test.dut.at1.send_and_verify('at^sisi=1', f'SISI: 1,4,{data_all},{data_all}'))
        test.expect(test.dut.at1.send_and_verify('at^siso?',
                                                 f'SISO: 1,"Socket",4,2,{data_all},{data_all}'))
        test.log.step('11. Close socket connection.')
        test.expect(test.client_profile.dstl_get_service().dstl_close_service_profile())
        test.log.step('12. Check state after closing connection.')
        test.expect(test.dut.at1.send_and_verify('at^sisi=1', 'SISI: 1,2,0,0,0,0'))
        test.expect(test.dut.at1.send_and_verify('at^siso?', 'SISO: 1,"Socket",2,1,0,0'))


if "__main__" == __name__:
    unicorn.main()
