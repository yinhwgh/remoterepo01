# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0091789.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init


class Test(BaseTest):
    '''
    TC0091789.001 - TpAtClckBasic
    Intention:
    This procedure provides the possibility of basic tests  for the test and write command of +CLCK.
    Subscriber: 1
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(10)

    def run(test):
        test.log.info('1. test without pin')
        test.expect(test.dut.at1.send_and_verify('at+cpin?', 'SIM PIN'))
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+cmee?', 'CMEE: 2'))
        test.expect(test.dut.at1.send_and_verify('at+clck=?', 'ERROR'))

        test.log.info('2. test with pin')
        test.dut.dstl_enter_pin()
        test.expect(test.dut.at1.send_and_verify('at+cpin?', 'READY'))
        test.expect(test.dut.at1.send_and_verify('at+clck=?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+clck?', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+clck', 'ERROR'))

        test.log.info('3. check all parameters and also with invalid values')
        test.expect(test.dut.at1.send_and_verify('at+clck?', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+clck', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+clck=\"XX\",2', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+clck=\"SC\",3', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+clck=\"SC\",0', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+clck=\"PN\",1', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+clck=\"PN\",0', 'ERROR|OK'))
        test.expect(test.dut.at1.send_and_verify('at+clck=\"PS\",0', 'ERROR'))

        test.log.info('4. check functionality')
        simpin1 = test.dut.sim.pin1
        test.expect(test.dut.at1.send_and_verify('at+clck=\"SC\",2','CLCK:\s*1'))
        test.expect(test.dut.at1.send_and_verify('at+clck=\"SC\",0,\"{}\"'.format(simpin1)))
        test.expect(test.dut.at1.send_and_verify('at+clck=\"SC\",2','CLCK:\s*0'))

        test.expect(test.dut.at1.send_and_verify('at+clck=\"SC\",1,\"{}\"'.format(simpin1)))
        test.expect(test.dut.at1.send_and_verify('at+clck=\"SC\",2','CLCK:\s*1'))







    def cleanup(test):
        test.log.info('***Test End, clean up***')



if "__main__" == __name__:
    unicorn.main()
