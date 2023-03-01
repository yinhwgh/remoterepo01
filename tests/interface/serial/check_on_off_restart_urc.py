#responsible: lijuan.li@thalesgroup.com
#location: Beijing
#TC

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board
from dstl.configuration.shutdown_smso import dstl_shutdown_smso
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network

class TcOnOffRestartUrcCheck(BaseTest):
    def setup(test):
        #        test.dut.restart()
        #        test.sleep(5)
        pass

    def run(test):
        test.log.info("1. test: Prepare the connection with the module for all used interfaces ")
        test.expect(test.dut.at2.send_and_verify("AT", ".*OK.*"))

        test.log.info("2. test: Restart the module by CFUN=1,1 ")
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify("AT+cfun=1,1", ".*OK.*", wait_for="SYSSTART", timeout=90))
        test.expect(test.dut.at2.wait_for(".*SYSSTART.*", timeout=90))

        test.log.info("3. test: Turn off the module by SMSO ")
        #test.expect(test.dut.at1.send_and_verify("AT^SMSO", ".*SHUTDOWN.*", wait_for="SHUTDOWN", timeout=90))
        test.expect(test.dut.dstl_shutdown_smso())
        test.expect(test.dut.at2.wait_for(".*SHUTDOWN.*", timeout=90))

        test.dut.dstl_turn_on_igt_via_dev_board()
        test.expect(test.dut.at1.wait_for(".*SYSSTART.*", timeout=90))
        test.expect(test.dut.at2.wait_for(".*SYSSTART.*", timeout=90))

    def cleanup(test):
        pass

if (__name__ == "__main__"):
    unicorn.main()
