#responsible: yanen.wang@thalesgroup.com
#location: Beijing
#TC0103455.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.shutdown_smso import dstl_shutdown_smso
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board

class Test(BaseTest):
    """
    TC0103455.001-SmsoShutdownBasic

    Check if command is implemented and possible to execute.

    1. Send AT^SMSO=? And check response
    2. Send command AT^SMSO
    3. Using McTest check if module is Off (MC:PWRIND)
    4. Turn On module (MC:IGT=1000) and wait for ^SYSSTART
    5. Send AT command to check if communication with module is possible

    """

    def setup(test):
        dstl_detect(test.dut)
    def run(test):
        test.log.step("1. Send AT^SMSO=? And check response")
        test.expect(test.dut.at1.send_and_verify("AT^SMSO=?", ".*OK.*"))
        test.log.step("2-3. Switch off module via AT^SMSO and Using McTest check if module is Off (MC:PWRIND)")
        test.expect(test.dut.at1.send_and_verify("AT^SMSO", ".*OK"))
        test.dut.devboard.wait_for('.* PWRIND: 1.*')
        test.sleep(5)
        test.log.step("4. Turn On module (MC:IGT=1000) and wait for ^SYSSTART")
        test.expect(dstl_turn_on_igt_via_dev_board(test.dut))
        test.expect(test.dut.at1.wait_for('.*SYSSTART.*'))
        test.log.step("5. Send AT twice")
        test.expect(test.dut.at1.send_and_verify("AT", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT", ".*OK.*"))
        test.expect(dstl_register_to_network(test.dut))
        test.log.step("6. Reset AT Command Settings to Factory Default Values")
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
