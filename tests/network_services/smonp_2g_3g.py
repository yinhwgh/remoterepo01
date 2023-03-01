#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0107119.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.security import lock_unlock_sim
from dstl.auxiliary import restart_module
from dstl.network_service import check_cell_monitor_parameters

import re


class Test(BaseTest):
    """
    TC0107119.001 - SMONP_2G_3G
    Intention:
        Test case to check AT^SMONP for 2G and 3G
    """

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_lock_sim())
        test.expect(test.dut.dstl_restart())

    def run(test):
        test.log.step("1. Check SMONP under pin locked")
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "SIM PIN"))
        test.expect(test.dut.at1.send_and_verify("AT^SMONP", "OK"))

        test.log.step("2. Make module register on 2g network AT+COPS=1,2,\"46000\",0")
        registered_to_2g = test.expect(test.dut.dstl_register_to_gsm())
        if registered_to_2g:
            test.check_smonp_state(rat="2G")
        else:
            test.log.error("Fail to register to GSM, skip tests for 2G.")
            test.dut.dstl_register_to_network()

        test.log.step("3. Make module register on 3g network AT+COPS=1,2,\"46001\",2")
        registered_to_3g = test.expect(test.dut.dstl_register_to_umts())
        if registered_to_3g:
            test.check_smonp_state(rat="3G")
        else:
            test.log.error("Fail to register to UMTS, skip tests for 3G.")
            test.dut.dstl_register_to_network()

        test.log.step("4. Check some invalid paramete")
        invalid_parameters = ['?', "=DD", '=2']
        for invalid_param in invalid_parameters:
            test.expect(test.dut.at1.send_and_verify(f"AT+SMONP{invalid_param}", "ERROR"))

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT+COPS=0", "OK"))

    def check_smonp_state(test, rat):
        unregistered = ""
        for r in ['2G', '3G', '4G']:
            if r != rat:
                unregistered += r + ":\s+([-]+,)+[-]+\s+"
        expect_smonp_status = eval(f"test.dut.dstl_expect_smonp_parameter_{rat.lower()}()")
        test.log.info("Checking expected response: " + expect_smonp_status)
        test.expect(test.dut.at1.send_and_verify("AT^SMONP", expect_smonp_status))
        last_response = test.dut.at1.last_response
        test.log.info("Checking expected response of unregistered RAT: " + unregistered)
        find_unregistered = re.search(unregistered, last_response)
        if find_unregistered:
            test.log.info(f"Expect format of unregistered rat {unregistered} in response.")
        else:
            test.expect(False, msg=f"Incorrect format of unregistered rat {unregistered} in response.")


if "__main__" == __name__:
    unicorn.main()