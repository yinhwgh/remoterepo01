#author: hui.yu@thalesgroup.com
#location: Dalian
#TC0084443.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module
from dstl.auxiliary import check_urc

class Test(BaseTest):
    def setup(test):
        test.dut.dstl_detect()
        pass

    def run(test):
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify('at+cpin?', expect='+CPIN: READY'))
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify('at+cops=0', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CSSN=?', expect='+CSSN: (0-1),(0-1)'))
        test.expect(test.dut.at1.send_and_verify('AT+CSSN=1,1', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=0,2', expect='+CCFC: 0,1'))
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CSSN=0,0', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CSSN?', expect='+CSSN: 0,0'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=0,2', expect='+CCFC: 0,1'))
        test.expect(test.dut.at1.send_and_verify('AT+CHLD=3', expect='+CME ERROR: unknown'))
        test.expect(test.dut.at1.send_and_verify('AT+CPIN="1234"', expect='+CME ERROR: SIM PUK2 required'))

        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify('at+cpin?', expect='+CPIN: READY'))
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify('at+cops=0', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CHLD=3', expect='+CME ERROR: unknown'))
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+cpin?', expect='+CPIN: READY'))
        test.expect(test.dut.at1.send_and_verify('AT+CHLD=3', expect='+CME ERROR: unknown'))
        test.expect(test.dut.at1.send_and_verify('AT+CHLD=0', expect='+CME ERROR: unknown'))
        test.expect(test.dut.at1.send_and_verify('AT+CHLD=1', expect='+CME ERROR: unknown'))
        test.expect(test.dut.at1.send_and_verify('AT+CHLD=2', expect='+CME ERROR: unknown'))
        #IPIS100324982
        #test.expect(test.dut.at1.send_and_verify('ATd>13700096438;', expect='+CME ERROR: invalid index'))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify('atd13700096438;', expect='OK'))
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify('ath', expect='OK'))
        test.sleep(15)
        test.r1.at1.send(f"ATD{test.dut.sim.int_voice_nr};")
        test.expect(test.dut.dstl_check_urc('RING'))
        test.expect(test.dut.at1.send_and_verify('AT+CHLD=1', expect='+CME ERROR: unknown'))
        test.expect(test.dut.at1.send_and_verify('AT+CHLD=2', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CHLD=3', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('ATD10086;', expect='OK'))
        test.sleep(15)
        test.expect(test.dut.at1.send_and_verify('ATH', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CCWA=2', expect='+CME ERROR: invalid index'))
        test.expect(test.dut.at1.send_and_verify('AT+CCWA=2', expect='+CME ERROR: invalid index'))
        test.r1.at1.send(f"ATD{test.dut.sim.int_voice_nr};")
        test.sleep(10)
        test.expect(test.dut.dstl_check_urc('RING'))
        test.expect(test.dut.at1.send_and_verify('AT+CCWA=2', expect='+CME ERROR: invalid index'))
        test.sleep(45)
        test.r1.at1.send(f"ATD{test.dut.sim.int_voice_nr};")
        test.expect(test.dut.dstl_check_urc('RING'))
        test.expect(test.dut.at1.send_and_verify('at+ccwa=1,1,1', expect='OK'))
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify('atd10086;', expect='OK'))
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify('AT+CHLD=2', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('ATH', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CSSN', expect='+CME ERROR: unknown'))
        test.expect(test.dut.at1.send_and_verify('AT+CSSN=1,1', expect='OK'))

    def cleanup(test):
        pass

if '__main__' == __name__:
    unicorn.main()
