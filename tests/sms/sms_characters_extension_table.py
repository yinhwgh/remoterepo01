#responsible: dariusz.drozdek@globallogic.com
#location: Wroclaw
#TC0083121.001

import re
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.send_sms_message import dstl_send_sms_message_from_memory


class Test(BaseTest):
    """TC0083121.001    SmsCharactersExtensionTable

    Test if GSM extension table characters ~[]\|{}^ and euro currency characters can be sent correctly in sms.

    - Send 7bit GSM SMS directly from first module in PDU mode containing characters: ~[]\|{}^ and €
    (euro currency character)
    Example content of 3gpp format SMS - 9BDE86B7F16D5E1BE006B5496D289B7219.
    If product works in 3gpp2 format use appropriate PDU SMS coding format.
    - Read received sms in text mode on second module.
    Additional steps due to issue from IPIS100312922:
    - Save the same message in memory using at+cmgw and then send it to second module using at+cmss=<index>.
    - Send the same message using at+cmss=<index>,<da>
    - Repeat with a mobile phone as a receiver.
    """

    def setup(test):
        for module in [test.dut, test.r1]:
            dstl_detect(module)
            dstl_get_bootloader(module)
            dstl_get_imei(module)
            test.expect(dstl_register_to_network(module))
            dstl_delete_all_sms_messages(module)
            test.expect(module.at1.send_and_verify("AT+CSCS=\"GSM\"", "OK"))
            test.expect(module.at1.send_and_verify("AT+CSMS=0", ".*OK.*"))
            test.expect(module.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*"))
            test.expect(module.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))
            test.expect(module.at1.send_and_verify("AT+CSCA=\"{}\"".format(module.sim.sca_int), ".*OK.*"))
            if module == test.r1:
                test.expect(dstl_select_sms_message_format(module))
            else:
                test.expect(dstl_select_sms_message_format(module, "PDU"))

    def run(test):
        pdu_content = "9BDE86B7F16D5E1BE006B5496D289B32"
        text_content = r"\\1B=\\1B<\\1B>\\1B\/\\1B@\\1B\(\\1B\)\\1B\\14\\1Be"

        test.log.step("- Send 7bit GSM SMS directly from first module in PDU mode containing characters: ~[]\|{}^ and "
                      "€ (euro currency character)")
        test.expect(test.dut.at1.send_and_verify("AT+CMGS=29", ">"))
        if ">" in test.dut.at1.last_response:
            test.expect(test.dut.at1.send_and_verify(
                '{}0100{}000012{}'.format(test.dut.sim.sca_pdu, test.r1.sim.pdu, pdu_content),
                end="\u001A", expect=".*OK|ERROR.*", timeout=30))
        else:
            test.expect(test.dut.at1.send("\u001A"))

        test.log.step(" - Read received sms in text mode on second module.")
        test.read_sms(test.r1, text_content, test.dut.sim.int_voice_nr[-9:])

        test.log.step("Additional steps due to issue from IPIS100312922:")
        test.log.step("- Save the same message in memory using at+cmgw and then send it to second module using "
                      "at+cmss=<index>.")
        test.expect(test.dut.at1.send_and_verify("AT+CMGW=29", ">"))
        if ">" in test.dut.at1.last_response:
            test.expect(test.dut.at1.send_and_verify('{}0100{}000012{}'.format(
                test.dut.sim.sca_pdu, test.r1.sim.pdu, pdu_content), end="\u001A", expect=".*OK|ERROR.*", timeout=20))

        sms_index = re.search(r"CMGW: (\d{1,3})", test.dut.at1.last_response)
        if sms_index:
            test.expect(test.dut.at1.send_and_verify("AT+CMGR={}".format(sms_index.group(1)),
                                                     ".*{}.*{}.*OK.*".format(test.r1.sim.pdu, pdu_content)))
            test.expect(dstl_send_sms_message_from_memory(test.dut, int(sms_index.group(1))))
            test.read_sms(test.r1, text_content, test.dut.sim.int_voice_nr[-9:])

            test.log.step("- Send the same message using at+cmss=<index>,<da>")
            test.expect(dstl_send_sms_message_from_memory(test.dut, int(sms_index.group(1)), test.r1.sim.int_voice_nr))
            test.read_sms(test.r1, text_content, test.dut.sim.int_voice_nr[-9:])

            test.log.step("- Repeat with a mobile phone as a receiver.")
            test.log.info("Enter Phone number for receiving SMS ")
            mobile_number = input()
            test.expect(dstl_send_sms_message_from_memory(test.dut, int(sms_index.group(1)), mobile_number.strip()))
            test.sleep(5)   # Timer for read SMS on mobile phone
            test.log.info("SMS content on mobile phone should be : ~[]\|{}^€")
            test.log.info("Does SMS content is correct? Yes or No")
            answer = input()
            test.log.info(answer.upper())
            test.expect(answer.upper() == "YES")
        else:
            test.expect(False, msg="Module does not save SMS in memory")


    def cleanup(test):
        dstl_delete_all_sms_messages(test.dut)
        dstl_delete_all_sms_messages(test.r1)
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))

    def read_sms(test, module, msg, da):
        test.expect(module.at1.wait_for(".*CMTI.*"))
        sms_index = re.search(r".*\",\s*(\d{1,3})", module.at1.last_response)
        if sms_index:
            test.expect(module.at1.send_and_verify("AT+CMGR={}".format(sms_index.group(1)),
                                                   ".*{}.*{}.*OK.*".format(da, msg)))
        else:
            test.expect(False, msg="Module does not receive SMS in required timeout")


if "__main__" == __name__:
    unicorn.main()
