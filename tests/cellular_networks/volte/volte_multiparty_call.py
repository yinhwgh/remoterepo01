#author: liu.xiaolin@thalesgroup.com
#location: Dalian
#TC0094828.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.auxiliary import check_urc
from dstl.call import enable_voice_call_with_ims
from dstl.call import setup_voice_call

class Test(BaseTest):
    '''
    TC0094828.001 - VolteMultipartyCall
    Intention: Coverage of IPIS100180465
             This test case is to check if Multiparty functionality works during VoLTE call.
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_register_to_lte())
        test.r1.dstl_detect()
        test.expect(test.r1.dstl_register_to_network())
        test.r2.dstl_detect()
        test.expect(test.r2.dstl_register_to_network())

    def run(test):
        r1_nat_number = test.r1.sim.nat_voice_nr
        test.dut.dstl_enable_voice_call_with_ims()
        test.expect(test.dut.at1.send_and_verify('AT+CREG=2', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CCWA=1,1,1', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SLCC=1', expect='.*OK.*'))
        test.log.step('1. Establish outgoing voice call')
        test.dut.at1.send(f"ATD{test.r1.sim.int_voice_nr};")
        test.expect(test.dut.at1.wait_for('\^SLCC: 1,0,3,0,0,0.*'))
        test.expect(test.r1.at1.wait_for("RING"))
        test.expect(test.dut.at1.send_and_verify('AT+CLCC', expect='\+CLCC: 1,0,3,0,0.*OK.*'))
        test.expect(test.r1.at1.send_and_verify('ATA', expect='.*OK.*'))
        test.expect(test.dut.at1.wait_for('\^SLCC: 1,0,0,0,0,0.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CLCC', expect='\+CLCC: 1,0,0,0,0.*OK.*'))
        test.log.step('2. Call from second module to the tested device')
        test.r2.at1.send(f"ATD{test.dut.sim.int_voice_nr};")
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify('AT^SLCC', expect='\^SLCC: 1,0,0,0,0,0.*\^SLCC: 2,1,5,0,0,0.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CLCC', expect='\+CLCC: 1,0,0,0,0.*\+CLCC: 2,1,5,0,0.*OK.*'))
        test.log.step('3. Place all active calls on hold (if any) and accept "the other call" as the active call: AT+CHLD=2')
        test.expect(test.dut.at1.send_and_verify('AT+CHLD=2', expect='.*OK.*'))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify('AT^SLCC', expect='\^SLCC: 1,0,1,0,0,0.*\^SLCC: 2,1,0,0,0,0.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CLCC', expect='\+CLCC: 1,0,1,0,0.*\+CLCC: 2,1,0,0,0.*OK.*'))
        test.log.step('4. Set up a conference AT+CHLD=3')
        test.expect(test.dut.at1.send_and_verify('AT+CHLD=3', expect='.*OK.*'))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify('AT^SLCC', expect='\^SLCC: 1,0,0,0,1,0.*\^SLCC: 2,1,0,0,1,0.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CLCC', expect='\+CLCC: 1,0,0,0,1.*\+CLCC: 2,1,0,0,1.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CAVIMS?', expect='\+CAVIMS: 1'))
        test.expect(test.dut.at1.send_and_verify('AT+CHLD=9', expect='.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SHUP16,9', expect='.*ERROR.*'))


    def cleanup(test):
        test.dut.dstl_release_call()
        test.r1.dstl_release_call()
        test.r2.dstl_release_call()
        test.expect(test.dut.at1.send_and_verify('AT&F', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT&W', expect='.*OK.*'))


if '__main__' == __name__:
    unicorn.main()
