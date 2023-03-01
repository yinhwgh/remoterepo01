#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0091810.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call import setup_voice_call

class Test(BaseTest):
    '''
    TC0091810.001 - TpAtCssnBasic
    Intention: This procedure provides the possibility of basic tests for the test and write command of +CSSN.
    Subscriber: 2
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(3)

    def run(test):
        int_dut_phone_num = test.r1.sim.int_voice_nr

        test.log.step('1. Check command without PIN.')
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+cpin?', 'SIM PIN'))
        test.expect(test.dut.at1.send_and_verify('AT+CSSN=?', '\+CME ERROR: SIM PIN required'))
        test.expect(test.dut.at1.send_and_verify('AT+CSSN?', '\+CME ERROR: SIM PIN required'))
        test.expect(test.dut.at1.send_and_verify('AT+CSSN=1,1', '\+CME ERROR: SIM PIN required'))

        test.log.step('2. Check command with PIN.')
        test.dut.dstl_enter_pin()
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify('AT+CSSN=?', '.*\\+CSSN: \\(0-1\\),\\(0-1\\).*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CSSN=0', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CSSN?', '.*\\+CSSN: 0,0.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CSSN=', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CSSN?', '.*\\+CSSN: 0,0.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CSSN=1,1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CSSN?', '.*\\+CSSN: 1,1.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CSSN=0,1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CSSN?', '.*\\+CSSN: 0,1.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CSSN=1,0', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CSSN?', '.*\\+CSSN: 1,0.*OK.*'))

        test.log.step('3. Check invalid values.')
        test.expect(test.dut.at1.send_and_verify('AT+CSSN=-1,0', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CSSN=0,-1', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CSSN=2,0', '.*ERROR.*'))


    def cleanup(test):
        pass



if "__main__" == __name__:
    unicorn.main()

