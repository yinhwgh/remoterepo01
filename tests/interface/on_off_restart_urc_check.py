#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0087994.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary.devboard import devboard
from dstl.configuration import shutdown_smso
from dstl.auxiliary import init

class  	TcOnOffRestartUrcCheck(BaseTest):
    """
        TC0087994.001 - TcOnOffRestartUrcCheck
        The module should be connected to the PC via at least two interfaces.
        Debugged: Serval
    """

    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        test.log.info('1. Checking interfaces, at lease two interfaces should be connected')
        at2_valid = False
        at3_valid = False
        if test.dut.at2 and test.dut.at2.send_and_verify("AT", ".*OK.*"):
            at2_valid = True
        if test.dut.at3 and test.dut.at3.send_and_verify("AT", ".*OK.*"):
            at3_valid = True
        if not at2_valid and not at3_valid:
            test.log.error("At lease two interfaces should be connected")

        test.log.info('2. "SYSSTART" URC returns when restart module with cfun=1,1 ')
        test.expect(test.dut.dstl_restart())
        # Need handle "SHUTDOWN" URC for Dahlia
        if at2_valid:
            test.expect(test.dut.at2.wait_for("\^SYSSTART"))
        if at3_valid:
            test.expect(test.dut.at3.wait_for("\^SYSSTART"))

        test.log.info('3. "SHUTDOWN" URC returns when turn off module with SMSO ')
        test.expect(test.dut.dstl_shutdown_smso())
        if at2_valid:
            test.expect(test.dut.at2.wait_for("\^SHUTDOWN"))
        if at3_valid:
            test.expect(test.dut.at3.wait_for("\^SHUTDOWN"))

        test.log.info('4. "SYSSTART" URC returns when turn on module with mc ')
        test.sleep(2)
        test.expect(test.dut.dstl_turn_on_igt_via_dev_board())
        test.expect(test.dut.at1.wait_for("\^SYSSTART"))
        if at2_valid:
            test.expect(test.dut.at2.wait_for("\^SYSSTART"))
        if at3_valid:
            test.expect(test.dut.at3.wait_for("\^SYSSTART"))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
