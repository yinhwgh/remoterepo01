#responsible: dariusz.drozdek@globallogic.com
#location: Wroclaw
#TC0094507.001

import re
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network, dstl_enter_pin


class Test(BaseTest):
    """TC0094507.001    TpAtCgerepBasic

    This procedure provides the possibility of basic tests for the test, read and write command of +CGEREP

    1. Check command without and with PIN.
    2. Check for invalid parameter.
    3. Check power up values.
    """

    def setup(test):
        dstl_detect(test.dut)
        test.expect(dstl_get_imei(test.dut))
        test.expect(dstl_get_bootloader(test.dut))
        test.expect(dstl_restart(test.dut))
        test.dut.at1.send_and_verify('AT+CGDCONT=1,\"IP\",\"{}\"'.format(test.dut.sim.apn_v4), ".*OK.*")

    def run(test):
        test.log.step("1. check command without and with PIN.")
        test.log.info("Check command without PIN")
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", r".*\+CPIN: SIM PIN.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CGEREP=?", r".*\+CME ERROR: SIM PIN required.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CGEREP=1", r".*\+CME ERROR: SIM PIN required.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CGEREP?", r".*\+CME ERROR: SIM PIN required.*"))
        test.log.info("Check command with PIN")
        test.expect(dstl_register_to_network(test.dut))
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify("AT+CGEREP=?", r".*\+CGEREP: \(0(-|,1,)2\),\(0(-|,)1\).*"))
        test.expect(test.dut.at1.send_and_verify("AT+CGEREP?", r".*\+CGEREP: 0,[01]"))

        for mode in range(3):
            for bfr in range(2):
                test.expect(test.dut.at1.send_and_verify("AT+CGEREP={},{}".format(mode, bfr), r".*OK*"))
                test.expect(test.dut.at1.send_and_verify("AT+CGEREP?", r".*\+CGEREP: {},{}.*OK.*".format(mode, bfr)))
                test.expect(test.dut.at1.send_and_verify("AT+CGEREP={}".format(mode), r".*OK*"))
                test.expect(test.dut.at1.send_and_verify("AT+CGEREP?", r".*\+CGEREP: {},{}.*OK.*".format(mode, bfr)))
        test.expect(test.dut.at1.send_and_verify("AT+CGEREP=", r".*OK*"))
        test.expect(test.dut.at1.send_and_verify("AT+CGEREP?", r".*\+CGEREP: 2,1"))

        test.log.step("2. Check for invalid parameter.")
        invalid_values = [",1", "-1", "3", ",0", "1,2", "1,-1", "43", "1,a", "b", "w,1", "1x", "1,1,1", "1,1,0",
                          "\"1\"", "1,\"1\""]
        for value in invalid_values:
            test.expect(test.dut.at1.send_and_verify("AT+CGEREP={}".format(value), r".*\+CME ERROR:*"))
            test.expect(test.dut.at1.send_and_verify("AT+CGEREP?", r".*\+CGEREP: 2,1"))

        test.log.step("3. Check power up values.")
        test.expect(test.dut.at1.send_and_verify("AT+CGEREP=1,1", r".*OK."))
        test.expect(dstl_restart(test.dut))
        test.expect(dstl_enter_pin(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT+CGEREP?", r".*\+CGEREP: 0,[0,1].*OK."))

    def cleanup(test):
        test.dut.at1.send_and_verify("AT+CGEREP=0,0", r".*OK.")
        test.dut.at1.send_and_verify("AT&F", ".*OK.*")
        test.dut.at1.send_and_verify("AT&W", ".*OK.*")


if "__main__" == __name__:
    unicorn.main()
