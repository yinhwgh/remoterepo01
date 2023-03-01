# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0095044.001
#SRV03-4887

import unicorn
import time
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_identification import dstl_get_defined_sw_revision
from dstl.network_service.attach_to_network import dstl_enter_pin
from dstl.security.set_sim_waiting_for_pin1 import dstl_set_sim_waiting_for_pin1
from dstl.auxiliary.write_json_result_file import *


class Test(BaseTest):
    """
    Intention:
    This procedure provides the possibility of basic tests with AT+GMR

    Description:
	- check command without and with PIN
    - check for invalid parameters
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_restart(test.dut)
        time.sleep(2)

    def run(test):
        test.log.info("TC0095044.001 TpAtGmrBasic")
        revision_format = dstl_get_defined_sw_revision(test.dut)
        test.log.info("Checking valid parameters without PIN")
        dstl_set_sim_waiting_for_pin1(test.dut)
        test.expect(test.dut.at1.send_and_verify("at+gmr=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at+gmr", revision_format))
        test.log.info("Checking invalid parameters without PIN")
        test.expect(test.dut.at1.send_and_verify("at+gmr?", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+gmr=1", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+gmr0", ".*ERROR.*"))
        test.log.info("Checking valid parameters with PIN")
        test.expect(dstl_enter_pin(test.dut))
        test.expect(test.dut.at1.send_and_verify("at+gmr=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at+gmr", revision_format))
        test.log.info("Checking invalid parameters with PIN")
        test.expect(test.dut.at1.send_and_verify("at+gmr?", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+gmr=1", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+gmr0", ".*ERROR.*"))

    def cleanup(test):
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        test.get('test_key', default='no_test_key'), str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + 'test_key' + ') - End *****')


if "__main__" == __name__:
    unicorn.main()