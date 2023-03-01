#responsible: feng.han@thalesgroup.com
#location: Dalian
#TC0091955.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module
from dstl.auxiliary import check_urc
from dstl.call.setup_voice_call import dstl_release_call
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.parser.internet_service_parser import InternetServiceParser
from dstl.auxiliary.ip_server.echo_server import EchoServer


class Test(BaseTest):
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='OK'))
        test.expect(test.dut.at2.send_and_verify('at+cmee=2', expect='OK'))
        test.expect(test.r1.at1.send_and_verify('at+cmee=2', expect='OK'))
        test.r1.dstl_detect()
        test.expect(test.r1.dstl_register_to_network())
    def run(test):
        test.log.step("1. Enable CEREG and CREG URC to report status of network registration")
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify('at+creg=1', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+cereg=1', expect='OK'))

        test.log.step("2. Make registration to Network.")
        test.expect(test.dut.dstl_register_to_network())
        test.connection_setup_dut = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        test.log.step("3. Create transparent TCP client and initiate data transfer.")
        test.step4to8('TCP')
        test.log.step("9. Repeat test from step 4 to 8 for transparent UDP Client.")
        test.step4to8('UDP')


    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('at^sisc=1','OK|ERROR'))

    def step4to8(test, protocol):

        test.echo_server = EchoServer("IPv4", f"{protocol}")
        client_profile = SocketProfile(test.dut, 1, test.connection_setup_dut.dstl_get_used_cid(), protocol=f"{protocol}",etx_char=26)
        client_profile.dstl_set_parameters_from_ip_server(test.echo_server)
        client_profile.dstl_generate_address()
        test.expect(client_profile.dstl_get_service().dstl_load_profile())
        test.sleep(2)
        test.expect(client_profile.dstl_get_service().dstl_open_service_profile())
        test.dut.dstl_check_urc('SISW: 1,1')
        test.sleep(2)
        data_to_send = '1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890'

        for i in range(0, 2):
            test.log.info(f'Start MT test loop {i + 1}')
            test.log.info('********loop {} *******'.format(i + 1))
            test.expect(client_profile.dstl_get_service().dstl_send_sisw_command(100))
            test.log.step("4. During step 3 try to set incoming voice call")
            test.expect(test.expect(test.r1.at1.send_and_verify(f'atd{test.dut.sim.nat_voice_nr};', expect='OK')))
            test.expect(test.dut.at2.wait_for('RING'))
            test.expect(client_profile.dstl_get_service().dstl_send_data(data_to_send))
            test.expect(test.r1.dstl_release_call())
            test.expect(test.dut.dstl_release_call())
            test.sleep(3)

        for i in range(0, 2):
            test.log.info(f'Start MO test loop {i+1}')
            test.log.info('********loop {} *******'.format(i + 1))
            test.log.step("6. During step 3, on second interface, try to initiate voice call")
            test.expect(client_profile.dstl_get_service().dstl_send_sisw_command(100))
            test.expect(test.dut.at2.send_and_verify(f'atd{test.r1.sim.nat_voice_nr};', expect='OK'))
            test.expect(test.r1.at1.wait_for('RING'))
            test.expect(client_profile.dstl_get_service().dstl_send_data(data_to_send))
            test.expect(test.r1.dstl_release_call())
            test.expect(test.dut.dstl_release_call())
            test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('at^sisc=1', expect='OK'))


if '__main__' == __name__:
    unicorn.main()
