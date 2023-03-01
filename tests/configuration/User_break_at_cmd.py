#responsible: feng.han@thalesgroup.com
#location: Dalian
#TC0087865.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import restart_module
from dstl.sms import sms_functions
from dstl.sms import sms_center_address
from dstl.sms import select_sms_format
from dstl.network_service import register_to_network
from dstl.auxiliary import check_urc

class Test(BaseTest):
    '''
        TC0087865.001 -  UserBreakAtCmd
        The goal of this test case is to verify the "user break" mechanism when interactions with the network are involved or for long running AT commands.
        Subscriber: 2
        '''
    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.expect(test.r1.dstl_enter_pin())

    def run(test):
        test.expect(test.dut.at1.send_and_verify('atd*43*11#;', expect='', wait_for=''))
        test.expect(test.dut.at1.send_and_verify('at', expect='OK'))
        test.expect(test.r1.at1.send_and_verify(f'atd{test.dut.sim.nat_voice_nr};', expect='OK'))
        test.expect(test.dut.dstl_check_urc('RING'))
        test.expect(test.dut.at1.send_and_verify('ata', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+clcc', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('ath', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+cops=?', expect='', wait_for='', wait_after_send=5))
        test.expect(test.dut.at1.send_and_verify('at', expect='\+CME ERROR: unknown'))
        test.expect(test.dut.at1.send_and_verify('AT+COPN', expect='', wait_for='', wait_after_send=2))
        test.expect(test.dut.at1.send_and_verify('at', expect='\+CME ERROR: unknown'))
        test.expect(test.dut.at1.send_and_verify('AT+CPOL?', expect='\+CPOL:.*'))
        test.expect(test.dut.at1.send_and_verify('at', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CLCK=?', expect='', wait_for=''))
        test.expect(test.dut.at1.send_and_verify('at', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CLIP?', expect='', wait_for=''))
        test.expect(test.dut.at1.send_and_verify('at', expect='\+CME ERROR: unknown'))
        test.expect(test.dut.at1.send_and_verify('AT+CLIR?', expect='', wait_for=''))
        test.expect(test.dut.at1.send_and_verify('at', expect='\+CME ERROR: unknown'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=0,2', expect='', wait_for=''))
        test.expect(test.dut.at1.send_and_verify('at', expect='\+CME ERROR: unknown'))
        test.expect(test.dut.at1.send_and_verify('at+ccwa=1,2', expect='', wait_for=''))
        test.expect(test.dut.at1.send_and_verify('at', expect='\+CME ERROR: unknown'))
        test.expect(test.r1.at1.send_and_verify(f'atd{test.dut.sim.nat_voice_nr};', expect='OK'))
        test.expect(test.dut.dstl_check_urc('RING'))
        test.expect(test.dut.at1.send_and_verify('at+chld=11', expect='', wait_for=''))
        test.expect(test.dut.at1.send_and_verify('at', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+cusd=1', expect='', wait_for=''))
        test.expect(test.dut.at1.send_and_verify('at', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+cmgf=1', expect='OK'))
        test.expect(test.dut.dstl_send_sms_message(destination_addr=test.dut.sim.nat_voice_nr, sms_text="1234567890"))
        test.expect(test.dut.at1.send_and_verify('at', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+cgatt=0', expect='', wait_for=''))
        test.expect(test.dut.at1.send_and_verify('at', expect='\+CME ERROR: unknown'))
        test.expect(test.dut.at1.send_and_verify('at+cgatt=1', expect='', wait_for=''))
        test.expect(test.dut.at1.send_and_verify('at', expect='\+CME ERROR: unknown'))
        test.expect(test.dut.at1.send_and_verify('at+cgdcont=6,"IPV4V6","cmcc"', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+cgact=1,6', expect='', wait_for=''))
        test.expect(test.dut.at1.send_and_verify('at', expect='\+CME ERROR: unknown'))

    def cleanup(test):
        test.expect(test.dut.dstl_restart())


if '__main__' == __name__:
    unicorn.main()
