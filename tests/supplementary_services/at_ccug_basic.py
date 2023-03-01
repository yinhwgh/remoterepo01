#author: liu.xiaolin@thalesgroup.com
#location: Dalian
#TC0095132.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode, dstl_set_airplane_mode

class Test(BaseTest):
    """Intention:
    Checks basic settings of AT+CCUG."""

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='OK'))

    def run(test):
        test.log.step('1. Check command without PIN.')
        test.expect(test.dut.at1.send_and_verify('AT+CPIN?', expect='\+CPIN: SIM PIN'))
        test.expect(test.dut.at1.send_and_verify('AT+CCUG=?', expect='\+CME ERROR: SIM PIN required'))
        test.expect(test.dut.at1.send_and_verify('AT+CCUG?', expect='\+CME ERROR: SIM PIN required'))
        test.expect(test.dut.at1.send_and_verify('AT+CCUG', expect='ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT+CCUG=1,10,1', expect='\+CME ERROR: SIM PIN required'))
        test.log.step('2. Check command with pin.')
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('AT+CCUG=?', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CCUG?', expect='\+CCUG: 0,0,0'))
        test.expect(test.dut.at1.send_and_verify('AT+CCUG=1,10,1', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CCUG?', expect='\+CCUG: 1,10,1'))
        test.log.step('3. Check other valid parameters for write command and check status.')
        test.expect(test.dut.at1.send_and_verify('AT+CCUG=0,0,0', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CCUG?', expect='\+CCUG: 0,0,0'))
        test.expect(test.dut.at1.send_and_verify('AT+CCUG=1,10,3', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CCUG?', expect='\+CCUG: 1,10,3'))
        test.expect(test.dut.at1.send_and_verify('AT+CCUG=0,9,2', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CCUG?', expect='\+CCUG: 0,9,2'))
        test.log.step('4. Check for invalid parameters.')
        test.expect(test.dut.at1.send_and_verify('AT+CCUG=3,9,2', expect='ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT+CCUG=1,11,2', expect='ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT+CCUG=1,10,4', expect='ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT+CCUG=*1,10,1', expect='ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT+CCUG=1,1*0,1', expect='ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT+CCUG=1,10,*1', expect='ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT+CCUG=a', expect='ERROR'))
        test.log.step('5. Check command with Airplane mode.')
        test.dut.dstl_set_airplane_mode()
        test.expect(test.dut.at1.send_and_verify('AT+CCUG=?', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CCUG?', expect='\+CCUG: 0,9,2'))
        test.expect(test.dut.at1.send_and_verify('AT+CCUG=1,10,1', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CCUG?', expect='\+CCUG: 1,10,1'))
        test.expect(test.dut.at1.send_and_verify('AT+CCUG=1,10,2', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CCUG?', expect='\+CCUG: 1,10,2'))
        test.expect(test.dut.at1.send_and_verify('AT+CCUG=3,9,2', expect='ERROR'))

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('AT&F', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT&W', expect='OK'))
        test.dut.dstl_set_full_functionality_mode()


if '__main__' == __name__:
    unicorn.main()
