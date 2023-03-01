#responsible: renata.bryla@globallogic.com
#location: Wroclaw
#TC0094489.001

import re
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.attach_to_network import dstl_enter_pin
from dstl.security.lock_unlock_sim import dstl_lock_sim
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.sms_functions import dstl_send_sms_message


class Test(BaseTest):
    """TC0094489.001    TpAtSindNewSms
    Check the status of indicator "newsms" with AT^SIND command.

    - check command without and with PIN
    - check all parameters and also with invalid values
    - functional tests are done here
    """

    mode_query = 2
    mode_enable = 1
    mode_disable = 0
    time_value_in_sec = 5
    invalid_value = ["", ",-1", ",3", ",2,1"]

    def setup(test):
        test.prepare_module_before_test(test.dut, "===== Start preparation for DUT module =====")
        test.prepare_module_before_test(test.r1, "===== Start preparation for REMOTE module =====")

    def run(test):
        test.log.h2("Starting TC0094489.001 TpAtSindNewSms")

        test.log.step("Check command without and with PIN")
        test.log.info("===== Check command without PIN =====")
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*OK.*"))
        if re.search(r".*SIM PIN.*", test.dut.at1.last_response):
            test.expect(True, msg="SIM PIN code locked - checking if command is PIN protected could be realized")
        else:
            test.log.info("SIM PIN entered - restart is needed")
            test.expect(dstl_restart(test.dut))
            test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*OK.*"))
            if re.search(r".*SIM PIN.*", test.dut.at1.last_response):
                test.expect(True, msg="SIM PIN code locked - checking if command is PIN protected could be realized")
            else:
                test.expect(True, msg="SIM PIN code unlocked - must be locked for checking if command is PIN protected")
                test.expect(dstl_lock_sim(test.dut))
                test.expect(dstl_restart(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
        test.execute_sind_command("AT^SIND=?", "")
        test.execute_sind_command("AT^SIND?", test.mode_disable)
        test.execute_sind_command("AT^SIND=\"newsms\",{}".format(test.mode_query), test.mode_disable)
        test.execute_sind_command("AT^SIND=\"newsms\",{}".format(test.mode_enable), test.mode_enable)
        test.execute_sind_command("AT^SIND=\"newsms\",{}".format(test.mode_query), test.mode_enable)
        test.log.info("===== Check command with PIN authentication =====")
        test.expect(dstl_enter_pin(test.dut))
        test.log.info("Wait according to info from ATC: [\n]"
                      "Users should be aware that error will occur when using this AT command quickly [\n]"
                      "after SIM PIN authentication due to the fact the SIM data may not yet be accessible")
        test.sleep(timeout=30)
        test.execute_sind_command("AT^SIND=?", "")
        test.execute_sind_command("AT^SIND?", test.mode_enable)
        test.execute_sind_command("AT^SIND=\"newsms\",{}".format(test.mode_query), test.mode_enable)

        test.log.step("Check all parameters and also with invalid values")
        test.log.info("===== Check command with valid parameters =====")
        test.execute_sind_command("AT^SIND=\"newsms\",{}".format(test.mode_disable), test.mode_disable)
        test.execute_sind_command("AT^SIND=\"newsms\",{}".format(test.mode_query), test.mode_disable)
        test.execute_sind_command("AT^SIND=\"newsms\",{}".format(test.mode_enable), test.mode_enable)
        test.execute_sind_command("AT^SIND=\"newsms\",{}".format(test.mode_query), test.mode_enable)
        test.log.info("===== Check command with invalid parameters =====")
        for i in test.invalid_value:
            test.execute_sind_command("AT^SIND=\"newsms\"{}".format(i), "test invalid value")

        test.log.step("Functional tests are done here")
        test.prepare_module_to_functional_test(test.dut, "===== Prepare DUT module to functional test =====")
        test.prepare_module_to_functional_test(test.r1, "===== Prepare REMOTE module to functional test =====")
        test.log.info("===== Check scenario with URC CIEV messages ENABLED =====")
        test.execute_sind_command("AT^SIND=\"newsms\",{}".format(test.mode_enable), test.mode_enable)
        test.execute_sind_command("AT^SIND=\"newsms\",{}".format(test.mode_query), test.mode_enable)
        test.check_scenario_for_functional_test(test.mode_enable, "SMS with SIND newsms ENABLED")
        test.log.info("===== Check scenario with URC CIEV messages DISABLED =====")
        test.execute_sind_command("AT^SIND=\"newsms\",{}".format(test.mode_disable), test.mode_disable)
        test.execute_sind_command("AT^SIND=\"newsms\",{}".format(test.mode_query), test.mode_disable)
        test.check_scenario_for_functional_test(test.mode_disable, "SMS with SIND newsms DISABLED")

    def cleanup(test):
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))
        test.expect(test.r1.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.r1.at1.send_and_verify("AT&W", ".*OK.*"))

    def prepare_module_before_test(test, module, text):
        test.log.info(text)
        test.expect(module.at1.send_and_verify("ATE1", "OK"))
        dstl_detect(module)
        dstl_get_imei(module)
        dstl_get_bootloader(module)
        dstl_set_scfg_urc_dst_ifc(module)
        test.expect(module.at1.send_and_verify('AT^SCFG="SMS/AutoAck",0', ".*O.*"))
        test.expect(module.at1.send_and_verify('AT+CSCS="GSM"', ".*OK.*"))

    def prepare_module_to_functional_test(test, module, text):
        test.log.info(text)
        test.expect(dstl_select_sms_message_format(module))
        test.expect(dstl_set_sms_center_address(module, module.sim.sca_int))
        test.expect(module.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*"))
        test.expect(dstl_set_preferred_sms_memory(module, "ME"))
        test.expect(dstl_delete_all_sms_messages(module))

    def execute_sind_command(test, command, mode):
        if mode == "test invalid value":
            expected_response = ".*CME ERROR: invalid index.*"
        else:
            if "AT^SIND=?" in command:
                expected_response = ".*,\\(newsms,\\(0-1\\)\\),.*OK.*"
            else:
                expected_response = ".*\\^SIND: newsms,{}.*OK.*".format(mode)
        test.expect(test.dut.at1.send_and_verify("{}".format(command), "{}".format(expected_response)))

    def check_scenario_for_functional_test(test, mode, text):
        test.expect(dstl_send_sms_message(test.r1, test.dut.sim.int_voice_nr, text))
        sms_index = test.check_cmti_urc()
        if sms_index:
            test.check_ciev_urc(mode, sms_index)
            test.expect(test.dut.at1.send_and_verify("AT+CMGR={}".format(sms_index), ".*[\n\r]{}.*OK.*".format(text)))
        else:
            test.log.info("Message NOT delivered - CIEV message CANNOT be verified")

    def check_cmti_urc(test):
        test.expect(dstl_check_urc(test.dut, ".*CMTI.*", timeout=360))
        sms_received = re.search(r"CMTI:\s*\"ME\",\s*(\d{1,3})", test.dut.at1.last_response)
        if sms_received:
            test.expect(True, msg="===== Message received correctly =====")
            return sms_received[1]
        else:
            return test.expect(False, msg="===== Message was not received =====")

    def check_ciev_urc(test, mode, index):
        if mode == test.mode_enable:
            test.log.info("===== Check CIEV URC - Expected SEARCH CIEV =====")
            test.expect(test.dut.at1.wait_for(".*CIEV: newsms,\"3gpp\",\"ME\",{}.*".format(index),
                                           timeout=test.time_value_in_sec, append=True))
        else:
            test.log.info("===== Check CIEV URC - Expected NOT SEARCH CIEV =====")
            test.expect(test.check_no_urc(".*CIEV: newsms,\"3gpp\",\"ME\",{}.*".format(index)))

    def check_no_urc(test, urc):
        test.wait(test.time_value_in_sec)
        test.dut.at1.read(append=True)
        if re.search(urc, test.dut.at1.last_response):
            test.log.error(f"URC {urc} occurred, Test Failed")
            return False
        else:
            test.log.info(f"URC {urc} NOT occurred, Test Passed")
            return True


if "__main__" == __name__:
    unicorn.main()