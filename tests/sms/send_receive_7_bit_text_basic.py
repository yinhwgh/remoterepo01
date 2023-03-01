# responsible: michal.rydzewski@globallogic.com
# location: Wroclaw
# TC0103285.001

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
from dstl.sms.configure_sms_text_mode_parameters import dstl_configure_sms_event_reporting, \
    dstl_set_sms_text_mode_parameters, dstl_read_sms_text_mode_parameters, \
    dstl_show_sms_text_mode_parameters
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.list_sms_message import dstl_list_sms_messages_from_preferred_memory
from dstl.sms.read_sms_message import dstl_read_sms_message
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.sms_functions import dstl_send_sms_message


class Test(BaseTest):
    """TC0103285.001    SendReceive7BitTextBasic

    This procedure provides the possibility of basic tests sending and receiving SMS of 7-bit.

    Check functionality by sending and receiving SMS in text mode with 7-bit coding schemes.
    0. Delete all SMS from DUT and Remote memory
    1. Set text mode on DUT and Remote ( at+cmgf=1 )
    2. Set desired SMS URCs presentation on DUT and Remote (at+cnmi=2,1)
    3. Set 7-bit coding on DUT and Remote ( at+csmp=17,1,0,0 )
    4. Send one message from DUT to Remote ( at+cmgs="tel_nr_remote")
    5. Check if SMS was sent correctly from DUT (wait for +CMGS) and received correctly on Remote
    6. Send one message from Remote to DUT ( at+cmgs="tel_nr_dut")
    7. Check received message on DUT (wait for +CMTI URC and use commands at+cmgl / at+cmgr=<index>)
    """

    def setup(test):
        test.preparation(test.dut)
        test.preparation(test.r1)

    def run(test):
        test.log.info("Check functionality by sending and receiving SMS in text mode with 7-bit "
                      "coding schemes.")
        test.log.step("0. Delete all SMS from DUT and Remote memory")
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_delete_all_sms_messages(test.r1))

        test.log.step("1. Set text mode on DUT and Remote ( at+cmgf=1 )")
        test.expect(dstl_select_sms_message_format(test.dut, sms_format="Text"))
        test.expect(dstl_select_sms_message_format(test.r1, sms_format="Text"))

        test.log.step("2. Set desired SMS URCs presentation on DUT and Remote (at+cnmi=2,1)")
        test.expect(dstl_configure_sms_event_reporting(test.dut, mode="2", mt="1"))
        test.expect(dstl_configure_sms_event_reporting(test.r1, mode="2", mt="1"))

        test.log.step("3. Set 7-bit coding on DUT and Remote ( at+csmp=17,1,0,0 )")
        test.set_7_bit_coding(test.dut)
        test.set_7_bit_coding(test.r1)

        test.log.step("4. Send one message from DUT to Remote ( at+cmgs=\"tel_nr_remote\")")
        test.send_sms(test.dut, test.r1, "3132")

        test.log.step("5. Check if SMS was sent correctly from DUT (wait for +CMGS) and received "
                      "correctly on Remote")
        test.log.info("URC +CMGS was checked in previous step")
        test.read_sms(test.dut, test.r1, "3132")

        test.log.step("6. Send one message from Remote to DUT ( at+cmgs=\"tel_nr_dut\")")
        test.send_sms(test.r1, test.dut, "3233")

        test.log.step(
            "7. Check received message on DUT (wait for +CMTI URC and use commands at+cmgl / "
            "at+cmgr=<index>)")
        test.read_sms(test.r1, test.dut, "3233")

    def cleanup(test):
        dstl_delete_all_sms_messages(test.dut)
        dstl_delete_all_sms_messages(test.r1)
        test.expect(dstl_set_sms_text_mode_parameters(test.dut, fo="17", vp_or_scts="167", pid="0",
                                                      dcs="0", exp_resp=".*OK.*"))
        test.expect(dstl_set_sms_text_mode_parameters(test.dut, fo="17", vp_or_scts="167", pid="0",
                                                      dcs="0", exp_resp=".*OK.*"))
        test.expect(dstl_reset_settings_to_factory_default_values(test.dut))
        test.expect(dstl_store_user_defined_profile(test.dut))
        test.expect(dstl_reset_settings_to_factory_default_values(test.r1))
        test.expect(dstl_store_user_defined_profile(test.r1))

    def preparation(test, module):
        dstl_detect(module)
        dstl_get_imei(module)
        dstl_get_bootloader(module)
        dstl_set_scfg_urc_dst_ifc(module)
        test.expect(dstl_set_character_set(module, "GSM"))
        test.expect(dstl_register_to_network(module), critical=True)
        test.expect(dstl_show_sms_text_mode_parameters(module))
        dstl_set_preferred_sms_memory(module, "ME")

    def send_sms(test, sender, receiver, text):
        test.expect(dstl_send_sms_message(sender, receiver.sim.int_voice_nr, sms_text=text))
        test.expect(dstl_check_urc(sender, ".*CMGS.*"))

    def read_sms(test, sender, receiver, text):
        test.expect(dstl_check_urc(receiver, ".*CMTI.*", timeout=200))
        sms_received_remote = re.search(r"CMTI.*\",\s*(\d)", receiver.at1.last_response)
        regex = r".*\{}.*(\n|\r){}.*".format(sender.sim.int_voice_nr, text)
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

    def set_7_bit_coding(test, module):
        test.expect(dstl_set_sms_text_mode_parameters(module, fo="17", vp_or_scts="1", pid="0",
                                                      dcs="0", exp_resp=".*OK.*"))
        text_mode_prm = test.expect(dstl_read_sms_text_mode_parameters(module))
        text_mode_prm_contains_expected = False
        if text_mode_prm == ['17', '1', '0', '0\r']:
            text_mode_prm_contains_expected = True
        test.expect(text_mode_prm_contains_expected)


if "__main__" == __name__:
    unicorn.main()
