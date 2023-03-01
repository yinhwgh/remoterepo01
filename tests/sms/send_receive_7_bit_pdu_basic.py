# responsible: michal.rydzewski@globallogic.com
# location: Wroclaw
# TC0103287.001

import re
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.character_set import dstl_set_character_set
from dstl.configuration.reset_to_factory_default_state import \
    dstl_reset_settings_to_factory_default_values
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.configuration.store_user_defined_profile import dstl_store_user_defined_profile
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.configure_sms_pdu_parameters import dstl_calculate_pdu_length
from dstl.sms.configure_sms_text_mode_parameters import dstl_configure_sms_event_reporting, \
    dstl_show_sms_text_mode_parameters
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.list_sms_message import dstl_list_sms_messages_from_preferred_memory
from dstl.sms.read_sms_message import dstl_read_sms_message
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.send_sms_message import dstl_send_sms_message
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory


class Test(BaseTest):
    """TC0103287.001    SendReceive7BitPduBasic

    This procedure provides the possibility of basic test steps for sending and receiving 7-bit
    messages in PDU mode.

    Check functionality by sending and receiving SMS in PDU mode with 7-bit coding schemes.
    0. Delete all SMS from DUT and Remote memory
    1. Set PDU mode on DUT and Remote ( at+cmgf=0 )
    2. Set desired SMS URCs presentation on DUT and Remote (at+cnmi=2,1)
    3. On DUT Encode 7-bit message in PDU and send it from DUT to Remote
    (at+cmgs="the_length_of_the_message",
    input "pdu_data" and confirm with ctrl+z)
    4. Check if SMS was sent correctly from DUT (wait for +CMGS) and received correctly on Remote
    5. On Remote Encode 7-bit message in PDU and send it from Remote to DUT
    6. Check received messages on the DUT (wait for +CMTI URC and use commands at+cmgl / at+cmgr=)
    """

    def setup(test):
        test.content = "07D4E2943A6D4E01"
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
        test.expect(dstl_configure_sms_event_reporting(test.dut, mode="2", mt="1"))
        test.expect(dstl_configure_sms_event_reporting(test.r1, mode="2", mt="1"))

        test.log.step("3. On DUT Encode 7-bit message in PDU and send it from DUT to Remote "
                      "(at+cmgs=\"the_length_of_the_message\", input \"pdu_data\" and confirm with "
                      "ctrl+z)")
        test.send_sms(test.dut, test.r1, test.content)

        test.log.step("4. Check if SMS was sent correctly from DUT (wait for +CMGS) and received "
                      "correctly on Remote")
        test.expect(re.search(".*[+]CMGS: .*", test.dut.at1.last_response))
        test.read_sms(test.r1, test.content)

        test.log.step("5. On Remote Encode 7-bit message in PDU and send it from Remote to DUT")
        test.send_sms(test.r1, test.dut, test.content)

        test.log.step("6. Check received messages on the DUT (wait for +CMTI URC and use commands "
                      "at+cmgl / at+cmgr=) ")
        test.read_sms(test.dut, test.content)

    def cleanup(test):
        dstl_delete_all_sms_messages(test.dut)
        dstl_delete_all_sms_messages(test.r1)
        test.expect(dstl_reset_settings_to_factory_default_values(test.dut))
        test.expect(dstl_store_user_defined_profile(test.dut))
        test.expect(dstl_reset_settings_to_factory_default_values(test.r1))
        test.expect(dstl_store_user_defined_profile(test.r1))

    def prepare_module(test, module):
        dstl_detect(module)
        dstl_get_imei(module)
        dstl_get_bootloader(module)
        dstl_set_scfg_urc_dst_ifc(module)
        test.expect(dstl_set_character_set(module, "GSM"))
        test.expect(dstl_register_to_network(module), critical=True)
        test.expect(dstl_show_sms_text_mode_parameters(module))
        test.expect(dstl_set_preferred_sms_memory(module, "ME"))
        test.expect(dstl_set_sms_center_address(module, module.sim.sca_int))

    def send_sms(test, sender, receiver, content):
        sms_pdu = sender.sim.sca_pdu + "1100" + receiver.sim.pdu + "000001" + content
        test.expect(dstl_send_sms_message(sender, dstl_calculate_pdu_length(sms_pdu),
                                          sms_text=sms_pdu, sms_format="PDU", set_sms_format=False,
                                          set_sca=False))

    def read_sms(test, receiver, text):
        test.expect(dstl_check_urc(receiver, ".*CMTI.*", timeout=200))
        sms_received = re.search(r"CMTI.*\",\s*(\d)", receiver.at1.last_response)
        if sms_received:
            test.log.info(" Check received message via CMGR")
            test.expect(
                re.search(rf".*[\n\r].*{text}.*", dstl_read_sms_message(receiver, sms_received[1])))
            test.log.info(" Check received message via CMGL")
            test.expect(dstl_list_sms_messages_from_preferred_memory(receiver, 4))
            test.log.info(f"Expected phrase : .*{text}.*")
            test.expect(re.search(rf'.*{text}.*', receiver.at1.last_response))
        else:
            test.expect(False, msg="Message was not received")


if "__main__" == __name__:
    unicorn.main()
