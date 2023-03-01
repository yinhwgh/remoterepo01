#responsible: renata.bryla@globallogic.com
#location: Wroclaw
#TC0092178.001

import unicorn
import re
from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.security.lock_unlock_sim import dstl_lock_sim
from dstl.sms.auxiliary_sms_functions import _calculate_pdu_length
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.sms_memory_capacity import dstl_get_sms_memory_capacity
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_network
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.write_sms_to_memory import dstl_write_sms_to_memory
from dstl.sms.delete_sms import dstl_delete_all_sms_messages


class Test(BaseTest):
    """TC0092178.001   AtSmgrBasic
    This procedure provides the possibility of basic tests for the test and write command of ^SMGR similar to +CMGR
    command with only one functional difference Status "REC UNREAD" of a short message is not overwritten to "REC READ".
    Description:
    Step 1: Check command without and with PIN
    Step 2: Check all parameters and also with invalid values
    Step 3: Check functionality by creating, sending and receiving SMS and reading them in PDU and text mode

    Expected results:
    AT command should be implemented and work as expected. Difference to +CMGR:
    Status "REC UNREAD" of a short message is not overwritten to "REC READ".
    """

    SMS_TIMEOUT = 360
    LIST_MSG_INDEX = []

    def setup(test):
        test.log.h2("Executing script for test case TC0092178.001 AtSmgrBasic")
        test.log.info('Preparing DUT for test')
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
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
        test.log.step('1: Check command without and with PIN')
        test.log.info("===== Check Test and Write SMGR command without PIN =====")
        test.expect(test.dut.at1.send_and_verify('AT^SMGR=?', '.*CMS ERROR.*SIM PIN required.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SMGR=1', '.*CMS ERROR.*SIM PIN required.*'))

        test.log.info("===== Check Test and Write SMGR command with PIN on an empty SMS memory =====")
        test.expect(dstl_enter_pin(test.dut))
        test.sleep(5)
        test.expect(dstl_set_preferred_sms_memory(test.dut, preferred_storage='ME', memory_index='All'))
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(test.dut.at1.send_and_verify('AT^SMGR=?', '.*OK.*'))
        test.expect(not re.search(".*SMGR:.*", test.dut.at1.last_response))
        test.expect(test.dut.at1.send_and_verify('AT^SMGR=1', '.*OK.*'))
        test.expect(not re.search(".*SMGR:.*", test.dut.at1.last_response))

        test.log.step('2: Check all parameters and also with invalid values ')
        test.log.info("===== Get Storage Capacity value =====")
        storage_capacity = dstl_get_sms_memory_capacity(test.dut, 1)
        test.log.info("Storage Capacity value: {}".format(storage_capacity))

        test.log.info("===== Check SMGR command with invalid values =====")
        if test.dut.platform.upper() == "QCT":
            test.log.info("For QCT platform, start index of message is value 0, "
                          "so first value out of index range is equal Storage Capacity value")
            test.expect(test.dut.at1.send_and_verify('AT^SMGR={}'.format(storage_capacity),
                                                     '.*CMS ERROR: invalid memory index.*'))
        else:
            test.log.info("For non-QCT platform, start index of message is value 1, "
                          "so first value out of index range is equal Storage Capacity value")
            test.expect(test.dut.at1.send_and_verify('AT^SMGR={}'.format(str(int(storage_capacity) + 1)),
                                                     '.*CMS ERROR: invalid memory index.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SMGR=1000', '.*CMS ERROR: invalid memory index.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SMGR=-0', '.*CMS ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SMGR=ABC', '.*CMS ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SMGR=1,37537', '.*CMS ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SMGR', '.*CMS ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SMGR?', '.*CMS ERROR.*'))

        test.log.info("===== Check Write SMGR command with valid values =====")
        if test.dut.platform.upper() == "QCT":
            for index in range(int(storage_capacity)):
                test.expect(test.dut.at1.send_and_verify('AT^SMGR={}'.format(index), '.*OK.*'))
        else:
            for index in range((int(storage_capacity) + 1)):
                test.expect(test.dut.at1.send_and_verify('AT^SMGR={}'.format(index + 1), '.*OK.*'))

        test.log.step('3: Check functionality by creating, sending and receiving SMS '
                      'and reading them in PDU and text mode')
        test.prepare_module_to_functional_test()
        test.log.info("===== Write messages and Send messages from memory =====")
        test.write_or_send_msg("WRITE")
        test.write_or_send_msg("WRITE")
        test.write_or_send_msg("SEND from memory")
        test.write_or_send_msg("SEND from memory")

        if len(test.LIST_MSG_INDEX) == 4:
            if test.LIST_MSG_INDEX[3]:
                test.log.info("===== Read last delivered message via CMGR to change Status to REC READ =====")
                test.expect(test.dut.at1.send_and_verify('AT+CMGR={}'.format(test.LIST_MSG_INDEX[3]), '.*OK.*'))
            else:
                test.log.info("===== Message NOT in memory - index list is empty =====")

            test.log.info("===== Check Write SMGR command in PDU mode =====")
            test.expect(dstl_select_sms_message_format(test.dut, 'PDU'))
            test.read_sms_in_pdu(test.LIST_MSG_INDEX[0], 2)
            test.read_sms_in_pdu(test.LIST_MSG_INDEX[1], 3)
            test.read_sms_in_pdu(test.LIST_MSG_INDEX[2], 0)
            test.read_sms_in_pdu(test.LIST_MSG_INDEX[3], 1)

            test.log.info("===== Check Write SMGR command in text mode and with show header (csdh=1) =====")
            test.expect(dstl_select_sms_message_format(test.dut, 'Text'))
            test.expect(test.dut.at1.send_and_verify('AT+CSDH=1', '.*OK.*'))
            test.read_sms_in_text(test.LIST_MSG_INDEX[0], test.prepare_regex_text_mode("STO UNSENT", csdh=1))
            test.read_sms_in_text(test.LIST_MSG_INDEX[1], test.prepare_regex_text_mode("STO SENT", csdh=1))
            test.read_sms_in_text(test.LIST_MSG_INDEX[2], test.prepare_regex_text_mode("REC UNREAD", csdh=1))
            test.read_sms_in_text(test.LIST_MSG_INDEX[3], test.prepare_regex_text_mode("REC READ", csdh=1))

            test.log.info("===== Check Write SMGR command in text mode and without show header (csdh=0) =====")
            test.expect(dstl_select_sms_message_format(test.dut, 'Text'))
            test.expect(test.dut.at1.send_and_verify('AT+CSDH=0', '.*OK.*'))
            test.read_sms_in_text(test.LIST_MSG_INDEX[0], test.prepare_regex_text_mode("STO UNSENT", csdh=0))
            test.read_sms_in_text(test.LIST_MSG_INDEX[1], test.prepare_regex_text_mode("STO SENT", csdh=0))
            test.read_sms_in_text(test.LIST_MSG_INDEX[2], test.prepare_regex_text_mode("REC UNREAD", csdh=0))
            test.read_sms_in_text(test.LIST_MSG_INDEX[3], test.prepare_regex_text_mode("REC READ", csdh=0))
        else:
            test.expect(False, msg="===== NOT ALL MESSAGE STATUSES IN MEMORY =====")

    def cleanup(test):
        test.log.info('===== Delete SMS from memory and restore values =====')
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))

    def prepare_module_to_functional_test(test):
        test.log.info("===== Prepare module to functional test =====")
        test.expect(dstl_register_to_network(test.dut))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="SMS/AutoAck",0', ".*O.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CSCS="GSM"', ".*OK.*"))
        test.expect(dstl_set_sms_center_address(test.dut, test.dut.sim.sca_int))
        test.expect(test.dut.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CSMS=1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*"))
        test.expect(dstl_select_sms_message_format(test.dut, 'Text'))

    def get_sms_index(test, module, regex, command):
        response_content = test.expect(re.search(regex, module.at1.last_response))
        if response_content:
            msg_index = response_content[1]
            test.log.info("===== SMS index for {} is: {} =====".format(command, msg_index))
            return int(msg_index)
        else:
            return test.log.error("Fail to get value of {}".format(command))

    def write_or_send_msg(test, msg_type):
        if msg_type == "WRITE":
            test.expect(dstl_write_sms_to_memory(test.dut, sms_text='Test SMS SMGR', sms_format='Text'))
            if dstl_check_urc(test.dut, ".*CMGW.*"):
                test.LIST_MSG_INDEX.append(test.get_sms_index(test.dut, r".*CMGW:\s*(\d{1,3})", "CMGW"))
                return test.LIST_MSG_INDEX
            else:
                test.log.error("===== Message was not saved =====")
        else:
            test.expect(test.dut.at1.send_and_verify('AT+CMSS={}'.format(test.LIST_MSG_INDEX[1]), '.*OK.*'))
            if dstl_check_urc(test.dut, ".*CMTI.*", timeout=test.SMS_TIMEOUT):
                test.LIST_MSG_INDEX.append(test.get_sms_index(test.dut, r".*CMTI.*,\s*(\d{1,3})", "CMTI"))
                return test.LIST_MSG_INDEX
            else:
                test.log.error("Message was not received")

    def read_sms_in_text(test, msg_index, expected_resp):
        if msg_index is not None:
            test.expect(test.dut.at1.send_and_verify("AT^SMGR={}".format(msg_index), "{}".format(expected_resp)))
            if re.search("{}".format(expected_resp), test.dut.at1.last_response):
                test.expect(True, msg="Correct message content")
            else:
                test.log.error("===== Incorrect message content =====")
        else:
            test.log.info("===== Message NOT in memory - index list is empty =====")

    def prepare_regex_text_mode(test, status, csdh):
        if status == "STO UNSENT" or status == "STO SENT":
            if csdh == 1:
                return r"\^SMGR: \"{0}\",\"\{1}\",,145,17,0,0,167,\"\{2}\",145,13\s*[\n\r]Test SMS SMGR\s*[\n\r].*OK.*".\
                    format(status, test.dut.sim.int_voice_nr, test.dut.sim.sca_int)
            elif csdh == 0:
                return r"\^SMGR: \"{0}\",\"\{1}\",\s*[\n\r]Test SMS SMGR\s*[\n\r].*OK.*".\
                    format(status, test.dut.sim.int_voice_nr)
        elif status == "REC UNREAD" or status == "REC READ":
            if csdh == 1:
                return r"\^SMGR: \"{0}\",\"\{1}\",,\".*\",145,\d{{1,3}},0,0,\".*\",145,13\s*[\n\r]Test SMS SMGR\s*"\
                       r"[\n\r].*OK.*".format(status, test.dut.sim.int_voice_nr)
            elif csdh == 0:
                return r"\^SMGR: \"{0}\",\"\{1}\",,\".*\"\s*[\n\r]Test SMS SMGR\s*.*OK.*".\
                    format(status, test.dut.sim.int_voice_nr)

    def read_sms_in_pdu(test, msg_index, status):
        content = "D4F29C0E9A36A7A069F32805"
        test.dut.at1.send_and_verify("AT^SMGR={}".format(msg_index), ".*OK.*")
        if msg_index is not None:
            msg_content = re.search(r"\S+{}".format(content), test.dut.at1.last_response)[0]
            if msg_content:
                regex_pdu = r".*\^SMGR: {0},,{1}\s*[\n\r].*{2}.*{3}\s*[\n\r].*" \
                    .format(status, _calculate_pdu_length(msg_content), test.dut.sim.pdu, content)
                test.log.info("Expected REGEX: {}".format(regex_pdu))
                test.expect(re.search(regex_pdu, test.dut.at1.last_response))
            else:
                test.expect(False, msg="Message not found")
        else:
            test.log.info("===== Message NOT in memory - index list is empty =====")


if "__main__" == __name__:
    unicorn.main()
