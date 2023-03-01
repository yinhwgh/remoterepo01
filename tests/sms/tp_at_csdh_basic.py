#responsible: dariusz.drozdek@globallogic.com, renata.bryla@globallogic.com
#location: Wroclaw
#TC0095686.001

import re
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.attach_to_network import attach_to_network
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.security.lock_unlock_sim import dstl_lock_sim
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.read_sms_message import dstl_read_sms_message
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.send_sms_message import dstl_send_sms_message_from_memory
from dstl.sms.sms_configurations import dstl_get_current_sms_memory
from dstl.sms.write_sms_to_memory import dstl_write_sms_to_memory


class Test(BaseTest):
    """TC0095686.001   TpAtCsdhBasic

    This procedure provides the possibility of basic tests for the test and write command of +CSDH

    1. Check command without and with PIN
    2. Check all parameters and also with invalid values
    3. Check influence of AT&F, AT&V
    4. Check functionality:
    4.1 Test with at+csdh=0 - no detailed header information are shown
    4.2 Test with at+csdh=1 - detailed header information are shown
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_full_functionality_mode(test.dut)
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

    def run(test):
        test.log.h2("Executing script for test case TC0095686.001 TpAtCsdhBasic")
        project = test.dut.project.upper()

        test.log.step("Step 1. Check command without and with PIN")
        test.log.info("===== Check command without PIN =====")
        if project == "COUGAR":
            test.expect(test.dut.at1.send_and_verify("AT+CSDH=?", r".*\+CSDH: (\(0-1\)|\(0,1\)).*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CSDH? ", r".*\+CSDH: 0.*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CSDH=0", ".*OK.*"))
        else:
            test.expect(test.dut.at1.send_and_verify("AT+CSDH=?", r".*\+CMS ERROR: SIM PIN required.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CSDH? ", r".*\+CMS ERROR: SIM PIN required.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CSDH=0", r".*\+CMS ERROR: SIM PIN required.*"))
        test.log.info("===== Check command with PIN =====")
        test.expect(dstl_enter_pin(test.dut))
        test.sleep(15)  # waiting for module to get ready
        test.expect(test.dut.at1.send_and_verify("AT+CSDH=?", r".*\+CSDH: (\(0-1\)|\(0,1\)).*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSDH? ", r".*\+CSDH: 0.*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSDH=0", ".*OK.*"))

        test.log.step("Step 2. Check all parameters and also with invalid values")
        test.log.info("===== Check command with valid values =====")
        test.send_and_check_csdh("0")
        test.send_and_check_csdh("1")
        if test.dut.project.upper() == "COUGAR":
            test.expect(test.dut.at1.send_and_verify("AT+CSDH=", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CSDH?", r".*\+CSDH: 0.*OK.*"))
            test.send_and_check_csdh("1")
        test.log.info("===== Check command with invalid values =====")
        invalid_values = ["-1", "2", "11", "a", "one", "1a", "\"a\"", "\"two\""]
        for i in invalid_values:
            test.send_and_check_csdh(i)
        test.expect(test.dut.at1.send_and_verify("AT+CSDH", r".*CMS ERROR:.*"))
        if test.dut.project.upper() != "COUGAR":
            test.send_and_check_csdh("")

        test.log.step("Step 3. Check influence of AT&F, AT&V")
        test.expect(dstl_select_sms_message_format(test.dut))
        test.send_and_check_csdh("1")
        test.expect(test.dut.at1.send_and_verify("AT&V", r".*\+CSDH: 1.*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSDH? ", r".*\+CSDH: 0.*OK.*"))
        test.send_and_check_csdh("1")
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSDH? ", r".*\+CSDH: 1.*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSDH? ", r".*\+CSDH: 0.*OK.*"))
        test.expect(dstl_select_sms_message_format(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT&V", r".*\+CSDH: 0.*OK.*"))
        test.expect(test.dut.at1.send_and_verify("ATZ", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSDH? ", r".*\+CSDH: 1.*OK.*"))
        test.expect(dstl_select_sms_message_format(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT&V", r".*\+CSDH: 1.*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))

        test.log.step("Step 4. Check functionality:")
        test.expect(attach_to_network(test.dut))
        test.expect(dstl_select_sms_message_format(test.dut))
        test.expect(dstl_get_current_sms_memory(test.dut))
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT+CSMS=1", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))
        test.log.step("Step 4.1 Test with at+csdh=0 - no detailed header information are shown")
        test.send_and_check_csdh("0")
        sms_in_memory_index = dstl_write_sms_to_memory(test.dut, "SMS test", return_index=True)
        test.expect(sms_in_memory_index)
        test.expect(dstl_send_sms_message_from_memory(test.dut, sms_in_memory_index[0]))
        test.expect(dstl_check_urc(test.dut, ".*CMTI.*", timeout=120))
        sms_index = re.search(r"CMTI:.*\",\s*(\d{1,3})", test.dut.at1.last_response)
        test.expect(test.dut.at1.send_and_verify("AT+CMGL=\"ALL\"", ".*OK.*"))
        test.expect(re.search(r".*\+CMGL: \d,\"REC UNREAD\",\"({}|{})\",,\".*\"\s*[\n\r]SMS test.*".format(
            "\\" + test.dut.sim.int_voice_nr, test.dut.sim.nat_voice_nr), test.dut.at1.last_response))
        test.expect(re.search(r".*\+CMGL: \d,\"STO SENT\",\"({}|{})\",,(|\".*\")\s*[\n\r]SMS test.*".format(
            "\\" + test.dut.sim.int_voice_nr, test.dut.sim.nat_voice_nr), test.dut.at1.last_response))
        test.expect(dstl_read_sms_message(test.dut, sms_in_memory_index[0]))
        test.expect(re.search(r".*\+CMGR: \"STO SENT\",\"({}|{})\",\s*[\n\r]SMS test.*".format(
            "\\" + test.dut.sim.int_voice_nr, test.dut.sim.nat_voice_nr), test.dut.at1.last_response))
        test.expect(dstl_read_sms_message(test.dut, sms_index[1]))
        test.expect(re.search(r".*\+CMGR: \"REC READ\",\"({}|{})\",,\".*\"\s*[\n\r]SMS test.*".format(
            "\\" + test.dut.sim.int_voice_nr, test.dut.sim.nat_voice_nr), test.dut.at1.last_response))
        test.expect(test.dut.at1.send_and_verify("AT+CNMI=2,2", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CMSS={}".format(sms_in_memory_index[0]), expect=".*OK.*",
                                                 wait_for=r".*CMT.*", timeout=120))
        test.expect(re.search(r".*\+CMT: \"({}|{})\",,\".*\"\s*[\n\r]SMS test.*".format(
            "\\" + test.dut.sim.int_voice_nr, test.dut.sim.nat_voice_nr), test.dut.at1.last_response))
        test.expect(test.dut.at1.send_and_verify("AT+CNMA", ".*OK.*"))
        test.log.step("Step 4.2 Test with at+csdh=1 - detailed header information are shown")
        test.send_and_check_csdh("1")
        test.expect(test.dut.at1.send_and_verify("AT+CMGL=\"ALL\"", ".*OK.*"))
        test.expect(re.search(r".*\+CMGL: \d,\"REC READ\",\"({}|{})\",,\".*\",(145|129),8\s*[\n\r]SMS test.*".format(
            "\\" + test.dut.sim.int_voice_nr, test.dut.sim.nat_voice_nr), test.dut.at1.last_response))
        test.expect(re.search(
            r".*\+CMGL: \d,\"STO SENT\",\"({}|{})\",,(|\".*\"),(145|129),8\s*[\n\r]SMS test.*".format(
                "\\" + test.dut.sim.int_voice_nr, test.dut.sim.nat_voice_nr), test.dut.at1.last_response))
        test.expect(dstl_read_sms_message(test.dut, sms_in_memory_index[0]))
        test.expect(re.search(r".*\+CMGR: \"STO SENT\",\"({}|{})\",,(145|129),17,0,0,(|\d{}),\"(\+\d+|\d+)\",(145|129),"
                              r"8\s*[\n\r]SMS test.*".format("\\" + test.dut.sim.int_voice_nr,
                              test.dut.sim.nat_voice_nr, "{1,3}"), test.dut.at1.last_response))
        test.expect(dstl_read_sms_message(test.dut, sms_index[1]))
        test.expect(re.search(r".*\+CMGR: \"REC READ\",\"({}|{})\",,\".*\",(145|129),\d{},0,0,\"(\+\d+|\d+)\",(145|129)"
                              r",8\s*[\n\r]SMS test.*".format("\\" + test.dut.sim.int_voice_nr,
                              test.dut.sim.nat_voice_nr, "{1,3}"), test.dut.at1.last_response))
        test.expect(test.dut.at1.send_and_verify("AT+CNMI=2,2", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CMSS={}".format(sms_in_memory_index[0]), expect=".*OK.*",
                                                 wait_for=r".*CMT.*", timeout=120))
        test.expect(re.search(
            r".*\+CMT: \"({}|{})\",,\".*\",(145|129),\d{},0,0,\"(\+\d+|\d+)\",(145|129),8\s*[\n\r]SMS test.*".format(
                "\\" + test.dut.sim.int_voice_nr, test.dut.sim.nat_voice_nr, "{1,3}"), test.dut.at1.last_response))
        test.expect(test.dut.at1.send_and_verify("AT+CNMA", ".*OK.*"))

    def cleanup(test):
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.dut.at1.send_and_verify("AT&F", ".*OK.*")
        test.dut.at1.send_and_verify("AT&W", ".*OK.*")

    def send_and_check_csdh(test, show):
        if show == "0" or show == "1":
            test.expect(test.dut.at1.send_and_verify("AT+CSDH={}".format(show), ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CSDH?", r"\+CSDH: {}.*OK.*".format(show)))
        else:
            test.expect(test.dut.at1.send_and_verify("AT+CSDH={}".format(show), r".*\+CMS ERROR:.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CSDH?", r"\+CSDH: 1.*OK.*"))


if "__main__" == __name__:
    unicorn.main()
