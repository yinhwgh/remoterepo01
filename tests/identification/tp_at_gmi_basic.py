# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0092543.001

import unicorn
import time
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_identification import dstl_get_defined_manufacturer
from dstl.network_service.attach_to_network import dstl_enter_pin
from dstl.security.set_sim_waiting_for_pin1 import dstl_set_sim_waiting_for_pin1


class Test(BaseTest):
    """
   Intention:
   This procedure provides the possibility of basic tests for the exec command of AT+GMI.

    Description:
    - check command without and with PIN
    - check with invalid parameters
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_restart(test.dut)
        time.sleep(2)
        test.dut.at1.send_and_verify("at+cmee=2", ".*OK.*")

    def run(test):
        test.log.info("TC0092543.001 TpAtGmiBasic")
        expected_result = "\s+{}\s+OK\s+".format(dstl_get_defined_manufacturer(test.dut))
        test.log.info("Checking valid parameters without PIN")
        dstl_set_sim_waiting_for_pin1(test.dut)
        test.expect(test.dut.at1.send_and_verify("at+gmi=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at+gmi", expected_result))
        test.log.info("Checking invalid parameters without PIN")
        test.expect(test.dut.at1.send_and_verify("at+gmi?", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+gmi=0", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+gmi0", ".*ERROR.*"))
        test.log.info("Checking valid parameters with PIN")
        test.expect(dstl_enter_pin(test.dut))
        time.sleep(2)
        test.expect(test.dut.at1.send_and_verify("at+gmi=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at+gmi", expected_result))
        test.log.info("Checking invalid parameters with PIN")
        test.expect(test.dut.at1.send_and_verify("at+gmi?", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+gmi=0", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+gmi0", ".*ERROR.*"))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
