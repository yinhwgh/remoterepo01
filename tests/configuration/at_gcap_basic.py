# responsible: christian.gosslar@thalesgroup.com
# location: Berlin
# LM0007549.001 - TC0091895.001- TpAtGcapBasic

import unicorn
from dstl.auxiliary import init
from core.basetest import BaseTest
from dstl.security.lock_unlock_sim import *
from dstl.auxiliary.restart_module import dstl_restart


from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.identification.collect_module_infos import dstl_collect_module_info
from dstl.identification.get_revision_number import dstl_get_revision_number
from dstl.identification.get_imei import dstl_get_imei
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.check_c_revision_number import dstl_check_c_revision_number
from dstl.identification.get_part_number import dstl_check_or_read_part_number


class TpAtCmeeBasic(BaseTest):

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.log.com('***** Collect some Module Infos *****')
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.dut.dstl_get_bootloader()
        test.dut.dstl_check_c_revision_number()
        test.dut.dstl_collect_module_info()
        test.dut.dstl_check_or_read_part_number(only_read=True)
        pass

    def run(test):
        resp_gcap_test_without_pin = ".*[+]CME ERROR: SIM PIN required.*"
        resp_gcap_test_with_pin = ".*OK.*"
        resp_gcap_exec_without_pin = ".*[+]CME ERROR: SIM PIN required.*"
        resp_gcap_exec_with_pin = ".*[+]CGSM.*"
        if test.dut.project == 'BOBCAT':
            test.log.info("")
        elif test.dut.project == 'VIPER':
            test.log.info("")

        test.log.step('Step 1.0: check test and exec command without PIN')
        # ==============================================================
        test.dut.at1.send_and_verify("at+CPIN?", ".*O.*")
        if "READY" in test.dut.at1.last_response:
            # restart the module
            test.expect(test.dut.dstl_restart())

        test.expect(test.attempt(test.dut.at1.send_and_verify, "AT+gCap=?",
                                 expect=resp_gcap_test_without_pin, retry=5, sleep=2))
        test.expect(test.dut.at1.send_and_verify("AT+GCAP", resp_gcap_exec_without_pin))

        test.log.step('Step 2.0: check test and exec command with PIN')
        # ==============================================================
        test.expect(test.dut.dstl_register_to_network())

        test.expect(test.dut.at1.send_and_verify("AT+gCap=?", resp_gcap_test_with_pin))
        test.expect(test.dut.at1.send_and_verify("AT+GCAP", resp_gcap_exec_with_pin))

        test.log.step('Step 3.0: check command with invalid parameters')
        # ==============================================================
        test.expect(test.dut.at1.send_and_verify("AT+GCAP?", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT+GCAP=21", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT+GCAP=-1", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT+GCAP=0", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT+GCAP=\"FCLASS\"", ".*ERROR.*"))
        pass

    def cleanup(test):
        """Cleanup method.
        Steps to be executed after test run steps.
        """
        # ==============================================================
        test.log.com('**** log  dir: ' + test.workspace + ' ****')
        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')
        pass


if __name__ == "__main__":
    unicorn.main()
