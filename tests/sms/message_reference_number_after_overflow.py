# responsible: renata.bryla@globallogic.com
# location: Wroclaw
# TC0095641.001, TC0095641.002

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
from dstl.sms.configure_sms_text_mode_parameters import dstl_set_sms_text_mode_parameters, \
    dstl_configure_sms_event_reporting
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.send_sms_message import dstl_send_sms_message


class Test(BaseTest):
    """TC0095641.001/TC0095641.002    MessageReferenceNumberAfterOverflow

    The goal of this TC is to check whether it is possible to reset the counter
    of sent SMS messages (message reference number)

    1. Send SMS message from Dut to Remote
    2. Check value of the message reference number
    3. Send SMS message from Dut to Remote
    4. Check if the counter has increased by 1
    5. Do steps 3 and 4 to reach the maximum counter value
    ("65535" - for Dahlia, "255" - for QCT modules, for the other modules value may be different.)
    6. Send another SMS
    7. Check if the SMS counter is set to 0

    Note:
    To avoid sending too many messages e.g. in case of SQN modules please consider editing
    the "etc/sqnimsd.xml" file (reboot might be required).
    """

    def setup(test):
        test.prepare_module(test.dut, "PREPARING DUT")
        test.prepare_module(test.r1, "PREPARING REMOTE")

    def run(test):
        iteration = 1
        max_ref_number = 255

        test.log.step("Step 1. Send SMS message from Dut to Remote")
        ref_number = test.send_sms(test.dut, test.r1, "test")
        test.delete_sms_from_remote()

        test.log.step("Step 2. Check value of the message reference number")
        test.log.info("Message reference number equals = {}".format(str(ref_number)))
        if ref_number:
            test.scenario_from_3_to_7(ref_number, max_ref_number, iteration)
        else:
            test.log.info("Try to send another SMS. If correct, received SMS will be removed "
                          "from REMOTE and scenario will be continue from step 3.")
            ref_number = test.send_sms(test.dut, test.r1, "test")
            if ref_number:
                test.delete_sms_from_remote()
                test.log.info("Sending SMS successful. Continue test scenario.")
                test.scenario_from_3_to_7(ref_number, max_ref_number, iteration)
            else:
                test.expect(False, critical=True, msg="SMS cannot be send !!! End of test")

    def cleanup(test):
        test.restore_values(test.dut)
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.restore_values(test.r1)
        test.expect(dstl_delete_all_sms_messages(test.r1))

    def restore_values(test, module):
        test.expect(dstl_reset_settings_to_factory_default_values(module))
        test.expect(dstl_store_user_defined_profile(module))

    def prepare_module(test, module, text):
        test.log.step(text)
        dstl_detect(module)
        dstl_get_imei(module)
        dstl_get_bootloader(module)
        test.expect(dstl_set_scfg_urc_dst_ifc(module))
        test.expect(dstl_register_to_network(module))
        test.expect(dstl_select_sms_message_format(module, "TEXT"))
        test.expect(dstl_set_preferred_sms_memory(module, "ME"))
        test.expect(dstl_set_character_set(module, 'GSM'))
        test.expect(dstl_configure_sms_event_reporting(module, "2", "1"))
        test.expect(dstl_set_sms_text_mode_parameters(module, "17", "167", "0", "0"))
        test.expect(dstl_set_sms_center_address(module, module.sim.sca_int))
        test.expect(dstl_delete_all_sms_messages(module))

    def scenario_from_3_to_7(test, ref_number, max_ref_number, iteration):
        for i in range(ref_number, max_ref_number):
            test.log.step("Step 3. Send SMS message from Dut to Remote")
            ref_number_next = test.send_sms(test.dut, test.r1, "test")
            test.delete_sms_from_remote()

            if ref_number_next:
                test.log.step("Step 4. Check if the counter has increased by 1")
                ref_number += 1
                if ref_number_next == ref_number:
                    test.log.info("Current message reference number equals: "
                                  f"{str(ref_number_next)}")
                    ref_number_prev = ref_number_next - 1
                    test.log.info(f"Previous message reference number equals: "
                                  f"{str(ref_number_prev)}")
                    test.log.info("Message reference number increase by 1 !")
                    test.expect(ref_number_prev == ref_number_next - 1)
                    if ref_number_next == max_ref_number:
                        test.log.info("Max counter of reference number has been reached !")
                        break
                else:
                    test.expect(False, msg="Message reference number NOT correct !")

                if iteration == 1:
                    test.log.step("Step 5. Do steps 3 and 4 to reach the maximum counter value "
                                  "(\"65535\" - for Dahlia, \"255\" - for QCT modules, "
                                  "for the other modules value may be different.)")
                iteration += 1
            else:
                test.log.info("Try to send another SMS. If correct, received SMS will be removed "
                              "from REMOTE and scenario will be continue from step 3.")
                ref_number_next = test.send_sms(test.dut, test.r1, "test")
                if ref_number_next:
                    test.delete_sms_from_remote()
                    test.log.info("Sending SMS successful. Continue test scenario.")
                    ref_number += 1
                else:
                    test.expect(False, critical=True, msg="SMS cannot be send !!! End of test")
                    break

        test.log.step("Step 6. Send another SMS")
        ref_number = test.send_sms(test.dut, test.r1, "test")
        test.delete_sms_from_remote()

        test.log.step("Step 7. Check if the SMS counter is set to 0")
        if ref_number == 0:
            test.log.info("Message reference number is set to 0 !")
            test.expect(ref_number == 0)
        else:
            test.expect(False, msg="Message reference number NOT set to 0 !")

    def send_sms(test, sender, receiver, text):
        cmgs_index = ""
        try:
            test.expect(dstl_send_sms_message(sender, receiver.sim.int_voice_nr, text,
                                              set_sms_format=False, set_sca=False))
            cmgs = test.expect(re.search(".*CMGS: (.*)", sender.at1.last_response))
            if cmgs:
                cmgs_index = cmgs.group(1)
            return int(cmgs_index)
        except ValueError:
            test.expect(False, critical=True, msg="+CMGS URC not appears. Sending SMS failed !!!")

    def delete_sms_from_remote(test):
        if test.expect(dstl_check_urc(test.r1, ".*CMTI.*", timeout=220)):
            test.expect(dstl_delete_all_sms_messages(test.r1))
        else:
            test.expect(False, critical=True, msg="Message not delivered. !!! End of test")


if "__main__" == __name__:
    unicorn.main()
