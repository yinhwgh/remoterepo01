#responsible: dariusz.drozdek@globallogic.com
#location: Wroclaw
#TC0103286.001

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
    """TC0103286.001    SendReceive16BitTextBasic

    This procedure provides the possibility of basic tests sending and receiving SMS of 16-bit.

    Check functionality by sending and receiving SMS in text mode with 16-bit coding schemes.
    0. Delete all SMS from DUT and Remote memory
    1. Set text mode on DUT and Remote ( at+cmgf=1 )
    2. Set desired SMS URCs presentation on DUT and Remote (at+cnmi=2,1)
    3. Set 16-bit coding on DUT and Remote ( at+csmp=17,1,0,8 )
    4. Send one message from DUT to Remote ( at+cmgs="tel_nr_remote")
    5. Check if SMS was sent correctly from DUT and received correctly on Remote (wait for +CMGS)
    6. Send one message from Remote to DUT ( at+cmgs="tel_nr_dut")
    7. Check received message on DUT (wait for +CMTI URC and use commands at+cmgl / at+cmgr=<index>)
    """

    def setup(test):
        test.preparation(test.dut)
        test.preparation(test.r1)

    def run(test):
        test.log.step("Check functionality by sending and receiving SMS in text mode with 16-bit coding schemes.")
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_register_to_network(test.r1))
        test.log.info("Set UCS2 character set on DUT and Remote")
        test.expect(test.dut.at1.send_and_verify("AT+CSCS=\"UCS2\"", ".*OK.*"))
        test.expect(test.r1.at1.send_and_verify("AT+CSCS=\"UCS2\"", ".*OK.*"))

        test.log.step("0. Delete all SMS from DUT and Remote memory")
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_set_preferred_sms_memory(test.r1, "ME"))
        test.expect(dstl_delete_all_sms_messages(test.r1))

        test.log.step("1. Set text mode on DUT and Remote ( at+cmgf=1 )")
        test.expect(dstl_select_sms_message_format(test.dut))
        test.expect(dstl_select_sms_message_format(test.r1))

        test.log.step("2. Set desired SMS URCs presentation on DUT and Remote (at+cnmi=2,1)")
        test.expect(test.dut.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*"))
        test.expect(test.r1.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*"))

        test.log.step("3. Set 16-bit coding on DUT and Remote ( at+csmp=17,1,0,8)")
        test.expect(test.dut.at1.send_and_verify("AT+CSMP=17,1,0,8", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSMP?", r".*\+CSMP: 17,1,0,8.*OK.*"))

        test.expect(test.r1.at1.send_and_verify("AT+CSMP=17,1,0,8", ".*OK.*"))
        test.expect(test.r1.at1.send_and_verify("AT+CSMP?", r".*\+CSMP: 17,1,0,8.*OK.*"))

        test.log.step("4. Send one message from DUT to Remote ( at+cmgs=\"tel_nr_remote\")")
        test.send_sms(test.dut, test.r1, "0053004D005300200074006F002000720065006D006F00740065")

        test.log.step("5. Check if SMS was sent correctly from DUT and received correctly on Remote (wait for +CMGS)")
        test.log.info("URC +CMGS was checked in previous step")
        test.read_sms(test.dut, test.r1, "0053004D005300200074006F002000720065006D006F00740065")

        test.log.step("6. Send one message from Remote to DUT ( at+cmgs=\"tel_nr_dut\")")
        test.send_sms(test.r1, test.dut, "0053004D005300200074006F0020006400750074")

        test.log.step(
            "7. Check received message on DUT (wait for +CMTI URC and use commands at+cmgl / at+cmgr=<index>)")
        test.read_sms(test.r1, test.dut, "0053004D005300200074006F0020006400750074")

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT+CSCS=\"GSM\"", ".*OK.*"))
        test.expect(test.r1.at1.send_and_verify("AT+CSCS=\"GSM\"", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))
        test.expect(test.r1.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_delete_all_sms_messages(test.r1))
        test.dut.at1.send_and_verify("AT&F", ".*OK.*")
        test.dut.at1.send_and_verify("AT&W", ".*OK.*")

    def preparation(test, module):
        dstl_detect(module)
        dstl_get_imei(module)
        dstl_get_bootloader(module)
        dstl_set_scfg_urc_dst_ifc(module)
        test.expect(dstl_register_to_network(module), critical=True)
        test.expect(module.at1.send_and_verify("AT+CSDH=1", "OK"))
        test.expect(dstl_set_preferred_sms_memory(module, "ME"))

    def decoder(test, string):
        return_string = ""
        for index in string:
            decoded_index = "00" + hex(ord(index)).split('x')[-1]
            return_string = return_string + decoded_index
        return return_string.upper()

    def send_sms(test, sender, receiver, text):
        test.expect(sender.at1.send_and_verify("AT+CMGS=\"{}\"".format(test.decoder(receiver.sim.int_voice_nr)),
                                               ".*>.*", wait_for=".*>.*"))
        test.expect(sender.at1.send_and_verify(text, end="\u001A", timeout=20, wait_for="CMGS", expect="OK"))
        test.expect(re.search(".*CMGS:.*", sender.at1.last_response), msg="URC CMGS was not found")

    def read_sms(test, sender, receiver, text):
        test.expect(dstl_check_urc(receiver, ".*CMTI.*", timeout=200))
        sms_received_remote = re.search(r"CMTI.*\",\s*(\d)", receiver.at1.last_response)
        sender_number = sender.sim.nat_voice_nr
        if sender_number[0] == "0":
            sender_number = sender.sim.nat_voice_nr[1:]
        regex = r".*{}.*(\n|\r){}.*".format(test.decoder(sender_number), text)
        if sms_received_remote:
            test.log.info(" Check received message via CMGR")
            test.expect(dstl_read_sms_message(receiver, sms_received_remote[1]))
            test.log.info("Expected phrase : " + regex)
            test.expect(re.search(regex, receiver.at1.last_response))
            test.log.info(" Check received message via CMGL")
            test.expect(dstl_list_sms_messages_from_preferred_memory(receiver, "ALL"))
            test.log.info("Expected phrase : " + regex)
            test.expect(re.search(regex, receiver.at1.last_response))
        else:
            test.expect(False, msg="Message was not received")

if "__main__" == __name__:
    unicorn.main()
