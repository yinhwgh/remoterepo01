#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0091867.001

import unicorn
from core.basetest import BaseTest
import re
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.call.setup_voice_call import dstl_is_voice_call_supported


class Test(BaseTest):
    """
    TC0091867.001 - TpAtCeerBasic
    This procedure provides the possibility of basic tests for +CEER.

    """
    def setup(test):

        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(3)


    def run(test):
        test.log.info('1. Check without pin')
        test.expect(test.dut.at1.send_and_verify('at+cpin?', 'SIM PIN'))
        test.expect(test.dut.at1.send_and_verify('at+ceer=?', '.*OK.*|(.*ERROR\s+)|(.*CME ERROR: SIM PIN required.*)|(.*CME ERROR: 11.*)'))
        test.expect(test.dut.at1.send_and_verify('at+ceer', ' (.*CEER: No cause information available.*)|(.*ERROR\s+)|(.*CME ERROR: SIM PIN required.*)|(.*CME ERROR: 11.*)'))
        test.expect(test.dut.at1.send_and_verify('at+ceer=0', '.*OK.*|(.*ERROR\s+)|(.*CME ERROR: SIM PIN required.*)|(.*CME ERROR: 11.*)'))

        test.log.info('2. Check with pin')
        test.dut.dstl_enter_pin()
        test.dut.dstl_register_to_network()
        test.expect(test.dut.at1.send_and_verify('at+ceer', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+ceer=?', 'OK'))

        test.log.info('3. Check check all parameters and also with invalid values')
        test.expect(test.dut.at1.send_and_verify('at+ceer?', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+ceer=1', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+ceer=0', 'OK'))

        if test.dut.dstl_is_voice_call_supported():
            test.log.info('4. Check functionality by establishing a call which returns BUSY and check +CEER output')
            test.dut.at1.send_and_verify('atd{};'.format(test.dut.sim.nat_voice_nr))
            test.dut.at1.wait_for('BUSY|NO CARRIER')
            test.expect(test.dut.at1.send_and_verify('at+ceer', 'CEER: 0,17,0|CEER: User busy'))
            test.sleep(15)

        test.log.info('5. Check also clearing last error result')
        test.expect(test.dut.at1.send_and_verify('at+ceer=0', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+ceer', '.*CEER: No cause information available.*'))

    def cleanup(test):
        pass





if (__name__ == "__main__"):
    unicorn.main()
