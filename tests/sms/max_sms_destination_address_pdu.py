#responsible: renata.bryla@globallogic.com
#location: Wroclaw
#TC0104853.001, TC0104853.002

import re
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.auxiliary_sms_functions import _calculate_pdu_length
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory

class Test(BaseTest):
    """
    Check a module behavior with usage of longer address parameter in PDU message. According to E.164 recommendation
    maximum length is 15 digits plus prefix (up to 5 digits e.g. in Finland or one "+" sign instead digital prefix).

    Precondition:
    1. PIN code is entered
    2. Module registered to the network
    3. Sms memory storage empty
    4. PDU mode set
    5. SCA_PDU prepared (SMS Service Center number in PDU mode)

    Description:
    1. Write to memory PDU message with 20 digits in destination address
    i.e. AT+CMGW=22
    [SCA_PDU]+110014812143658709214365870900000004F4F29C0E
    2. Write to memory message with 15 digits and "+"
    i.e. AT+CMGW=20
    [SCA_PDU]+11000F9121436587092143F500000004F4F29C0E
    3. Write to memory message with 30 digits
    i.e. AT+CMGW=27
    [SCA_PDU]+11001E8121436587092143658709214365870900000004F4F29C0E
    4. Read messages written to memory and check if is correct in PDU and Text mode
    5. Send message with 20 digits by at+cmgs command
    i.e. at+cmgs=22
    [SCA_PDU]+110014812143658709214365870900000004F4F29C0E
    6. Send message with 15 digits and "+" by at+cmgs command
    i.e. AT+CMGS=20
    [SCA_PDU]+11000F9121436587092143F500000004F4F29C0E
    7. Send message with 30 digits by at+cmgs command
    i.e. AT+CMGS=27
    [SCA_PDU]+11001E8121436587092143658709214365870900000004F4F29C0E
    8. Send from memory message from point 2 with new 20 digits
    i.e. at+cmss=0,"12345678901234567890"
    9. Send from memory message from point 2 with new 15 digits and "+"
    i.e. at+cmss=0,"+123456789012345"
    10. Send from memory message from point 2 with new 30 digits
    i.e. at+cmss=0,"123456789012345678901234567890"
    11. Send from memory message from point 2 without changing
    i.e. at+cmss=0

    For modules with support of concatenated sms commands - no PDU syntax is available.
    Standard cmgw and cmgs commands are used so no additional steps are done here.

    Steps with unsupported commands may be omitted, i.e. Koala supports only directly sent messages.
    """

    SMS_TIMEOUT = 360
    DA_15_PDU = "0F9121436587092143F5"
    DA_15_TEXT = "+123456789012345"
    DA_20_PDU = "148121436587092143658709"
    DA_20_TEXT = "12345678901234567890"
    DA_30_PDU = "1E81214365870921436587092143658709"
    DA_30_TEXT = "123456789012345678901234567890"
    SMS_CONTENT = "F4F29C0E"
    OK_RESPONSE = ".*OK.*"
    CMS_ERROR_RESPONSE = ".*CMS ERROR.*"
    OK_OR_CMS_ERROR_RESPONSE = ".*OK.*|.*CMS ERROR.*"

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_bootloader(test.dut)
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_select_sms_message_format(test.dut, 'PDU'))
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", test.OK_RESPONSE))
        if test.dut.project.upper() != "VIPER":
            test.expect(test.dut.at1.send_and_verify('AT^SCFG="Sms/AutoAck","0"', test.OK_RESPONSE))
        test.sca_pdu = test.dut.sim.sca_pdu

    def run(test):
        if test.dut.project.upper() == "VIPER":
            test.log.info('TC0104853.002 - MaxSmsDestinationAddressPDU')
        else:
            test.log.info('TC0104853.001 - MaxSmsDestinationAddressPDU')

        test.log.step("Step 1. Write to memory PDU message with 20 digits in destination address \r"
                      "i.e. AT+CMGW=22 \r[SCA_PDU]+110014812143658709214365870900000004F4F29C0E")
        index_da_20 = test.save_or_send_sms_pdu("CMGW", test.DA_20_PDU, test.OK_RESPONSE)

        test.log.step('Step 2. Write to memory message with 15 digits and "+" \r'
                      'i.e. AT+CMGW=20 \r[SCA_PDU]+11000F9121436587092143F500000004F4F29C0E')
        index_da_15 = test.save_or_send_sms_pdu("CMGW", test.DA_15_PDU, test.OK_RESPONSE)

        test.log.step("Step 3. Write to memory message with 30 digits \r"
                      "i.e. AT+CMGW=27 \r[SCA_PDU]+11001E8121436587092143658709214365870900000004F4F29C0E")
        test.save_or_send_sms_pdu("CMGW", test.DA_30_PDU, test.CMS_ERROR_RESPONSE)

        test.log.step("Step 4. Read messages written to memory and check if is correct in PDU and Text mode")
        test.log.info("===== Read messages written to memory in PDU mode =====")
        test.read_sms(index_da_20, "PDU", test.DA_20_PDU)
        test.read_sms(index_da_15, "PDU", test.DA_15_PDU)
        test.log.info("===== Read messages written to memory in Text mode =====")
        test.expect(dstl_select_sms_message_format(test.dut))
        test.read_sms(index_da_20, "Text", test.DA_20_TEXT)
        test.read_sms(index_da_15, "Text", test.DA_15_TEXT)
        test.log.info("===== Back to PDU mode =====")
        test.expect(dstl_select_sms_message_format(test.dut, 'PDU'))

        test.log.step("Step 5. Send message with 20 digits by at+cmgs command \r"
                      "i.e. at+cmgs=22 \r[SCA_PDU]+110014812143658709214365870900000004F4F29C0E")
        test.save_or_send_sms_pdu("CMGS", test.DA_20_PDU, test.OK_OR_CMS_ERROR_RESPONSE)

        test.log.step('Step 6. Send message with 15 digits and "+" by at+cmgs command \r'
                     'i.e. AT+CMGS=20 \r[SCA_PDU]+11000F9121436587092143F500000004F4F29C0E')
        test.save_or_send_sms_pdu("CMGS", test.DA_15_PDU, test.OK_OR_CMS_ERROR_RESPONSE)

        test.log.step("Step 7. Send message with 30 digits by at+cmgs command \r"
                      "i.e. AT+CMGS=27 \r[SCA_PDU]+11001E8121436587092143658709214365870900000004F4F29C0E")
        test.save_or_send_sms_pdu("CMGS", test.DA_30_PDU, test.CMS_ERROR_RESPONSE)

        test.log.step('Step 8. Send from memory message from point 2 with new 20 digits \r'
                      'i.e. at+cmss=0,"12345678901234567890"')
        test.send_msg_from_memory("{},{}".format(index_da_20, test.DA_20_TEXT), test.OK_OR_CMS_ERROR_RESPONSE)

        test.log.step('Step 9. Send from memory message from point 2 with new 15 digits and "+" \r'
                      'i.e. at+cmss=0,"+123456789012345"')
        test.send_msg_from_memory("{},{}".format(index_da_20, test.DA_15_TEXT), test.OK_OR_CMS_ERROR_RESPONSE)

        test.log.step('Step 10. Send from memory message from point 2 with new 30 digits \r'
                      'i.e. at+cmss=0,"123456789012345678901234567890"')
        test.send_msg_from_memory("{},{}".format(index_da_20, test.DA_30_TEXT), test.CMS_ERROR_RESPONSE)

        test.log.step("Step 11. Send from memory message from point 2 without changing \ri.e. at+cmss=0")
        test.send_msg_from_memory("{}".format(index_da_20), test.OK_OR_CMS_ERROR_RESPONSE)

    def cleanup(test):
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.dut.at1.send_and_verify("AT&F", test.OK_RESPONSE)
        test.dut.at1.send_and_verify("AT&W", test.OK_RESPONSE)

    def get_sms_index(test, regex, message):
        response_content = test.expect(re.search(regex, test.dut.at1.last_response))
        if response_content:
            msg_index = response_content.group(1)
            test.log.info("SMS index for {} is: {}".format(message, msg_index))
            return int(msg_index)
        else:
            return test.log.error("Fail to get value of {}".format(message))

    def save_or_send_sms_pdu(test, command, da_pdu_num, exp_resp):
        sms_pdu = "{}1100{}00000004{}".format(test.sca_pdu, da_pdu_num, test.SMS_CONTENT)
        test.log.info("SMS PDU: {}".format(sms_pdu))
        test.dut.at1.send_and_verify("AT+{}={}".format(command, _calculate_pdu_length(sms_pdu)), expect=">")
        test.expect(test.dut.at1.send_and_verify(sms_pdu, end="\u001A", expect=exp_resp, timeout=test.SMS_TIMEOUT))
        if exp_resp == test.CMS_ERROR_RESPONSE:
            return test.log.info("CMS ERROR as expected.")
        else:
            if "CMGW" in command:
                if exp_resp == test.OK_RESPONSE:
                    index = test.get_sms_index(r".*CMGW:\s*(\d{1,3})", "CMGW")
                    return index
            else:
                return test.log.info("Send Message could NOT be accepted by module or could be accepted, "
                                     "but probably rejected by network because of random number.")

    def read_sms(test, index, msg_format, da_number):
        if "Text" in msg_format:
            if da_number == test.DA_15_TEXT:
                da_nr = "\"\{}\"".format(da_number)
            else:
                da_nr = "\"{}\"".format(da_number)
            regex = ".*CMGR:\s*\"STO UNSENT\",{},\s*[\n\r]test[\n\r].*".format(da_nr)
        else:
            regex = ".*CMGR:\s*2,,\d{{1,3}}\s*[\n\r]{}1100{}00000004{}".format(test.sca_pdu, da_number, test.SMS_CONTENT)
        test.expect(test.dut.at1.send_and_verify("AT+CMGR={}".format(index), test.OK_RESPONSE))
        test.log.info("Expected REGEX: {}".format(regex))
        test.expect(re.search(regex, test.dut.at1.last_response))

    def send_msg_from_memory(test, parameters, exp_resp):
        test.expect(test.dut.at1.send_and_verify("AT+CMSS={}".format(parameters), exp_resp, timeout=test.SMS_TIMEOUT))
        if exp_resp == test.CMS_ERROR_RESPONSE:
            return test.log.info("CMS ERROR as expected.")
        else:
            return test.log.info("Send Message could NOT be accepted by module or could be accepted, "
                                 "but probably rejected by network because of random number.")


if "__main__" == __name__:
    unicorn.main()