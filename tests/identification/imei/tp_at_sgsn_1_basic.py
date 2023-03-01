# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0092544.001

import unicorn
from dstl.auxiliary.init import dstl_detect
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.identification.get_imei import dstl_get_imei
import time

class Test(BaseTest):
    """
    Intention:
    This procedure provides the possibility of basic tests for the exec command of AT^SGSN for
    Customer IMEI  modules only.

    Description:
    - check command without and with PIN
    - check with invalid parameters
    """

    def setup(test):
        dstl_detect(test.dut)
        test.IMEI = dstl_get_imei(test.dut)
        dstl_restart(test.dut)
        time.sleep(2)

    def run(test):
        test.log.info("TC0092544.001 TpAtSgsn1Basic")
        test.log.info("Checking command without PIN")
        test.expect(test.dut.at1.send_and_verify("at^sgsn=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at^sgsn?", "\s\d{15}\s"))
        test.expect(test.dut.at1.send_and_verify("at^sgsn", test.IMEI))
        test.log.info("Checking command without PIN - invalid values")
        test.expect(test.dut.at1.send_and_verify("at^sgsn=1", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at^sgsn0", ".*ERROR.*"))
        test.log.info("Checking command with PIN")
        dstl_enter_pin(test.dut)
        time.sleep(2)
        test.expect(test.dut.at1.send_and_verify("at^sgsn=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at^sgsn?", "\s\d{15}\s"))
        test.expect(test.dut.at1.send_and_verify("at^sgsn", test.IMEI))
        test.log.info("Checking command with PIN - invalid values")
        test.expect(test.dut.at1.send_and_verify("at^sgsn=1", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at^sgsn0", ".*ERROR.*"))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()