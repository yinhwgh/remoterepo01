#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0091793.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.identification import get_identification

class TpAtCgmiBasic(BaseTest):
    """
    TC0091793.001 - TpAtCgmiBasic
    This procedure provides the possibility of basic tests for the exec command of AT+Cgmi.
    Debugged: Serval
    """

    def setup(test):
        # Restart to make pin locked
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_restart())
        test.dut.at1.send_and_verify("at+cmee=2", ".*OK.*")

    def run(test):
        # Regular expression, e.g. "\s+Cinterion\s+OK\s+", "\s+SIEMENS\+OK\s+"
        expected_result = "\s+{}\s+OK\s+".format(test.dut.dstl_get_defined_manufacturer())
        # 1. Valid parameters without pin
        test.expect(test.dut.at1.send_and_verify("at+cgmi=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at+cgmi", expected_result))
        # 2. Invalid parameters without pin
        test.expect(test.dut.at1.send_and_verify("at+cgmi?", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+cgmi=0", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+cgmi0", ".*ERROR.*"))
        # 3. Valid parameters with pin
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify("at+cgmi=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at+cgmi", expected_result))
        # 4. Invalid parameters with pin
        test.expect(test.dut.at1.send_and_verify("at+cgmi?", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+cgmi=0", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+cgmi0", ".*ERROR.*"))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
