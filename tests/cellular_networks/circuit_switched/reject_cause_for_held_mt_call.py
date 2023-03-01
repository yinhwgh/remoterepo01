#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0083761.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call import setup_voice_call
from dstl.call import get_release_cause

class Test(BaseTest):

    '''
    TC0083761.001 - RejectionCauseForHeldMTCall
    Intention: Disconnect all held calls with AT^SHUP with different rejection causes.
    Subscriber: 3
    Equipment:Need r1 and r1 support at+ceer Extended Error Report.
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.dut.dstl_register_to_network()
        test.r1.dstl_detect()
        test.r1.dstl_restart()
        test.sleep(3)
        test.r1.dstl_register_to_network()
        test.r2.dstl_detect()
        test.r2.dstl_restart()
        test.sleep(3)
        test.r2.dstl_register_to_network()
        test.sleep(10)

    def run(test):

        test.expect(test.dut.at1.send_and_verify('AT+CCWA=1,1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CCWA=1,2', 'CCWA: 1,1'))

        support_cause =test.dut.dstl_get_supported_release_cause()

        if test.dut.dstl_is_gsm_supported():
           if test.dut.dstl_register_to_gsm():
               test.log.info('Test under 2G network')
               for cause in support_cause:
                   test.check_release_cause(cause)
           else:
                test.log.error('Register to 2G network fail')
                test.expect(False)

        if test.dut.dstl_is_umts_supported():
            if test.dut.dstl_register_to_umts():
                test.log.info('Test under 3G network')
                for cause in support_cause:
                    test.check_release_cause(cause)
            else:
                test.log.error('Register to 3G network fail')
                test.expect(False)

        if test.dut.dstl_is_lte_supported():
            if test.dut.dstl_register_to_lte():
                test.log.info('Test under 4G network')
                for cause in support_cause:
                    test.check_release_cause(cause)
            else:
                test.log.error('Register to 4G network fail')
                test.expect(False)


    def cleanup(test):
       test.log.info('***Test End***')
       test.expect(test.dut.at1.send_and_verify('AT+CCWA=0,0', 'OK'))
       test.expect(test.dut.at1.send_and_verify('AT&F', 'OK'))
       test.expect(test.r1.at1.send_and_verify('AT&F', 'OK'))
       test.expect(test.r2.at1.send_and_verify('AT&F', 'OK'))

    def check_release_cause(test, cause):
        nat_dut_phone_num = test.dut.sim.nat_voice_nr
        nat_r1_phone_num = test.r1.sim.nat_voice_nr
        shup_cause={1:'.*Unassigned \\(unallocated\\) number.*|.*Unassigned/unallocated number.*',
                    16:'.*normal call clearing.*|.*Normal call clearing.*',
                    17:'.*User busy.*',
                    18:'.*No user responding.*',
                    21:'.*Call rejected.*',
                    27:'.*Destination out of order.*',
                    31:'.*Normal, unspecified.*',
                    88:'.*incompatible destination.*|.*Incompatible destination.*',
                    128:'.*Normal call clearing.*|.*Call rejected.*'}
        exp_clcc_1 = '.*\+CLCC:\s*1,0,0,0,0.*\+CLCC:\s*2,1,5,0,0.*OK.*|.*\+CLCC:\s*2,1,5,0,0.*\+CLCC:\s*1,0,0,0,0.*OK.*'
        exp_clcc_2 = '.*\+CLCC:\s*1,0,1,0,0.*\+CLCC:\s*2,1,0,0,0.*OK.*|.*\+CLCC:\s*2,1,0,0,0.*\+CLCC:\s*1,0,1,0,0.*OK.*'
        exp_clcc_3 = '.*\+CLCC:\s*2,1,0,0,0.*OK.*'
        test.log.info(f'*** Start test cause {cause} ***')
        # dut setup call to r1
        test.expect(test.dut.at1.send_and_verify(f'atd{nat_r1_phone_num};', ''))
        test.expect(test.r1.at1.wait_for('RING'))
        test.expect(test.r1.at1.send_and_verify('ATA', 'OK'))
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify('at+clcc', '.*\+CLCC:\s*1,0,0,0,0.*'))
        #r2 setup call to dut
        test.expect(test.r2.at1.send_and_verify(f'atd{nat_dut_phone_num};', ''))
        test.expect(test.dut.at1.wait_for('.*\+CCWA:.*'))
        test.expect(test.dut.at1.send_and_verify('at+clcc', exp_clcc_1))
        test.expect(test.dut.at1.send_and_verify('AT+CHLD=2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+clcc', exp_clcc_2))
        #release first call
        test.expect(test.dut.at1.send_and_verify(f'AT^SHUP={cause},1', 'OK'))
        test.expect(test.r1.at1.wait_for('BUSY|NO CARRIER'))
        test.sleep(2)
        test.expect(test.r1.at1.send_and_verify('AT+CEER', '.*\+CEER: ' + shup_cause[cause] + '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+clcc', exp_clcc_3))
        #release second call
        test.expect(test.dut.at1.send_and_verify(f'AT^SHUP={cause},2', 'OK'))
        test.expect(test.r2.at1.wait_for('BUSY|NO CARRIER'))
        test.sleep(2)
        test.expect(test.r2.at1.send_and_verify('AT+CEER', '.*\+CEER: ' + shup_cause[cause] + '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+clcc', '\+clcc\s+OK'))
        test.dut.dstl_release_call()
        test.r1.dstl_release_call()
        test.r2.dstl_release_call()


if "__main__" == __name__:
    unicorn.main()

