#responsible: renata.bryla@globallogic.com
#location: Wroclaw
#TC0103288.001

import re
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.list_sms_message import dstl_list_sms_messages_from_preferred_memory
from dstl.sms.read_sms_message import dstl_read_sms_message
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory


class Test(BaseTest):
    """TC0103288.001    SendReceive16BitPduBasic

    This procedure provides the possibility of basic test steps for sending and receiving 16-bit messages in PDU mode.

    Check functionality by sending and receiving SMS in PDU mode with 16-bit coding schemes.
    0. Delete all SMS from DUT and Remote memory
    1. Set PDU mode on DUT and Remote ( at+cmgf=0 )
    2. Set desired SMS URCs presentation on DUT and Remote (at+cnmi=2,1)
    3. On DUT Encode 16-bit message in PDU and send it from DUT to Remote (at+cmgs="the_length_of_the_message",
    input "pdu_data" and confirm with ctrl+z)
    4. Check if SMS was sent correctly from DUT (wait for +CMGS) and received correctly on Remote
    5. On Remote Encode 16-bit message in PDU and send it from Remote to DUT
    6. Check received messages on the Remote (wait for +CMTI URC and use commands at+cmgl / at+cmgr=<index> )
    """

    def setup(test):
        test.content = "00540045005300540053004D0053"
        test.prepare_module(test.dut)
        test.prepare_module(test.r1)

    def run(test):
        test.log.step("0. Delete all SMS from DUT and Remote memory")
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_delete_all_sms_messages(test.r1))

        test.log.step("1. Set PDU mode on DUT and Remote ( at+cmgf=0 )")
        test.expect(dstl_select_sms_message_format(test.dut, 'PDU'))
        test.expect(dstl_select_sms_message_format(test.r1, 'PDU'))

        test.log.step("2. Set desired SMS URCs presentation on DUT and Remote (at+cnmi=2,1)")
        test.expect(test.dut.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*"))
        test.expect(test.r1.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*"))

        test.log.step("3. On DUT Encode 16-bit message in PDU and send it from DUT to Remote "
                      "(at+cmgs=\"the_length_of_the_message\", input \"pdu_data\" and confirm with ctrl+z)")
        test.send_sms(test.dut, test.r1, test.content)

        test.log.step("4. Check if SMS was sent correctly from DUT (wait for +CMGS) and received correctly on Remote")
        test.log.info("Checking if SMS was sent correctly form DUT (+CMGS) was checked in previous step")
        test.read_sms(test.r1, test.content)

        test.log.step("5. On Remote Encode 16-bit message in PDU and send it from Remote to DUT")
        test.send_sms(test.r1, test.dut, test.content)

        test.log.step(
            "6. Check received messages on the Remote (wait for +CMTI URC and use commands at+cmgl / at+cmgr=<index> )")
        test.read_sms(test.dut, test.content)

    def cleanup(test):
        dstl_delete_all_sms_messages(test.dut)
        dstl_delete_all_sms_messages(test.r1)
        test.dut.at1.send_and_verify("AT&F", ".*OK.*")
        test.dut.at1.send_and_verify("AT&W", ".*OK.*")

    def prepare_module(test, module):
        dstl_detect(module)
        dstl_get_imei(module)
        dstl_get_bootloader(module)
        dstl_set_scfg_urc_dst_ifc(module)
        test.expect(module.at1.send_and_verify("AT+CSCS=\"GSM\"", "OK"))
        test.expect(dstl_register_to_network(module), critical=True)
        test.expect(module.at1.send_and_verify("AT+CSDH=1", "OK"))
        dstl_set_preferred_sms_memory(module, "ME")

    def send_sms(test, sender, receiver, content):
        sms_pdu = sender.sim.sca_pdu + "1100" + receiver.sim.pdu + "0008010E" + content
        ready_to_send = sender.at1.send_and_verify("AT+CMGS=28", ".*>.*", wait_for=".*>.*")
        if ready_to_send:
            test.expect(sender.at1.send_and_verify(sms_pdu, end="\u001A", expect=".*[+]CMGS:.*"))
        else:
            test.log.error("Unexpected response for AT+CMGS")

    def read_sms(test, receiver, text):
        test.expect(dstl_check_urc(receiver, ".*CMTI.*", timeout=200))
        sms_received = re.search(r"CMTI.*\",\s*(\d)", receiver.at1.last_response)
        regex = r".*{}.*".format(text)
        if sms_received:
            test.log.info(" Check received message via CMGR")
            test.expect(dstl_read_sms_message(receiver, sms_received[1]))
            test.log.info("Expected phrase : " + regex)
            test.expect(re.search(regex, receiver.at1.last_response))
            test.log.info(" Check received message via CMGL")
            test.expect(dstl_list_sms_messages_from_preferred_memory(receiver, 4))
            test.log.info("Expected phrase : " + regex)
            test.expect(re.search(regex, receiver.at1.last_response))
        else:
            test.expect(False, msg="CMTI URC did not appear")


if "__main__" == __name__:
    unicorn.main()
