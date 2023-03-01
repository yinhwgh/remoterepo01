#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0105160.002

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module
from dstl.auxiliary.init import dstl_detect
from dstl.call import setup_voice_call

class Test(BaseTest):
    '''
    TC0105160.002 - sind_dtmf_sleep_mode
    Test case to check TDMF URC should be stored in buffer in sleep mode,
    and release when module exist sleep mode
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.r1.dstl_register_to_network())

    def run(test):
        try:
            test.dut.usb_m.send_and_verify('at', 'OK')
        except:
            test.expect(False, critical=True, msg='usb_m port not connect, stop run this tc')
        test.log.step('1. Enable DTMF sind URCon DUT')
        test.expect(test.dut.at1.send_and_verify('AT^SIND="dtmf",1', 'SIND: dtmf,1,1'))
        test.log.step('2. Make an on-going call from DUT to remote, remote answer the call')
        nat_r1_phone_num = test.r1.sim.nat_voice_nr
        test.dut.dstl_voice_call_by_number(test.r1, nat_r1_phone_num)
        test.log.step('3. Make DUT enter sleep mode')
        test.dut.at1.send_and_verify('AT^SPOW=2,1000,3', 'OK')
        test.log.step('4. In remote side, generate TDMF tone by at+vts=0')
        test.expect(test.r1.at1.send_and_verify('AT+VTS="0"', 'OK'))
        test.log.step('5. Verify on DUT side no URC popup')
        test.sleep(5)
        test.dut.at1.read()
        test.log.step('6. Make DUT exist sleep mode')
        test.expect(test.dut.usb_m.send_and_verify('AT^SPOW=1,0,0', 'OK'))
        test.sleep(5)
        test.log.step('7. Verify DTMF URC popup as below:')
        test.expect(test.r1.at1.send_and_verify('AT+VTS="0"', 'OK'))
        port_output = test.dut.at1.read()
        test.expect('CIEV: dtmf,"0",1' in port_output)

    def cleanup(test):
        test.dut.dstl_release_call()
        test.r1.dstl_release_call()

if __name__=='__main__':
    unicorn.main()
