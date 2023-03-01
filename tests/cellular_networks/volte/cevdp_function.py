#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0105069.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call import setup_voice_call
from dstl.auxiliary import restart_module
from dstl.call import enable_voice_call_with_ims

class Test(BaseTest):

    def setup(test):

        test.dut.detect()
        test.dut.dstl_restart()
        test.r1_nat_num = test.r1.sim.nat_voice_nr
        test.dut.dstl_register_to_network()
        test.r1.dstl_register_to_network()
        test.sleep(5)

    def run(test):
        test.dut.dstl_enable_voice_call_with_ims(manually_register_to_lte=False)

        test.log.step('1.Check that VoLTE is enabled by default')
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', 'OK'))
        test.log.step('2. Check voice domain preference setting - CS Voice only.')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=1', 'OK'))
        test.sleep(3)
        test.expect(test.dut.dstl_voice_call_by_number(test.r1,test.r1_nat_num))
        test.sleep(2)
        test.check_is_vlote(expect=False)
        test.expect(test.dut.dstl_release_call())
        test.expect(test.r1.dstl_release_call())
        test.sleep(10)
        test.log.step('3. Check voice domain preference setting - CS Voice preferred, IMS PS Voice as secondary.')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=2', 'OK'))
        test.sleep(3)
        test.expect(test.dut.dstl_voice_call_by_number(test.r1, test.r1_nat_num))
        test.sleep(2)
        test.check_is_vlote(expect=False)
        test.expect(test.dut.dstl_release_call())
        test.expect(test.r1.dstl_release_call())
        test.sleep(10)
        test.log.step('4. Check voice domain preference setting - IMS PS Voice preferred, CS Voice as secondary.')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=3', 'OK'))
        test.sleep(3)
        test.expect(test.dut.dstl_voice_call_by_number(test.r1, test.r1_nat_num))
        test.sleep(3)
        test.check_is_vlote()
        test.expect(test.dut.dstl_release_call())
        test.expect(test.r1.dstl_release_call())
        test.sleep(10)
        test.log.step('5. Check voice domain preference setting - IMS PS Voice only.')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=4', 'OK'))
        test.sleep(3)
        test.expect(test.dut.dstl_voice_call_by_number(test.r1, test.r1_nat_num))
        test.sleep(2)
        test.check_is_vlote()
        test.expect(test.dut.dstl_release_call())
        test.expect(test.r1.dstl_release_call())

        test.log.step('6. Change back to the default setting.')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=3', 'OK'))


    def check_is_vlote(test, expect = True):
        if expect == True:
            test.expect(test.dut.at1.send_and_verify('at^smoni', 'SMONI: 4G'))
        else:
            test.expect(test.dut.at1.send_and_verify('at^smoni', '2G|3G'))


    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()