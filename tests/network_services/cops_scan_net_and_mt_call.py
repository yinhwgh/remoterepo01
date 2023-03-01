#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0093042.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init

class Test(BaseTest):
    '''
    TC0093042.001 - TpCCopsScanNetAndMtCall
    Subscriber :2
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(3)

    def run(test):
        test.r1.dstl_register_to_network()

        test.log.info('1. For RAT=GSM and network scanning occur MT Voice Call')
        result2g = test.dut.dstl_register_to_gsm()
        test.sleep(3)
        if result2g:
            test.function_check()

        else:
            test.log.error('Register error, please check network condition')
            test.expect(False)


        test.log.info('2. For RAT=UTRAN and network scanning occur MT Voice Call')
        result3g = test.dut.dstl_register_to_umts()
        test.sleep(3)
        if result3g:
            test.function_check()

        else:
            test.log.error('Register error, please check network condition')
            test.expect(False)


    def cleanup(test):
        pass

    def function_check(test):
        test.dut.at1.send('at+cops=?')
        test.sleep(3)
        test.r1.at1.send_and_verify(f'atd{test.dut.sim.nat_voice_nr};')

        test.expect(test.dut.at1.wait_for('RING'))
        test.dut.at1.send_and_verify('ath')
        test.expect(test.r1.at1.wait_for('NO CARRIER'))



if "__main__" == __name__:
    unicorn.main()
