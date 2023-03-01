# responsible: kamil.mierzwa@globallogic.com
# location: Wroclaw
# TC0000001.001

import re
import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.identification.check_c_revision_number import dstl_check_c_revision_number
from dstl.identification.check_identification_ati import dstl_check_ati1_response
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.configuration.functionality_modes import dstl_set_airplane_mode, dstl_set_full_functionality_mode
from dstl.security.set_sim_waiting_for_pin1 import dstl_set_sim_waiting_for_pin1
from dstl.configuration.set_error_message_format import dstl_set_error_message_format

class Test(BaseTest):
    """
    Aim of this test is checking if ATI8 command works correctly.
    First section of test is without PIN
    Second section of test is with PIN
    Third section of test is in airplane mode
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_sim_waiting_for_pin1(test.dut)
        dstl_set_error_message_format(test.dut, "2")

    def run(test):
        test.log.step("1. Check ATI8 command without PIN ")
        test.expect(dstl_check_ati1_response(test.dut))
        test.expect(dstl_check_c_revision_number(test.dut))

        test.log.step("2. Check ATI8 command with PIN ")
        test.expect(dstl_enter_pin(test.dut))
        test.expect(dstl_check_ati1_response(test.dut))
        test.expect(dstl_check_c_revision_number(test.dut))

        test.log.step("3. Check ATI8 command in airplane mode ")
        test.expect(dstl_set_airplane_mode(test.dut))
        test.expect(dstl_check_ati1_response(test.dut))
        test.expect(dstl_check_c_revision_number(test.dut))
        test.expect(dstl_set_full_functionality_mode(test.dut))

        if test.dut.platform.upper() == "INTEL":
            test.log.step("4. Check ATI8 command with disabling JRC midlet ")
            test.expect(test.dut.at1.send_and_verify("at^sjam=4", ".*OK.*"))
            jrc_name = re.search(r"JRC-\d\.\d[2]\.\d+\.jad", test.dut.at1.last_response).group(0)
            if not jrc_name:
                test.log.critical("JRC midlet is not installed")
                test.expect(False, critical=True)
            test.expect(test.dut.at1.send_and_verify(f"at^sjam=2,\"a:/{jrc_name}\",\"\"", ".*OK.*"))
            test.expect(dstl_check_ati1_response(test.dut))
            test.expect(dstl_check_c_revision_number(test.dut))
            test.expect(test.dut.at1.send_and_verify(f"at^sjam=1,\"a:/{jrc_name}\",\"\"", ".*OK.*"))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()