# responsible: renata.bryla@globallogic.com
# location: Wroclaw
# TC0011144.001

import re
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.character_set import dstl_set_character_set
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.configure_sms_text_mode_parameters import dstl_set_sms_text_mode_parameters
from dstl.sms.delete_sms import dstl_delete_all_sms_messages, dstl_delete_sms_message_from_index
from dstl.sms.get_sms_count_from_memory import dstl_get_sms_count_from_memory
from dstl.sms.read_sms_message import dstl_read_sms_message
from dstl.sms.select_message_service import dstl_set_message_service
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.send_sms_message import dstl_send_sms_message
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.sms_functions import dstl_enable_sms_urc
from dstl.sms.sms_memory_capacity import dstl_get_sms_memory_capacity
from dstl.sms.write_sms_to_memory import dstl_write_sms_to_memory


class Test(BaseTest):
    """TC0011144.001 SmsStorageFullText
    Test SMS overflow presentation of the SIM and ME Memory in text mode

    Depending on the product, 1 of the scenarios will be realized:
    - Scenario for products which support MT memory and at^smgo command
    - Scenario for products which support at^sind="smsfull" command
    - Scenario for products which NOT support at^sind="smsfull" and/or at^smgo  commands
    """

    MSG_INDEX_1 = "1"
    MSG_INDEX_2 = "2"
    SMS_TIMEOUT = 360
    TIME_WAIT_IN_SECONDS = 30
    TIME_WAIT_IN_SECONDS_LONG = 120

    def setup(test):
        test.prepare_module_to_test(test.dut, "===== Prepare DUT module to the test =====")
        test.prepare_module_to_test(test.r1, "===== Prepare REMOTE module to the test =====")
        test.sm_storage_capacity = test.prepare_storage_capacity("SM")
        test.fulfill_memory("SM", test.sm_storage_capacity)
        test.me_storage_capacity = test.prepare_storage_capacity("ME")
        test.fulfill_memory("ME", test.me_storage_capacity)

    def run(test):
        test.log.info(f'Will be realized scenario: \n'
                      f'Scenario for products which NOT support at^sind="smsfull" '
                      f'and/or at^smgo commands')

        test.log.step("Step 1.a: Free one place on ME on receiver, "
                      "send SMS to it and check if it is delivered.")
        test.expect(dstl_delete_sms_message_from_index(test.dut, test.MSG_INDEX_1))
        test.expect(dstl_send_sms_message(test.r1, test.dut.sim.int_voice_nr, "SMS step 1a",
                                          set_sms_format=False, set_sca=False))
        test.verify_delivered_message("SMS step 1a", r"CMTI:.*\",\s*(\d{1,3})")
        test.expect(
            dstl_get_sms_count_from_memory(test.dut)[0] == int(test.me_storage_capacity))

        test.log.step("Step 1.b: Free one place on ME on receiver, "
                      "write SMS to it and check if it is saved.")
        test.expect(dstl_delete_sms_message_from_index(test.dut, test.MSG_INDEX_1))
        test.expect(dstl_write_sms_to_memory(test.dut, "SMS step 1b"))
        test.read_message(test.MSG_INDEX_1, "SMS step 1b")
        test.expect(
            dstl_get_sms_count_from_memory(test.dut)[0] == int(test.me_storage_capacity))

        test.log.step("Step 2.a: Free one place on SM on receiver, "
                      "send SMS to it and check  if it is delivered.")
        test.expect(dstl_set_preferred_sms_memory(test.dut, "SM"))
        test.expect(dstl_delete_sms_message_from_index(test.dut, test.MSG_INDEX_1))
        test.expect(dstl_send_sms_message(test.r1, test.dut.sim.int_voice_nr, "SMS step 2a",
                                          set_sms_format=False, set_sca=False))
        test.verify_delivered_message("SMS step 2a", r"CMTI:.*\",\s*(\d{1,3})")
        test.expect(
            dstl_get_sms_count_from_memory(test.dut)[0] == int(test.sm_storage_capacity))

        test.log.step("Step 2.b: Free one place on SM on receiver, "
                      "write SMS to it and check  if it is saved.")
        test.expect(dstl_delete_sms_message_from_index(test.dut, test.MSG_INDEX_1))
        test.expect(dstl_write_sms_to_memory(test.dut, "SMS step 2b"))
        test.read_message(test.MSG_INDEX_1, "SMS step 2b")
        test.expect(
            dstl_get_sms_count_from_memory(test.dut)[0] == int(test.sm_storage_capacity))

        test.log.step("Step 3: Free one place on ME on receiver, "
                      "send two no-class SMSes to it and check if it is delivered.")
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
        test.expect(dstl_delete_sms_message_from_index(test.dut, test.MSG_INDEX_1))
        test.expect(dstl_send_sms_message(test.r1, test.dut.sim.int_voice_nr, "SMS step 3 1st",
                                          set_sms_format=False, set_sca=False))
        test.expect(dstl_send_sms_message(test.r1, test.dut.sim.int_voice_nr, "SMS step 3 2nd",
                                          set_sms_format=False, set_sca=False))
        test.verify_delivered_message("SMS step 3 1st", r"CMTI:.*\",\s*(\d{1,3})")
        test.dut.at1.read()     # some operators report that the memory is full
        # - read the last answer to clear the buffer before continuing the test
        test.expect(dstl_delete_sms_message_from_index(test.dut, test.MSG_INDEX_1))
        if dstl_check_urc(test.dut, ".*CMTI.*", timeout=test.SMS_TIMEOUT):
            test.verify_delivered_message("SMS step 3 2nd", r'CMTI:.*"ME",\s*(1)')
        else:
            test.log.info("===== Send another SMS to push previous =====")
            test.expect(dstl_delete_sms_message_from_index(test.dut, test.MSG_INDEX_2))
            test.expect(dstl_send_sms_message(test.r1, test.dut.sim.int_voice_nr,
                                              "SMS step 3 to push 2nd",
                                              set_sms_format=False, set_sca=False))
            test.verify_delivered_message("SMS step 3 to push 2nd", r'CMTI:.*"ME",\s*(1)')
            test.verify_delivered_message("SMS step 3 2nd", r'CMTI:.*"ME",\s*(2)')
        test.expect(
            dstl_get_sms_count_from_memory(test.dut)[0] == int(test.me_storage_capacity))

        test.log.step("Step 4: Additional step for backward compatibility Fulfill memory "
                      "and send one additional SMS, free one place on ME "
                      "then check if it is delivered.")
        test.expect(dstl_send_sms_message(test.r1, test.dut.sim.int_voice_nr, "SMS step 4 1st",
                                          set_sms_format=False, set_sca=False))
        test.sleep(test.TIME_WAIT_IN_SECONDS)
        test.dut.at1.read()     # some operators report that the memory is full
        # - read the last answer to clear the buffer before continuing the test
        test.expect(dstl_delete_sms_message_from_index(test.dut, test.MSG_INDEX_1))
        if dstl_check_urc(test.dut, ".*CMTI.*", timeout=test.SMS_TIMEOUT):
            test.verify_delivered_message("SMS step 4 1st", r'CMTI:.*"ME",\s*(1)')
        else:
            test.log.info("===== Send another SMS to push previous =====")
            test.expect(dstl_delete_sms_message_from_index(test.dut, test.MSG_INDEX_2))
            test.expect(dstl_send_sms_message(test.r1, test.dut.sim.int_voice_nr,
                                              "SMS step 4 2nd to push 1st",
                                              set_sms_format=False, set_sca=False))
            test.verify_delivered_message("SMS step 4 2nd to push 1st", r'CMTI:.*"ME",\s*(1)')
            test.verify_delivered_message("SMS step 4 1st", r'CMTI:.*"ME",\s*(2)')
        test.expect(
            dstl_get_sms_count_from_memory(test.dut)[0] == int(test.me_storage_capacity))

        test.log.step("Step 5: Fulfill memory. Free one place on ME and "
                      "then send one additional class 2 SMS, wait if it is delivered (shall "
                      "not) then free two place on SM and send another one push Sms on SM "
                      "and both Sms shall be delivered.")
        test.expect(dstl_delete_sms_message_from_index(test.dut, test.MSG_INDEX_1))
        test.expect(dstl_set_sms_text_mode_parameters(test.r1, "17", "167", "0", "242"))
        test.expect(dstl_send_sms_message(test.r1, test.dut.sim.int_voice_nr,
                                          "SMS step 5 class 2 1st",
                                          set_sms_format=False, set_sca=False))
        test.sleep(test.TIME_WAIT_IN_SECONDS_LONG)
        test.expect(not re.search(".*CMTI.*", test.dut.at1.last_response))
        test.expect(dstl_set_preferred_sms_memory(test.dut, "SM"))
        test.expect(dstl_delete_sms_message_from_index(test.dut, test.MSG_INDEX_1))
        test.sleep(test.TIME_WAIT_IN_SECONDS)
        if dstl_check_urc(test.dut, ".*CMTI.*", timeout=test.SMS_TIMEOUT):
            test.verify_delivered_message("SMS step 5 class 2 1st", r'CMTI:.*"SM",\s*(1)')
        else:
            test.log.info("===== Send another SMS to push previous =====")
            test.expect(dstl_delete_sms_message_from_index(test.dut, test.MSG_INDEX_2))
            test.expect(dstl_send_sms_message(test.r1, test.dut.sim.int_voice_nr,
                                              "SMS step 5 class 2 to push 1st",
                                              set_sms_format=False, set_sca=False))
            test.verify_delivered_message("SMS step 5 class 2 to push 1st",
                                          r'CMTI:.*"SM",\s*(1)')
            test.verify_delivered_message("SMS step 5 class 2 1st", r'CMTI:.*"SM",\s*(2)')
        test.expect(
            dstl_get_sms_count_from_memory(test.dut)[0] == int(test.sm_storage_capacity))

    def cleanup(test):
        test.expect(dstl_set_sms_text_mode_parameters(test.r1, "17", "167", "0", "0"))
        test.expect(dstl_set_preferred_sms_memory(test.dut, "SM"))
        dstl_delete_all_sms_messages(test.dut)
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
        dstl_delete_all_sms_messages(test.dut)

    def prepare_module_to_test(test, module, text):
        test.log.info(text)
        dstl_detect(module)
        dstl_get_imei(module)
        dstl_get_bootloader(module)
        dstl_set_scfg_urc_dst_ifc(module)
        test.expect(dstl_register_to_network(module), critical=True)
        test.expect(dstl_set_error_message_format(module))
        test.expect(dstl_set_character_set(module, 'GSM'))
        test.expect(dstl_set_message_service(module))
        test.expect(dstl_enable_sms_urc(module))
        test.expect(dstl_set_sms_text_mode_parameters(module, "17", "167", "0", "0"))
        test.expect(dstl_set_sms_center_address(module, module.sim.sca_int))
        test.expect(dstl_set_preferred_sms_memory(module, "SM"))
        test.expect(dstl_delete_all_sms_messages(module))
        test.expect(dstl_set_preferred_sms_memory(module, "ME"))
        test.expect(dstl_delete_all_sms_messages(module))
        test.expect(dstl_select_sms_message_format(module))

    def prepare_storage_capacity(test, memory):
        test.log.info(f"=== Set memory {memory} to prepare memory capacity =====")
        test.expect(dstl_set_preferred_sms_memory(test.dut, memory))
        storage_capacity = dstl_get_sms_memory_capacity(test.dut, 1)
        test.log.info(f"{memory} Storage Capacity value: {storage_capacity}")
        return storage_capacity

    def fulfill_memory(test, memory, storage_capacity):
        test.log.info(f"===== Fulfill memory {memory} =====")
        test.expect(dstl_set_preferred_sms_memory(test.dut, f"{memory}"))

        test.log.step(f"Write SMS to {memory} storage until storage is full")
        for index in range(int(storage_capacity)):
            test.expect(
                dstl_write_sms_to_memory(test.dut, f'SMS message {index} - memory: {memory}'))
        test.log.info(f"===== check if memory {memory} is full =====")
        test.expect(dstl_get_sms_count_from_memory(test.dut)[0] == int(storage_capacity))

    def read_message(test, index, text):
        test.expect(dstl_read_sms_message(test.dut, index))
        regex = f'.*CMGR:.*\s*[\n\r]{text}.*'
        test.log.info("Expected REGEX: {}".format(regex))
        test.expect(re.search(regex, test.dut.at1.last_response))

    def verify_delivered_message(test, text, regex):
        test.expect(dstl_check_urc(test.dut, ".*CMTI.*", timeout=test.SMS_TIMEOUT))
        sms_received = re.search(regex, test.dut.at1.last_response)
        if sms_received:
            test.read_message(sms_received[1], text)
        else:
            test.expect(False, msg="Message was not received")


if "__main__" == __name__:
    unicorn.main()