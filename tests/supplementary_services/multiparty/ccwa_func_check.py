#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0084441.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call import setup_voice_call

class Test(BaseTest):
    '''
    TC0084441.001 - TpCccwaFunc
    Ccwa functional test.
    Subscriber: 3
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.r2.dstl_detect()
        test.dut.dstl_restart()
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.r1.dstl_register_to_network())
        test.expect(test.r2.dstl_register_to_network())
        test.sleep(3)

        test.int_dut_phone_num = test.dut.sim.int_voice_nr
        test.int_r1_phone_num = test.r1.sim.int_voice_nr
        test.nat_r2_phone_num = test.r2.sim.nat_voice_nr

    def run(test):
        test.log.info('Start test ccwa for class 1')
        test.check_ccwa_func_class(1)
        test.log.info('Start test ccwa for class 255')
        test.check_ccwa_func_class(255)

    def cleanup(test):
        pass


    def check_ccwa_func_class(test, classes):
        test.expect(test.dut.at1.send_and_verify('at+CCFC=4,0', 'OK|ERROR'))

        test.set_and_query_ccwa(classes, 1)
        test.expect(test.dut.dstl_voice_call_by_number(test.r1, test.int_r1_phone_num))
        test.expect(test.r2.at1.send_and_verify(f'ATD{test.int_dut_phone_num};','.*'))
        test.expect(test.dut.at1.wait_for(f".*\+CCWA:.*{test.nat_r2_phone_num}.*"))
        test.expect(test.r2.dstl_release_call())
        test.expect(test.r1.dstl_release_call())
        test.expect(test.dut.dstl_release_call())

        test.set_and_query_ccwa(classes, 0)

    def set_and_query_ccwa(test, classes, mode):
        if mode == 0:
            test.expect(test.dut.at1.send_and_verify(f'AT+CCWA=0,0,{classes}', '.*OK.*'))
            test.expect(test.dut.at1.send_and_verify(f'AT+CCWA=1,2,{classes}', '.*CCWA: 0,1.*OK.*|.*CCWA: 0,255.*OK.*'))
        else:
            test.expect(test.dut.at1.send_and_verify(f'AT+CCWA=1,1,{classes}', '.*OK.*'))
            test.expect(test.dut.at1.send_and_verify(f'AT+CCWA=1,2,{classes}', '.*CCWA: 1,1.*OK.*'))



if "__main__" == __name__:
    unicorn.main()

