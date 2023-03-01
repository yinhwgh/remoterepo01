#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0091737.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.configuration import functionality_modes
from dstl.security import lock_unlock_sim
from dstl.network_service import register_to_network


class Test(BaseTest):
    '''
    TC0091737.001 - TpCccid
    '''

    def setup(test):

        test.dut.dstl_detect()
        test.dut.dstl_lock_sim()
        test.dut.dstl_restart()
        test.sleep(5)

    def run(test):

        test.log.info("1.Test under full fucntion mode. ")
        test.step2to6()

        test.log.info("7. Test under airplane mode. ")
        test.dut.dstl_set_airplane_mode()
        test.step2to6()

    def cleanup(test):
        test.log.info('return full fuction mode.')
        test.dut.dstl_set_full_functionality_mode()


    def step2to6(test):
        iccid_from_sim_cfg = test.dut.sim.kartennummer_gedruckt
        if (iccid_from_sim_cfg != 'None'):
            response = '.*CCID:.*'+iccid_from_sim_cfg+'.*OK.*'
        else:
            response = '.*CCID:.*(8986|891|8901|8948|8949).*OK.*'

        test.expect(test.dut.at1.send_and_verify("AT+CCID=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CCID", response))
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify("AT+CCID=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CCID", response))



if (__name__ == "__main__"):
    unicorn.main()
