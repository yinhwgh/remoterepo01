# author: wen.liu@thalesgroup.com
# location: Dalian
# TC0088239.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.call import setup_voice_call


class Test(BaseTest):
    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(5)
        test.r1.dstl_restart()
        test.sleep(5)
        test.r1.dstl_register_to_network()
        pass

    def run(test):
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='OK'))
        test.log.step("1. Test/Write command without PIN")
        test.expect(test.dut.at1.send_and_verify('at+cpin?', expect='\+CPIN: SIM PIN\s+OK'))
        test.expect(test.dut.at1.send_and_verify('at+vts=?', expect='\+VTS: \(0-9,#,\*,A-D\),\(1-255\)\s+OK'))
        test.expect(test.dut.at1.send_and_verify('at+vts="0",3', expect='\+CME ERROR: operation.*not allowed'))
        test.log.step("2. Test/Write command with PIN")
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.dut.at1.send_and_verify('at+vts=?', expect='\+VTS: \(0-9,#,\*,A-D\),\(1-255\)\s+OK'))
        test.expect(test.dut.at1.send_and_verify('at+vts="0",3', expect='\+CME ERROR: operation.*not allowed'))
        test.log.step("3. Check execute command during dialing")
        r1_phone_num = test.r1.sim.int_voice_nr
        test.expect(test.dut.at1.send_and_verify('atd{};'.format(r1_phone_num), '', ''))
        test.expect(test.r1.at1.wait_for('RING'))
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('at+vts="0"', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+vts="1",5', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+vts="#",5', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+vts="A"', expect='OK'))
        test.log.step("4. Check execute command during calling")
        test.expect(test.r1.at1.send_and_verify('ata', expect='OK'))
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('at+clcc', '.*CLCC: 1,0,0,0,0.*OK.*'))
        dtmf = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '#', '*', 'A', 'B', 'C', 'D'}
        for set_dtmf in dtmf:
            test.expect(test.dut.at1.send_and_verify(f'at+vts="{set_dtmf}"', expect='OK'))
            test.expect(test.dut.at1.send_and_verify(f'at+vts="{set_dtmf}",5', expect='OK'))
            test.expect(test.dut.at1.send_and_verify(f'at+vts="{set_dtmf}",255', expect='OK', timeout=30))

        test.log.step("5. Negative test")
        test.expect(test.dut.at1.send_and_verify('at+vts="1",256', expect='ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+vts="11",5', expect='ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+vts="K",5', expect='ERROR'))
        # check without quotes, AT-Spec: the string must be enclosed in quotation marks ("...").
        test.expect(test.dut.at1.send_and_verify('at+vts=0,5', expect='ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+vts="1",-1', expect='ERROR'))
        pass

    def cleanup(test):
        test.expect(test.dut.dstl_release_call())


if '__main__' == __name__:
    unicorn.main()
