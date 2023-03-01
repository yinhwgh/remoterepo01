#responsible: jingxin.shen@thalesgroup.com
#location: Beijing
#TC0095145.001

import unicorn
import time
import re
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import  dstl_register_to_lte
from dstl.network_service.register_to_network import  dstl_enter_pin
from dstl.status_control import sind_parameters
from dstl.status_control import extended_indicator_control
from dstl.call.setup_voice_call import dstl_release_call

'''
Case name: TC0095145.001  SIND_CEER_BasicFunction 
'''


class at_sind_ceer_basic(BaseTest):
    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        test.log.info('---------Test Begin -------------------------------------------------------------')
        test.expect(test.dut.dstl_restart())
        sind_test_response = test.dut.dstl_get_expected_sind_test_response_dict()
        test.ceer_test_response = sind_test_response['ceer']

        for iLoop in range(1, 4):
            '''
            iLoop=1:test in airplane mode
            iLoop=2:test in normal mode without pin
            iLoop=3:test in normal mode with pin
            '''
            if iLoop == 1:
                test.expect(test.dut.at1.send_and_verify('at+cfun=4', '^SYSSTART AIRPLANE MODE'))
            if iLoop == 2:
                test.expect(test.dut.at1.send_and_verify('at+cfun=1', 'OK'))
                test.expect(test.dut.at1.send_and_verify('at+cpin?', '+CPIN: SIM PIN'))
            if iLoop == 3:
                test.expect(test.dut.dstl_enter_pin())
                test.expect(test.dut.at1.send_and_verify('at+cpin?', '+CPIN: READY'))

            ''' 1.check ceer in response of at^sind'''
            test.expect(test.dut.at1.send_and_verify('at^sind=?', f',{test.ceer_test_response},'))
            test.expect(test.dut.at1.send_and_verify('at^sind=ceer,0', '^SIND: ceer,0,0'))
            test.expect(test.dut.at1.send_and_verify('at^sind?', '^SIND: ceer,0,0'))

            ''' 2.legal mode and ceerRelCauseGroup test'''
            test.expect(test.dut.at1.send_and_verify('at^sind=ceer,2', '^SIND: ceer,0,0'))

            test.expect(test.dut.at1.send_and_verify('at^sind=ceer,1', '^SIND: ceer,1,0'))
            test.expect(test.dut.at1.send_and_verify('at^sind=ceer,1,4', '^SIND: ceer,1,4'))
            test.expect(test.dut.at1.send_and_verify('at^sind=ceer,1,8', '^SIND: ceer,1,4,8'))
            test.expect(test.dut.at1.send_and_verify('at^sind=ceer,1,2', '^SIND: ceer,1,2,4,8'))
            test.expect(test.dut.at1.send_and_verify('at^sind=ceer,1,1', '^SIND: ceer,1,1,2,4,8'))
            test.expect(test.dut.at1.send_and_verify('at^sind=ceer,1,5', '^SIND: ceer,1,1,2,4,5,8'))
            test.expect(test.dut.at1.send_and_verify('at^sind=ceer,2', '^SIND: ceer,1,1,2,4,5,8'))
            test.expect(test.dut.at1.send_and_verify('at^sind=ceer,1,99', '^SIND: ceer,1,99'))

            test.expect(test.dut.at1.send_and_verify('at^sind=ceer,1,7', '^SIND: ceer,1,99'))
            test.expect(test.dut.at1.send_and_verify('at^sind=ceer,1,0', '^SIND: ceer,1,0'))
            test.expect(test.dut.at1.send_and_verify('at^sind=ceer,1,7', '^SIND: ceer,1,7'))

        ''' 3.functional test'''
        test.dut.dstl_register_to_lte()
        test.expect(test.dut.at1.send_and_verify('at^sind=ceer,0', '^SIND: ceer,0,0'))
        test.expect(test.dut.at1.send_and_verify('at^sind=ceer,1,99', '^SIND: ceer,1,99'))
        activated = test.expect(test.dut.at1.send_and_verify('at+cgact?', '\+CGACT: 1,\d+'))
        if activated:
            activated_cids = re.findall('\+CGACT: (\d+),1', test.dut.at1.last_response)
            activated_cid = activated_cids[-1]
        else:
            activated_cid = 1
        # test.expect(test.dut.at1.send_and_verify(f'at+cgact=0,{activated_cid}', '\+CIEV: ceer,4,"PDP lowerlayer error"'))
        # Since 'ceer,4,"PDP lowerlayer error"' cannot return for every SIM provider, change to call
        test.expect(test.dut.at1.send_and_verify(f"ATD{test.dut.sim.nat_voice_nr};", "OK"))
        test.expect(test.dut.dstl_release_call())
        test.expect(test.dut.at1.wait_for('\+CIEV: ceer,1,"Client ended call"', append=True))
        test.expect(test.dut.at1.send_and_verify('at^sind=ceer,0', '^SIND: ceer,0,0'))
        test.log.info("If PDP status is not changed, CIEV: ceer .* URC should not display.")
        if test.dut.at1.send_and_verify("AT+CGACT=0,{activated_cid}", "OK"):
            test.expect(test.dut.at1.send_and_verify(f'at+cgact=0,{activated_cid}',
                                                     '+CME ERROR: unknown'))
        test.expect(not test.dut.at1.wait_for(".*CIEV: ceer,.*", append=True),
                    msg="No ceer urc should return")

        ''' 4.illegal mode and ceerRelCauseGroup test'''
        mode = [0, 1, 2]
        ceerRelCauseGroup = test.get_valid_ceer_release_group_value()

        i = 0
        while (i <= 100):
            if (i in mode):
                test.expect(test.dut.at1.send_and_verify('at^sind=ceer,' + str(i), 'OK'))
            else:
                test.expect(test.dut.at1.send_and_verify('at^sind=ceer,' + str(i), '+CME ERROR: invalid index'))

            if (i in ceerRelCauseGroup):
                test.expect(test.dut.at1.send_and_verify('at^sind=ceer,1,' + str(i), 'OK'))
            else:
                test.expect(test.dut.at1.send_and_verify('at^sind=ceer,1,' + str(i), '+CME ERROR: invalid index'))

            test.expect(test.dut.at1.send_and_verify('at^sind=ceer,0,' + str(i), '+CME ERROR: invalid index'))
            test.expect(test.dut.at1.send_and_verify('at^sind=ceer,2,' + str(i), '+CME ERROR: invalid index'))
            i = i + 1

        illegal = ['*', 'a', '-1', '#', '^', '+']
        for param in illegal:
            test.expect(test.dut.at1.send_and_verify('at^sind=ceer,' + param, '+CME ERROR: invalid index'))
            if not test.expect(test.dut.at1.send_and_verify('at^sind=ceer,1,' + param, '+CME ERROR: invalid index')):
                test.log.error("For Viper, failure is caused by not to fix IPIS100334874.")

        test.log.info('---------Test End -------------------------------------------------------------')

    def cleanup(test):
        test.expect(test.dut.dstl_disable_one_indicator("ceer"))

    def get_valid_ceer_release_group_value(test):
        ceerRelCauseGroup = []
        value_ranges = re.findall('(\d+\-\d+)', test.ceer_test_response)
        if value_ranges:
            for group in value_ranges:
                numbers = group.split('-')
                ceerRelCauseGroup += range(int(numbers[0]), int(numbers[-1]) + 1)
        single_value = re.findall(',(\d+)[^-]', test.ceer_test_response)
        if single_value:
            ceerRelCauseGroup += [int(n) for n in single_value]
        test.log.info(f"Valid values for ceerRelCauseGroup are {ceerRelCauseGroup}.")
        return ceerRelCauseGroup




if (__name__ == '__main__'):
    unicorn.main()
