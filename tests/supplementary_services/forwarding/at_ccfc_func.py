# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0088317.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call import setup_voice_call


class Test(BaseTest):
    """
    TC0088317.001 - TpAtCcfcFunc
    Intention: This procedure provides functional tests for AT+CCFC (call forwarding).
    Subscriber: 3
    """

    exp_resp_clear_all_cf = "OK"

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
        test.int_r2_phone_num = test.r2.sim.int_voice_nr

        global exp_resp_clear_all_cf
        if test.dut.platform == 'XGOLD':
            exp_resp_clear_all_cf = '\+CME ERROR: (132|service option not supported)'
            # clearing is performed, but blocked for some classes which are not supported
        pass

    def run(test):
        test.expect(test.dut.at1.send_and_verify('AT+CMEE=1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CSSN=1,1', 'OK'))
        test.expect(test.r1.at1.send_and_verify('AT+CSSN=1,1', 'OK'))
        test.expect(test.r2.at1.send_and_verify('AT+CSSN=1,1', 'OK'))
        global exp_resp_clear_all_cf
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=4,4', exp_resp_clear_all_cf))

        for i in range(0, 6):
            if i < 4:
                test.set_ccfc(i)
                test.function_check(str(i+1), i)
                test.clear_all_cf(str(i+1)+'.3')
            if i == 4:
                test.set_ccfc(i)
                test.function_check('5.1', 0)
                test.function_check('5.2', 1)
                test.function_check('5.3', 2)
                test.function_check('5.4', 3)
                test.clear_all_cf('5.5')
            if i == 5:
                test.set_ccfc(i)
                test.function_check('6.1', 1)
                test.function_check('6.2', 2)
                test.function_check('6.3', 3)
                test.clear_all_cf('6.4')

    def cleanup(test):
        global exp_resp_clear_all_cf
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=4,4', exp_resp_clear_all_cf))
        pass

    def set_ccfc(test, reason):
        if reason == 0:
            test.log.info('1. Start test CF-UNCONDITIONAL')
            test.log.step('1.1 set CF-UNCONDITIONAL')
            test.expect(test.dut.at1.send_and_verify(f'AT+CCFC=0,3,"{test.int_r2_phone_num}",,1', 'OK'))
            test.expect(test.dut.at1.send_and_verify('AT+CCFC=0,2', f'CCFC: 1,1,"\\{test.int_r2_phone_num}",145'))

        if reason == 1:
            test.log.info('2. Start test CF-BUSY')
            test.log.step('2.1 set CF-BUSY')
            test.expect(test.dut.at1.send_and_verify(f'AT+CCFC=1,3,"{test.int_r2_phone_num}",,1', 'OK'))
            test.expect(test.dut.at1.send_and_verify('AT+CCFC=1,2', f'CCFC: 1,1,"\\{test.int_r2_phone_num}",145'))

        if reason == 2:
            test.log.info('3. Start test CF-NO REPLY')
            test.log.step('3.1 set CF-NO REPLY')
            test.expect(test.dut.at1.send_and_verify(f'AT+CCFC=2,3,"{test.int_r2_phone_num}",,1', 'OK'))
            test.expect(test.dut.at1.send_and_verify('AT+CCFC=2,2', f'CCFC: 1,1,"\\{test.int_r2_phone_num}",145'))

        if reason == 3:
            test.log.info('4. Start test CF-NOT REACHABLE')
            test.log.step('4.1 set CF-NO REPLY')
            test.expect(test.dut.at1.send_and_verify(f'AT+CCFC=3,3,"{test.int_r2_phone_num}",,1', 'OK'))
            test.expect(test.dut.at1.send_and_verify('AT+CCFC=3,2', f'CCFC: 1,1,"\\{test.int_r2_phone_num}",145'))

        if reason == 4:
            test.log.info('5. Start test CF-NOT REACHABLE')
            test.log.step('5.1 set CF-ALL')
            test.expect(test.dut.at1.send_and_verify(f'AT+CCFC=4,3,"{test.int_r2_phone_num}",,1', 'OK'))

        if reason == 5:
            test.log.info('6. Start test CF-NOT REACHABLE')
            test.log.step('6.1 set CF-ALL CONDITIONAL')
            test.expect(test.dut.at1.send_and_verify(f'AT+CCFC=5,3,"{test.int_r2_phone_num}",,1', 'OK'))
        pass

    def function_check(test, step, reason):
        if reason == 0:
            test.log.step(f'{step}.2 check CF unconditional')
            test.expect(test.dut.at1.send_and_verify(f'ATD{test.int_dut_phone_num};', '.*', wait_for='.*\+CSSI: 0.*'))
            test.expect(test.r2.at1.wait_for(".*\+CSSU: 0.*"))
            test.expect(test.r2.at1.wait_for("RING"))
            test.expect(test.r2.at1.send_and_verify('at+clcc', '.*CLCC: 1,1,4,0.*'))
            test.dut.at1.wait_for_strict("NO CARRIER", 180)

            test.expect(test.dut.dstl_release_call())
            test.expect(test.r1.dstl_release_call())
            test.expect(test.r2.dstl_release_call())

        if reason == 1:
            test.log.step(f'{step}.2 check CF BUSY')
            test.expect(test.dut.dstl_voice_call_by_number(test.r2, test.int_r2_phone_num))
            if '5.2' in step:
                test.expect(test.dut.at1.wait_for(".*\+CSSI: 0.*"))
            # as discussed with xiaoyu.chen, CSSI: do not appear on China network, LTE-TN also does not show +CSSI: 1
            else:
                test.expect(test.dut.at1.wait_for(".*\+CSSI: 1.*"))

            test.expect(test.r1.at1.send_and_verify(f'ATD{test.int_dut_phone_num};', '.*'))

            test.expect(test.r2.at1.wait_for(".*\+CSSU: 0.*"))
            test.expect(test.dut.at1.send_and_verify('at+clcc', '.*CLCC:.*'))

            test.expect(test.dut.dstl_release_call())
            test.expect(test.r1.dstl_release_call())
            test.expect(test.r2.dstl_release_call())

        if reason == 2:
            test.log.step(f'{step}.2 check CF NO REPLY')

            test.expect(test.r1.at1.send_and_verify(f'ATD{test.int_dut_phone_num};', '.*'))

            test.expect(test.r2.at1.wait_for(".*\+CSSU: 0.*"))
            test.expect(test.r2.at1.wait_for(".*RING.*"))
            test.expect(test.dut.at1.send_and_verify('at+clcc', 'OK'))
            test.expect(test.r2.at1.send_and_verify('at+clcc', '.*CLCC: 1,1,4,0.*'))
            test.expect(test.dut.dstl_release_call())
            test.expect(test.r1.dstl_release_call())
            test.expect(test.r2.dstl_release_call())

        if reason == 3:
            test.log.step(f'{step}.2 check CF NOT REACHABLE')
            test.expect(test.dut.at1.send_and_verify('AT+COPS=2', 'OK'))
            test.expect(test.r1.at1.send_and_verify(f'ATD{test.int_dut_phone_num};', '.*'))

            test.expect(test.r2.at1.wait_for(".*\+CSSU: 0.*"))
            test.expect(test.r2.at1.wait_for(".*RING.*"))
            test.expect(test.r2.at1.send_and_verify('at+clcc', '.*CLCC: 1,1,4,0.*'))
            test.expect(test.dut.dstl_release_call())
            test.expect(test.r1.dstl_release_call())
            test.expect(test.r2.dstl_release_call())

            test.expect(test.dut.dstl_register_to_network())
        pass

    def clear_all_cf(test, step):
        test.log.step(f'{step} Clear all CFs')
        global exp_resp_clear_all_cf
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=4,4', exp_resp_clear_all_cf))


if "__main__" == __name__:
    unicorn.main()
