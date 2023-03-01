#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0095670.001

import unicorn

from core.basetest import BaseTest

from dstl.status_control import extended_indicator_control
from dstl.network_service import register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import check_urc

import re

class Test(BaseTest):
    '''
    TC0095670.001 - URCsCheckUsingAtSind
    Check if module can properly display psinfo URCs when registering to 2G/3G/4G
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_enter_pin())
        test.log.info("Step 1. Enable the presentation of a specyfic URC for \"psinfo\" parameter")
        test.expect(test.dut.dstl_enable_one_indicator("psinfo"))

    def run(test):
        test.set_multi_mode()
        ok_or_error = "(OK|ERROR)"

        if test.dut.dstl_is_gsm_supported():
            test.log.info("Step 2. Register module to the GSM network")
            test.expect(test.dut.at1.send_and_verify("AT+COPS=0,,,0", "OK", wait_for=ok_or_error, timeout=60))

            test.log.info("Step 3. Wait for \"psinfo\" status for GSM")
            test.expect(test.dut.dstl_check_urc(expect_urc="\+CIEV: psinfo,[0-4]\s+", timeout=60), 
            msg="PSINFO URC does not appear or incorrect for GSM registration")
            test.check_network_status()

        if test.dut.dstl_is_umts_supported():
            test.log.info("Step 4. Register module to the UTRAN network")
            test.expect(test.dut.at1.send_and_verify("AT+COPS=0,,,2", "OK", wait_for=ok_or_error, timeout=60))

            test.log.info("Step 5. Wait for \"psinfo\" status for UTRAN")
            test.expect(test.dut.dstl_check_urc(expect_urc="\+CIEV: psinfo,([5-9]|10)\s+", timeout=60), 
            msg="PSINFO URC does not appear or incorrect for UTRAN regstration")
            test.check_network_status()

        if test.dut.dstl_is_lte_supported():
            test.log.info("Step 6. Register module to the LTE network")
            test.expect(test.dut.at1.send_and_verify("AT+COPS=0,,,7", "OK", wait_for=ok_or_error, timeout=60))

            test.log.info("Step 7. Wait for \"psinfo\" status for LTE")
            test.expect(test.dut.dstl_check_urc(expect_urc="\+CIEV: psinfo,(16|17)\s+", timeout=60), 
            msg="PSINFO URC does not appear or incorrect for LTE regstration")
            test.check_network_status()

    def cleanup(test):
        test.expect(test.dut.dstl_disable_one_indicator("psinfo"))

    def check_network_status(test):
        test.expect(test.dut.at1.send_and_verify("AT+CREG?", "\+CREG: \d,1", wait_for="\s+OK\s+"), msg="Incorrect network status")
        test.dut.at1.send_and_verify("AT+COPS?", "\+COPS: \d,\d,.+,[0267]\s+", wait_for="\s+OK\s+")
    
    
    def set_multi_mode(test):
        test.log.info("Setting to multiple mode")
        test.expect(test.dut.at1.send_and_verify("AT^SXRAT=?", "OK", wait_for="(OK|ERROR)"))
        sxrat_response = test.dut.at1.last_response
        sxrat_format = re.compile("\^SXRAT: \(\d\-(\d)\).*")
        search_groups = sxrat_format.search(sxrat_response)
        if search_groups:
            max_sxrat = search_groups.group(1)
            test.expect(test.dut.at1.send_and_verify(f"AT^SXRAT={max_sxrat}", "OK", wait_for="(OK|ERROR)"))



if __name__=='__main__':
    unicorn.main()
