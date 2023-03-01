#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0091797.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init

class TpAtCimiBasic(BaseTest):
    """
    TC0091797.001 - TpAtCimiBasic
    This procedure provides the possibility of basic tests for the exec command of AT+CIMI.
    Debugged: Serval
    """

    def setup(test):
        # Restart to make pin locked
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_restart())
        test.dut.at1.send_and_verify("at+cmee=2", ".*OK.*")

    def run(test):
        # Regular expression of IMSI, 15 digits
        imsi = "\s+\d{15}\s+OK\s+"
        # 1. Valid parameters without pin
        test.expect(test.dut.at1.send_and_verify("at+cimi=?", ".*CME ERROR: SIM PIN required.*"))
        test.expect(test.dut.at1.send_and_verify("at+cimi", ".*CME ERROR: SIM PIN required.*"))
        # 2. Invalid parameters without pin
        test.expect(test.dut.at1.send_and_verify("at+cimi?", ".*CME ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+cimi=1", ".*CME ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+cimi0", ".*CME ERROR.*"))
        # 3. Valid parameters with pin
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify("at+cimi=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at+cimi", imsi))
        # 4. Invalid parameters with pin
        test.expect(test.dut.at1.send_and_verify("at+cimi?", ".*CME ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+cimi=1", ".*CME ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+cimi0", ".*CME ERROR.*"))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
