# responsible: renata.bryla@globallogic.com
# location: Wroclaw
# TC0095684.001

import re
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
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
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.send_sms_message import dstl_send_sms_message


class Test(BaseTest):
    """TC0095684.001    SendReceive7BitAnd8BitTextBasic

    This procedure provides the possibility of basic tests sending and receiving sms of 7,8-bit.

    Check functionality by sending and receiving SMS in text mode with 7-bit and 8-bit
    coding schemes.
    1. Set text mode on Dut and Remote ( at+cmgf=1 )
    2. Set desired SMS URCs presentation on Dut and Remote (at+cnmi=2,1)
    3. Set 7-Bit coding on Dut and Remote ( at+csmp=17,1,0,0 )
    4. Send one message from Dut to Remote ( at+cmgs="tel_nr_remote")
    and check if SMS was send from Dut (wait for +CMGS URC)
    5. Send one message from Remote to Dut ( at+cmgs="tel_nr_dut")
    6. Check receive message on Dut (at+cmgl / at+cmgr=<index>)
    7. Set 8-Bit coding on Dut and Remote ( at+csmp=17,1,0,4 )
    8. Send one message from Dut to Remote ( at+cmgs="tel_nr_remote")
    and check if SMS was send from Dut (wait for +CMGS URC)
    9. Send one message from Remote to Dut ( at+cmgs="tel_nr_dut")
    10. Check receive message on Dut (at+cmgl / at+cmgr=<index>)
    """

    def setup(test):
        test.preparation(test.dut)
        test.preparation(test.r1)
        test.dcs_7bit = "0"
        test.dcs_8bit = "4"

    def run(test):
        test.log.step("1. Set text mode on DUT and Remote ( at+cmgf=1 )")
        test.expect(dstl_select_sms_message_format(test.dut))
        test.expect(dstl_select_sms_message_format(test.r1))

        test.log.step("2. Set desired SMS URCs presentation on DUT and Remote (at+cnmi=2,1)")
        test.expect(dstl_configure_sms_event_reporting(test.dut, "2", "1"))
        test.expect(dstl_configure_sms_event_reporting(test.r1, "2", "1"))

        test.log.step("3. Set 7-bit coding on DUT and Remote ( at+csmp=17,1,0,0 )")
        test.set_and_check_csmp(test.dut, test.dcs_7bit)
        test.set_and_check_csmp(test.r1, test.dcs_7bit)

        test.log.step("4. Send one message from Dut to Remote ( at+cmgs=\"tel_nr_remote\") "
                      "and check if SMS was send from Dut (wait for +CMGS URC)")
        test.send_sms(test.dut, test.r1, "3132")
        test.verify_delivered_msg(test.r1, "3132")

        test.log.step("5. Send one message from Remote to DUT ( at+cmgs=\"tel_nr_dut\")")
        test.send_sms(test.r1, test.dut, "3334")

        test.log.step("6. Check receive message on Dut (at+cmgl / at+cmgr=<index>)")
        test.verify_delivered_msg(test.dut, "3334")

        test.log.step("7. Set 8-Bit coding on Dut and Remote ( at+csmp=17,1,0,4 )")
        test.set_and_check_csmp(test.dut, test.dcs_8bit)
        test.set_and_check_csmp(test.r1, test.dcs_8bit)

        test.log.step("8. Send one message from Dut to Remote ( at+cmgs=\"tel_nr_remote\") "
                      "and check if SMS was send from Dut (wait for +CMGS URC)")
        test.send_sms(test.dut, test.r1, "3536")
        test.verify_delivered_msg(test.r1, "3536")

        test.log.step("9. Send one message from Remote to DUT ( at+cmgs=\"tel_nr_dut\")")
        test.send_sms(test.r1, test.dut, "3738")

        test.log.step("10. Check receive message on Dut (at+cmgl / at+cmgr=<index>)")
        test.verify_delivered_msg(test.dut, "3738")

    def cleanup(test):
        test.delete_sms_from_memory(test.dut)
        test.restore_values(test.dut)
        test.delete_sms_from_memory(test.r1)
        test.restore_values(test.r1)

    def preparation(test, module):
        dstl_detect(module)
        dstl_get_imei(module)
        dstl_get_bootloader(module)
        dstl_set_scfg_urc_dst_ifc(module)
        test.expect(dstl_register_to_network(module), critical=True)
        test.expect(dstl_show_sms_text_mode_parameters(module))
        test.delete_sms_from_memory(module)
        test.expect(dstl_set_sms_center_address(module, module.sim.sca_int))

    def delete_sms_from_memory(test, module):
        test.log.info("Delete SMS from memory")
        test.expect(dstl_set_preferred_sms_memory(module, "ME"))
        test.expect(dstl_delete_all_sms_messages(module))

    def restore_values(test, module):
        test.expect(dstl_set_sms_text_mode_parameters(module, "17", "167", "0", "0"))
        test.expect(dstl_reset_settings_to_factory_default_values(module))
        test.expect(dstl_store_user_defined_profile(module))

    def set_and_check_csmp(test, module, dcs):
        test.expect(dstl_set_sms_text_mode_parameters(module, "17", "1", "0", dcs))
        test.expect(dstl_read_sms_text_mode_parameters(module) == ["17", "1", "0", f"{dcs}\r"])

    def send_sms(test, sender, receiver, text):
        test.expect(dstl_send_sms_message(sender, receiver.sim.int_voice_nr, text,
                                          set_sms_format=False, set_sca=False))
        test.expect(re.search(".*CMGS.*", sender.at1.last_response))

    def verify_delivered_msg(test, receiver, content):
        test.expect(dstl_check_urc(receiver, ".*CMTI.*", timeout=360))
        sms_received = re.search(r"CMTI:.*\",\s*(\d{1,3})", receiver.at1.last_response)
        if sms_received:
            test.expect(dstl_list_sms_messages_from_preferred_memory(receiver, "ALL"))
            test.log.info(f"Expected msg content after list message: .*{content}.*")
            test.expect(re.search(r".*[\n\r]{}.*".format(content), receiver.at1.last_response))
            test.log.info(f"Expected msg content after read message: .*{content}.*")
            test.expect(re.search(rf".*[\n\r]{content}.*",
                                  dstl_read_sms_message(receiver, sms_received[1])))
        else:
            test.expect(False, msg="Message was not received")


if "__main__" == __name__:
    unicorn.main()
