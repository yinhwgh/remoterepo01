# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0091802.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call import setup_voice_call


class Test(BaseTest):
    """
    TC0091802.001 - TpAtChldBasic
    This procedure provides the possibility of basic tests for the test and write command of +CHLD.
    Subscriber: 3
    """
    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.r2.dstl_detect()
        test.dut.dstl_restart()
        test.expect(test.r1.dstl_register_to_network())
        test.expect(test.r2.dstl_register_to_network())
        test.sleep(3)

        test.nat_dut_phone_num = test.dut.sim.nat_voice_nr

        test.nat_r1_phone_num = test.r1.sim.nat_voice_nr
        test.r1_phone_num_regexpr = test.r1.sim.nat_voice_nr
        if test.r1_phone_num_regexpr.startswith('0'):
            test.r1_phone_num_regexpr = test.r1_phone_num_regexpr[1:]

        test.nat_r2_phone_num = test.r2.sim.nat_voice_nr
        test.r2_phone_num_regexpr = test.r2.sim.nat_voice_nr
        if test.r2_phone_num_regexpr.startswith('0'):
            test.r2_phone_num_regexpr = test.r2_phone_num_regexpr[1:]

        pass

    def run(test):
        test.log.step('1. test write and read commands without pin')
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+cpin?', 'SIM PIN'))
        test.expect(test.dut.at1.send_and_verify('at+chld=1', '\+CME ERROR: SIM PIN required'))
        test.expect(test.dut.at1.send_and_verify('at+chld=?', '\+CME ERROR: SIM PIN required'))

        test.log.step('2. test with pin and invalid values')
        test.dut.dstl_register_to_network()

        test.expect(test.dut.at1.send_and_verify('at+chld?', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+chld=1', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+chld=13', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+chld=-1', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+chld=1,1', 'ERROR'))

        test.expect(test.dut.at1.send_and_verify('at+chld=?', '.*\+CHLD: \(0,1,1[Xx],2,2[Xx],3,4\).*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+ccwa=1,1,1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccwa=1,2', '.*\+CCWA: 1,1'))

        test.log.step('3. test the functionality ')
        test.log.step('3.1 AT+CHLD=1 ,AT+CHLD=2 ')
        test.step3_1()
        test.sleep(5)

        test.log.step('3.2 AT+CHLD=0 ')
        test.step3_2()
        test.sleep(5)

        test.log.step('3.3 AT+CHLD=1x ')
        test.step3_3()
        test.sleep(5)

        test.log.step('3.4 AT+CHLD=2x ')
        test.step3_4()
        test.sleep(5)

        test.log.step('3.5 AT+CHLD=3(conference call) ,AT+CHLD=4(ECT)')
        test.step3_5()
        pass

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('at+ccwa=0,0,1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccwa=,2', '.*\+CCWA: 0,.*'))
        test.expect(test.dut.dstl_release_call())
        pass

    def step3_1(test):
        test.expect(test.dut.dstl_voice_call_by_number(test.r1, test.nat_r1_phone_num))

        test.expect(test.r2.at1.send_and_verify(f'ATD{test.nat_dut_phone_num};', '.*'))
        test.expect(test.dut.at1.wait_for(f".*\+CCWA:.*{test.r2_phone_num_regexpr}.*"))

        test.expect(test.dut.at1.send_and_verify('at+clcc',
                                                 f'.*CLCC: 1,0,0,0,0,.*{test.r1_phone_num_regexpr}'
                                                 f'.*CLCC: 2,1,5,0,0.*{test.r2_phone_num_regexpr}.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+chld=2', 'OK'))

        if test.dut.project is 'VIPER':
            test.log.warning("following defect accepted, see VPR02-940 - not to fix")
            test.expect(test.dut.at1.send_and_verify('at+clcc', f'.*CLCC: 1,0,1,0,0,.*{test.r1_phone_num_regexpr}'
                                                                f'.*CLCC: 2,1,0,0,0,"".*OK.*'))
        else:
            test.expect(test.dut.at1.send_and_verify('at+clcc', f'.*CLCC: 1,0,1,0,0,.*{test.r1_phone_num_regexpr}'
                                                                f'.*CLCC: 2,1,0,0,0.*{test.r2_phone_num_regexpr}.*OK.*'))

        test.expect(test.dut.at1.send_and_verify('at+chld=1', 'OK'))

        test.expect(test.r2.at1.wait_for('.*NO CARRIER.*'))
        test.expect(test.dut.at1.send_and_verify('at+clcc',
                                                 f'.*CLCC: 1,0,0,0,0,.*{test.r1_phone_num_regexpr}.*OK.*'))
        test.expect(test.dut.dstl_release_call())
        test.expect(test.r1.dstl_release_call())
        test.expect(test.r2.dstl_release_call())
        pass

    def step3_2(test):
        test.log.info('3.2.1 Test terminate all held calls')
        test.expect(test.dut.dstl_voice_call_by_number(test.r1, test.nat_r1_phone_num))

        test.expect(test.r2.at1.send_and_verify(f'ATD{test.nat_dut_phone_num};', '.*'))
        test.expect(test.dut.at1.wait_for(f".*\+CCWA:.*{test.r2_phone_num_regexpr}.*"))

        test.expect(test.dut.at1.send_and_verify('at+clcc',
                                                 f'.*CLCC: 1,0,0,0,0,.*{test.r1_phone_num_regexpr}'
                                                 f'.*CLCC: 2,1,5,0,0.*{test.r2_phone_num_regexpr}.*OK.*'))

        test.expect(test.dut.at1.send_and_verify('at+chld=2', 'OK'))
        if test.dut.project is 'VIPER':
            test.log.warning("following defect accepted, see VPR02-940 - not to fix")
            test.expect(test.dut.at1.send_and_verify('at+clcc', f'.*CLCC: 1,0,1,0,0,.*{test.r1_phone_num_regexpr}'
                                                                f'.*CLCC: 2,1,0,0,0,"".*OK.*'))
        else:
            test.expect(test.dut.at1.send_and_verify('at+clcc',
                                                     f'.*CLCC: 1,0,1,0,0,.*{test.r1_phone_num_regexpr}'
                                                     f'.*CLCC: 2,1,0,0,0.*{test.r2_phone_num_regexpr}.*OK.*'))

        test.expect(test.dut.at1.send_and_verify('at+chld=0', 'OK'))
        test.expect(test.r1.at1.wait_for('.*NO CARRIER.*'))
        test.expect(test.dut.at1.send_and_verify('at+clcc',
                                                 f'.*CLCC: 2,1,0,0,0.*{test.r2_phone_num_regexpr}.*OK.*'))

        test.expect(test.dut.at1.send_and_verify('at+chld=2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+clcc',
                                                 f'.*CLCC: 2,1,1,0,0.*{test.r2_phone_num_regexpr}.*OK.*'))

        test.expect(test.dut.at1.send_and_verify('at+chld=0', 'OK', wait_for='.*NO CARRIER.*'))

        test.expect(test.dut.dstl_release_call())
        test.expect(test.r1.dstl_release_call())
        test.expect(test.r2.dstl_release_call())

        test.log.info('3.2.2 Test terminate all held calls')
        test.expect(test.dut.dstl_voice_call_by_number(test.r1, test.nat_r1_phone_num))
        test.expect(test.r2.at1.send_and_verify(f'ATD{test.nat_dut_phone_num};', '.*'))
        test.expect(test.dut.at1.wait_for(f".*\+CCWA:.*{test.r2_phone_num_regexpr}.*"))
        test.expect(test.dut.at1.send_and_verify('at+chld=0', 'OK'))
        test.expect(test.r2.at1.wait_for('.*BUSY.*', timeout=120))
        test.expect(test.dut.dstl_release_call())
        pass

    def step3_3(test):
        test.expect(test.dut.dstl_voice_call_by_number(test.r1, test.nat_r1_phone_num))
        test.sleep(3)
        test.expect(test.dut.dstl_voice_call_by_number(test.r2, test.nat_r2_phone_num))
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('at+clcc',
                                                 f'.*CLCC: 1,0,1,0,0,.*{test.r1_phone_num_regexpr}'
                                                 f'.*CLCC: 2,0,0,0,0.*{test.r2_phone_num_regexpr}.*OK.*'))

        test.expect(test.dut.at1.send_and_verify('at+chld=12', 'OK'))
        test.expect(test.r2.at1.wait_for('.*NO CARRIER.*'))
        test.expect(test.dut.at1.send_and_verify('at+clcc',
                                                 f'.*CLCC: 1,0,(0|1),0,0,.*{test.r1_phone_num_regexpr}.*OK.*'))

        test.expect(test.dut.dstl_voice_call_by_number(test.r2, test.nat_r2_phone_num))
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('at+clcc',
                                                 f'.*CLCC: 1,0,1,0,0,.*{test.r1_phone_num_regexpr}'
                                                 f'.*CLCC: 2,0,0,0,0.*{test.r2_phone_num_regexpr}.*OK.*'))

        test.expect(test.dut.at1.send_and_verify('at+chld=11', 'OK'))
        test.expect(test.r1.at1.wait_for('.*NO CARRIER.*'))
        test.expect(test.dut.at1.send_and_verify('at+clcc',
                                                 f'.*CLCC: 2,0,0,0,0,.*{test.r2_phone_num_regexpr}.*OK.*'))

        test.expect(test.dut.dstl_release_call())
        test.expect(test.r1.dstl_release_call())
        test.expect(test.r2.dstl_release_call())
        pass

    def step3_4(test):
        test.expect(test.dut.dstl_voice_call_by_number(test.r1, test.nat_r1_phone_num))

        test.expect(test.r2.at1.send_and_verify(f'ATD{test.nat_dut_phone_num};', '.*'))
        test.expect(test.dut.at1.wait_for(f".*\+CCWA:.*{test.r2_phone_num_regexpr}.*"))

        test.expect(test.dut.at1.send_and_verify('at+clcc',
                                                 f'.*CLCC: 1,0,0,0,0,.*{test.r1_phone_num_regexpr}'
                                                 f'.*CLCC: 2,1,5,0,0.*{test.r2_phone_num_regexpr}.*OK.*'))

        test.expect(test.dut.at1.send_and_verify('at+chld=2', 'OK'))
        if test.dut.project is 'VIPER':
            test.log.warning("following defect accepted, see VPR02-940 - not to fix")
            test.expect(test.dut.at1.send_and_verify('at+clcc', f'.*CLCC: 1,0,1,0,0,.*{test.r1_phone_num_regexpr}'
                                                                f'.*CLCC: 2,1,0,0,0,"".*OK.*'))
        else:
            test.expect(test.dut.at1.send_and_verify('at+clcc',
                                                 f'.*CLCC: 1,0,1,0,0,.*{test.r1_phone_num_regexpr}'
                                                 f'.*CLCC: 2,1,0,0,0.*{test.r2_phone_num_regexpr}.*OK.*'))

        test.expect(test.dut.at1.send_and_verify('at+chld=21', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+clcc',
                                                 f'.*\+CLCC: 1,0,0,0,0,.*{test.r1_phone_num_regexpr}'
                                                 f'.*\+CLCC: 2,1,1,0,0.*{test.r2_phone_num_regexpr}.*OK.*'))
        test.expect(test.dut.dstl_release_call())
        test.expect(test.r1.at1.wait_for('.*NO CARRIER.*'))
        test.expect(test.r2.dstl_release_call())
        pass

    def step3_5(test):
        test.log.info(' Notice: Need SIM card /Network support conference (multiparty) call (CHLD=3)and ECT (CHLD=4)!')
        test.expect(test.dut.dstl_voice_call_by_number(test.r1, test.nat_r1_phone_num))
        test.expect(test.r2.at1.send_and_verify(f'ATD{test.nat_dut_phone_num};', '.*'))
        test.expect(test.dut.at1.wait_for(f".*\+CCWA:.*{test.r2_phone_num_regexpr}.*"))

        test.expect(test.dut.at1.send_and_verify('at+clcc',
                                                 f'.*\+CLCC: 1,0,0,0,0,.*{test.r1_phone_num_regexpr}'
                                                 f'.*\+CLCC: 2,1,5,0,0.*{test.r2_phone_num_regexpr}.*OK.*'))

        test.expect(test.dut.at1.send_and_verify('at+chld=2', 'OK'))
        if test.dut.project is 'VIPER':
            test.log.warning("following defect accepted, see VPR02-940 - not to fix")
            test.expect(test.dut.at1.send_and_verify('at+clcc', f'.*CLCC: 1,0,1,0,0,.*{test.r1_phone_num_regexpr}'
                                                                f'.*CLCC: 2,1,0,0,0,"".*OK.*'))
        else:
            test.expect(test.dut.at1.send_and_verify('at+clcc',
                                                 f'.*\+CLCC: 1,0,1,0,0,.*{test.r1_phone_num_regexpr}'
                                                 f'.*\+CLCC: 2,1,0,0,0.*{test.r2_phone_num_regexpr}.*OK.*'))

        test.expect(test.dut.at1.send_and_verify('at+chld=3', 'OK'))
        if test.dut.project is 'VIPER':
            test.log.warning("following defect accepted, see VPR02-940 - not to fix")
            test.expect(test.dut.at1.send_and_verify('at+clcc', f'.*CLCC: 1,0,0,0,1,.*{test.r1_phone_num_regexpr}'
                                                                f'.*CLCC: 2,1,0,0,1,"".*OK.*'))
        else:
            test.expect(test.dut.at1.send_and_verify('at+clcc',
                                                 f'.*\+CLCC: 1,0,0,0,1,.*{test.r1_phone_num_regexpr}'
                                                 f'.*\+CLCC: 2,1,0,0,1.*{test.r2_phone_num_regexpr}.*OK.*'))

        ret = test.dut.at1.send_and_verify('at+chld=4', 'OK')    # ECT - this does not work in the Ericsson TN
        if 'CME ERROR: resource limitation' in test.dut.at1.last_response and '26295' in test.dut.sim.imsi:
            test.expect(True, msg=" CHLD=4 / ECT is not available at Ericsson Testnetwork, response is OK")

        test.expect(test.dut.at1.send_and_verify('at+clcc', 'OK'))

        test.expect(test.dut.dstl_release_call())
        test.expect(test.r1.dstl_release_call())
        test.expect(test.r2.dstl_release_call())
        pass


if "__main__" == __name__:
    unicorn.main()
