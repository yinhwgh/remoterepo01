# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0095043.001

import unicorn
import time
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.network_service.attach_to_network import dstl_enter_pin
from dstl.security.set_sim_waiting_for_pin1 import dstl_set_sim_waiting_for_pin1


class Test(BaseTest):
    """
    Intention:
    This procedure provides the possibility of basic tests for the exec command of AT+Gmm.

    Description:
	- check command without and with PIN
    - check for invalid parameters
    """
    def setup(test):
        dstl_detect(test.dut)
        dstl_restart(test.dut)
        time.sleep(2)
        dstl_set_error_message_format(test.dut)

    def run(test):
        test.log.info("TC0095043.001 TpAtGmmBasic")
        module_type = f"{test.dut.product}-{test.dut.variant}\s+OK\s+"
        expected_module_type = module_type
        test.log.info("Checking valid parameters without PIN")
        dstl_set_sim_waiting_for_pin1(test.dut)
        test.expect(test.dut.at1.send_and_verify("at+gmm=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at+gmm", expected_module_type))
        test.log.info("Checking invalid parameters without PIN")
        test.expect(test.dut.at1.send_and_verify("at+gmm?", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+gmm=1", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+gmm0", ".*ERROR.*"))
        test.log.info("Checking valid parameters with PIN")
        test.expect(dstl_enter_pin(test.dut))
        time.sleep(3)
        test.expect(test.dut.at1.send_and_verify("at+gmm=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at+gmm", expected_module_type))
        test.log.info("Checking invalid parameters with PIN")
        test.expect(test.dut.at1.send_and_verify("at+gmm?", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+gmm=1", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+gmm0", ".*ERROR.*"))

    def cleanup(test):
        pass

if "__main__" == __name__:
    unicorn.main()
