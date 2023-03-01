#author: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0091809.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.security.set_sim_waiting_for_pin1 import dstl_set_sim_waiting_for_pin1
from dstl.security import unlock_sim_pin2

class Test(BaseTest):
    """
    TC0091809.001 - TpAtCpucBasic
    Intention:
    This procedure provides basic tests for the test and write command of +CPUC.
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_set_sim_waiting_for_pin1()
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='OK'))

    def run(test):
        test.log.step('1. test without PIN')
        test.expect(test.dut.at1.send_and_verify('at+cpuc=?', 'CME ERROR: SIM PIN required'))
        test.expect(test.dut.at1.send_and_verify('at+cpuc="EUR","0.88"', 'CME ERROR: SIM PIN required'))
        test.expect(test.dut.at1.send_and_verify('at+cpuc?', 'CME ERROR: SIM PIN required'))

        test.log.step('2. test with PIN')
        test.dut.dstl_enter_pin()
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify('at+cpuc=?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+cpuc="EUR","0.88"', 'CME ERROR: SIM PIN2 required'))
        test.check_cpuc_read_resp('CPUC: \"(\\w{2,3}|)\",\"[0-9.]+\".*OK.*')

        test.log.step('3. check all parameters and also with invalid values')
        test.dut.dstl_enter_pin2()
        test.expect(test.dut.at1.send_and_verify('at+cpuc="GBP","0.88"', 'OK'))
        test.check_cpuc_read_resp('.*CPUC: \"GBP\",\"0.88\".*')
        test.expect(test.dut.at1.send_and_verify(f'at+cpuc="EUR","0","{test.dut.sim.pin2}"', 'OK'))
        test.check_cpuc_read_resp('.*CPUC: \"EUR\",\"0\".*')
        pass

    def cleanup(test):
        pass

    def check_cpuc_read_resp(test, exp_resp):
        if test.dut.project is 'VIPER':
            test.expect(test.dut.at1.send_and_verify('at+cpuc?', '.*CME ERROR: unknown.*', timeout=25))
            test.log.warning("defect accepted by project, see VPR02-939")
        else:
            test.expect(test.dut.at1.send_and_verify('at+cpuc?', exp_resp))
        pass


if "__main__" == __name__:
    unicorn.main()