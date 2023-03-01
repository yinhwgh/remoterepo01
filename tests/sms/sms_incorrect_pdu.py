#responsible: sebastian.lupkowski@globallogic.com
#location: Wroclaw
#TC0102495.001, TC0102495.002

import unicorn
import re
from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.auxiliary_sms_functions import _calculate_pdu_length


class Test(BaseTest):
    """
    Try to write, send and read SMS in PDU mode with incorrectly coded content.
    Test based on IPIS100237712, IPIS100245568 and IPIS100278214.

    1. Set DUT to PDU mode (at+cmgf=0),
    2. Try to write PDU with parameter shorter and then longer than actual message length,
    3. Write a PDU message with encoded User Data Length (UDL) value larger than actual Data Length,
    3a. If message was saved then try to read it in PDU and Text mode and then send it,
    4. Write a PDU message with encoded User Data Length (UDL) value smaller than actual Data Length,
    4a. If message was saved then try to read it in PDU and Text mode and then send it,
    5. Write a PDU message with encoded User Data Length (UDL) value larger than maximum message Length
    (max. 160 GSM characters - 0xA0),
    5a. If message was saved then try to read it in PDU and Text mode and then send it,
    6. Write an SMS-Submit with incorrectly modified VP (i.e. in PDU 816022405074FF - FF here stands for nonexistent
    timezone, date and time need to be set later than actual date and time to deliver this message),
    6a. If message was saved then try to read it in PDU and Text mode and then send it,
    7. write an SMS-Deliver with incorrect SCTS (i.e. in PDU 816022405074FF - FF here stands for nonexistent timezone),
    7a. If message was saved then try to read it in PDU and Text mode,
    8. Write an SMS-Deliver message with encoded User Data Length (UDL) value larger than maximum message Length
    (max. 160 GSM characters - 0xA0),
    8a. If message was saved then try to read it in PDU and Text mode.
    """

    cmd_ok = ".*OK.*"
    cmd_err = ".*ERROR.*"
    reference_pdu = "069121436587F91100098189674523F10000A710F4F29C0E6A97E7F3F0B90C8212AB"
    timeout = 120
    new_timestamp = ''

    def setup(test):
        test.log.h2("Starting TP for TC0102495.001/.002 - SmsIncorrectPDU")
        test.log.info("Preparing module")
        test.prepare_module()

    def run(test):
        test.log.step("1. Set DUT to PDU mode (at+cmgf=0)")
        test.expect(dstl_select_sms_message_format(test.dut, 'PDU'))

        test.log.step("2. Try to write PDU with parameter shorter and then longer than actual message length")
        test.log.info("=== +CMGW with <length> shorter than actual PDU (length = 27) ===")
        test.expect(test.dut.at1.send_and_verify('AT+CMGW=26', '.*>.*', wait_for='.*>.*'))
        test.expect(test.dut.at1.send_and_verify(test.reference_pdu, end="\u001A", expect=test.cmd_err))

        test.log.info("=== +CMGW with <length> longer than actual PDU (length = 27) ===")
        test.expect(test.dut.at1.send_and_verify('AT+CMGW=28', '.*>.*', wait_for='.*>.*'))
        test.expect(test.dut.at1.send_and_verify(test.reference_pdu, end="\u001A", expect=test.cmd_err))

        test.log.step("3. Write a PDU message with encoded User Data Length (UDL) value larger than actual Data Length")
        new_msg = "{}1100{}0000A711{}".format(test.dut.sim.sca_pdu, test.dut.sim.pdu, test.reference_pdu[40:])
        substep = "3a. If message was saved then try to read it in PDU and Text mode and then send it"
        test.execute_substep(new_msg, substep)

        test.log.step("4. Write a PDU message with encoded User Data Length (UDL) value smaller than actual "
                      "Data Length")
        new_msg = "{}1100{}0000A70F{}".format(test.dut.sim.sca_pdu, test.dut.sim.pdu, test.reference_pdu[40:])
        substep = "4a. If message was saved then try to read it in PDU and Text mode and then send it"
        test.execute_substep(new_msg, substep)

        test.log.step("5. Write a PDU message with encoded User Data Length (UDL) value larger than maximum "
                      "message Length")
        new_msg = "{}1100{}0000A7A1{}".format(test.dut.sim.sca_pdu, test.dut.sim.pdu, test.reference_pdu[40:])
        substep = "5a. If message was saved then try to read it in PDU and Text mode and then send it"
        test.execute_substep(new_msg, substep)

        test.log.step("6. Write an SMS-Submit with incorrectly modified VP")
        test.new_timestamp = test.get_new_timestamp()
        if test.new_timestamp:
            new_msg = "{}1900{}0000{}{}".format(test.dut.sim.sca_pdu, test.dut.sim.pdu, test.new_timestamp,
                                                test.reference_pdu[38:])
            substep = "6a. If message was saved then try to read it in PDU and Text mode and then send it"
            test.execute_substep(new_msg, substep)
        else:
            test.log.error("Could not create correct timestamp. Step cannot be executed")

        test.log.step("7. write an SMS-Deliver with incorrect SCTS")
        if test.new_timestamp:
            new_msg = "{}04{}0000{}{}".format(test.dut.sim.sca_pdu, test.dut.sim.pdu, test.new_timestamp,
                                              test.reference_pdu[38:])
            substep = "7a. If message was saved then try to read it in PDU and Text mode"
            test.execute_substep(new_msg, substep, False)
        else:
            test.log.error("Could not create correct timestamp. Step cannot be executed")

        test.log.step("8. Write an SMS-Deliver message with encoded User Data Length (UDL) value larger than maximum "
                      "message Length")
        if test.new_timestamp:
            new_msg = "{}04{}0000{}A1{}".format(test.dut.sim.sca_pdu, test.dut.sim.pdu, test.new_timestamp,
                                                test.reference_pdu[40:])
            substep = "8a. If message was saved then try to read it in PDU and Text mode"
            test.execute_substep(new_msg, substep, False)
        else:
            test.log.error("Could not create correct timestamp. Step cannot be executed")

    def cleanup(test):
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.dut.at1.send_and_verify("AT&F", test.cmd_ok)
        test.dut.at1.send_and_verify("AT&W", test.cmd_ok)

    def prepare_module(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_bootloader(test.dut)
        test.expect(dstl_register_to_network(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", test.cmd_ok))
        test.expect(test.dut.at1.send_and_verify('AT+CNMI=2,1', test.cmd_ok))
        test.expect(dstl_set_scfg_urc_dst_ifc(test.dut))
        test.expect(dstl_set_preferred_sms_memory(test.dut, 'ME'))
        test.expect(dstl_delete_all_sms_messages(test.dut))

    def write_send_pdu_message(test, content, command):
        test.expect(test.dut.at1.send_and_verify('AT+{}={}'.format(command, _calculate_pdu_length(content)), '.*>.*',
                                                 wait_for='.*>.*'))
        return test.dut.at1.send_and_verify(content, end="\u001A", expect=test.cmd_ok, timeout=test.timeout)

    def execute_substep(test, message, description, send=True):
        if test.write_send_pdu_message(message, 'CMGW'):
            test.log.step(description)
            index = re.search(r".*CMGW:.*(\d{1,3}).*", test.dut.at1.last_response).group(1)
            if index is not None:
                test.expect(test.dut.at1.send_and_verify("AT+CMGR={}".format(index), test.cmd_ok))
                test.log.info("No content check - it may be malformed")
                test.expect(dstl_select_sms_message_format(test.dut, 'Text'))
                test.expect(test.dut.at1.send_and_verify("AT+CMGR={}".format(index), test.cmd_ok))
                test.log.info("No content check - it may be malformed")
                test.expect(dstl_select_sms_message_format(test.dut, 'PDU'))
                if send:
                    test.expect(test.dut.at1.send_and_verify("AT+CMSS={}".format(index), test.cmd_ok,
                                                             timeout=test.timeout))
                    if dstl_check_urc(test.dut, ".*\+CMTI:.*\"ME\",\s*\d{1,3}.*", test.timeout):
                        received_index = re.search(r".*CMTI:.*(\d{1,3}).*", test.dut.at1.last_response).group(1)
                        test.expect(test.dut.at1.send_and_verify("AT+CMGR={}".format(received_index), test.cmd_ok))
                        test.log.info("No content check - it may be malformed")
                    else:
                        test.log.info("Message not received - NETWORK DEPENDENT!")
            else:
                test.log.error("No index found")
        else:
            test.log.info("Message not saved - PLATFORM DEPENDENT!")
            test.log.info("Checking if module does not crash or restart")
            test.sleep(10)  # waiting for possible module crash
            test.expect(not re.search(r".*SYSTART.*|.*EXIT.*", test.dut.at1.last_response))

    def get_new_timestamp(test):
        test.log.info("=== Send a message to itself and get current timestamp from it ===")
        test_message = "{}1100{}0000A704F4F29C0E".format(test.dut.sim.sca_pdu, test.dut.sim.pdu)
        test.write_send_pdu_message(test_message, "CMGS")
        if test.expect(dstl_check_urc(test.dut, ".*\+CMTI:.*\"ME\",\s*\d{1,3}.*", test.timeout)):
            received_index = re.search(r".*CMTI:.*(\d{1,3}).*", test.dut.at1.last_response).group(1)
            test.expect(test.dut.at1.send_and_verify("AT+CMGR={}".format(received_index), test.cmd_ok))
            scts = re.search(r".*{}0000(\d{{12}})".format(test.dut.sim.pdu), test.dut.at1.last_response).group(1)
            hours = int("{}{}".format(scts[7], scts[6]))
            if hours == 23:
                hours = "00"
            else:
                hours += 1
                hours = str(hours)
            if len(hours) == 1:
                hours = "0" + hours
            return "{}{}{}".format(scts[0:6], hours[::-1], scts[8:])
        else:
            test.log.error("Unable to create new timestamp. Steps 6-8 won't be executed due to lack of "
                           "correct timestamp")
            return False


if "__main__" == __name__:
    unicorn.main()
