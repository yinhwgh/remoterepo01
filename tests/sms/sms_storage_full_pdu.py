# responsible: renata.bryla@globallogic.com
# location: Wroclaw
# TC0011209.001

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
from dstl.sms.configure_sms_pdu_parameters import dstl_calculate_pdu_length
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
    """TC0011209.001 SmsStorageFullPDU
    test SMS overflow presentation of the SIM and ME Memory in PDU mode

    Depending on the product, 1 of the scenarios will be realized:
    - Scenario for products which support MT memory and at^smgo command
    - Scenario for products which support at^sind=\"smsfull\" command
    - Scenario for products which do NOT support at^sind="smsfull" and/or  at^smgo  commands:
    """

    MSG_INDEX_1 = "1"
    MSG_INDEX_2 = "2"
    SMS_TIMEOUT = 360
    TIME_WAIT_IN_SECONDS = 30
    TIME_WAIT_IN_SECONDS_LONG = 120
    SMS_TEXT_1A = "0BD3E61434A797E1A05818"
    SMS_TEXT_1B = "0BD3E61434A797E1A09818"
    SMS_TEXT_2A = "0BD3E61434A797E1205918"
    SMS_TEXT_2B = "0BD3E61434A797E1209918"
    SMS_TEXT_3_1ST = "0ED3E61434A797E1A0192836A703"
    SMS_TEXT_3_2ND = "0ED3E61434A797E1A01948E62603"
    SMS_TEXT_3_PUSH = "16D3E61434A797E1A01988FE06C1EB733448E62603"
    SMS_TEXT_4_1ST = "0ED3E61434A797E1201A2836A703"
    SMS_TEXT_4_PUSH = "1AD3E61434A797E1201A48E62683E86F10BC3E478362733A"
    SMS_TEXT_5 = "16D3E61434A797E1A01A68CC0ECFE720192836A703"
    SMS_TEXT_5_PUSH = "1ED3E61434A797E1A01A68CC0ECFE7201988FE06C1EB73342836A703"

    def setup(test):
        test.prepare_module_to_test(test.dut, "===== Prepare DUT module to the test =====")
        test.prepare_module_to_test(test.r1, "===== Prepare REMOTE module to the test =====")
        test.sm_storage_capacity = test.prepare_storage_capacity("SM")
        test.fulfill_memory("SM", test.sm_storage_capacity)
        test.me_storage_capacity = test.prepare_storage_capacity("ME")
        test.fulfill_memory("ME", test.me_storage_capacity)

    def run(test):
        test.log.info(f'Will be realized scenario: \n'
                      f'Scenario for products which do NOT support at^sind="smsfull" '
                      f'and/or at^smgo commands \n e.g. product SERVAL')

        test.log.step("Step 1.a: Free one place on ME on receiver, "
                      "send SMS to it and check if it is delivered.")
        test.expect(dstl_delete_sms_message_from_index(test.dut, test.MSG_INDEX_1))
        pdu_1a = f'{test.r1.sim.sca_pdu}1100{test.dut.sim.pdu}0000FF{test.SMS_TEXT_1A}'
        test.expect(dstl_send_sms_message(test.r1, dstl_calculate_pdu_length(pdu_1a),
                                          sms_text=pdu_1a, sms_format="PDU",
                                          set_sms_format=False, set_sca=False))
        test.verify_delivered_message(test.SMS_TEXT_1A, r"CMTI:.*\",\s*(\d{1,3})")
        test.expect(dstl_get_sms_count_from_memory(test.dut)[0] == int(test.me_storage_capacity))

        test.log.step("Step 1.b: Free one place on ME on receiver, "
                      "write SMS to it and check if it is saved.")
        test.expect(dstl_delete_sms_message_from_index(test.dut, test.MSG_INDEX_1))
        pdu_1b = f'{test.dut.sim.sca_pdu}1100{test.dut.sim.pdu}0000FF{test.SMS_TEXT_1B}'
        test.expect(dstl_write_sms_to_memory(test.dut, sms_format="PDU", pdu=pdu_1b))
        test.read_message(test.MSG_INDEX_1, test.SMS_TEXT_1B)
        test.expect(dstl_get_sms_count_from_memory(test.dut)[0] == int(test.me_storage_capacity))

        test.log.step("Step 2.a: Free one place on SM on receiver, "
                      "send SMS to it and check if it is delivered.")
        test.expect(dstl_set_preferred_sms_memory(test.dut, "SM"))
        test.expect(dstl_delete_sms_message_from_index(test.dut, test.MSG_INDEX_1))
        pdu_2a = f'{test.r1.sim.sca_pdu}1100{test.dut.sim.pdu}0000FF{test.SMS_TEXT_2A}'
        test.expect(dstl_send_sms_message(test.r1, dstl_calculate_pdu_length(pdu_2a),
                                          sms_text=pdu_2a, sms_format="PDU",
                                          set_sms_format=False, set_sca=False))
        test.verify_delivered_message(test.SMS_TEXT_2A, r"CMTI:.*\",\s*(\d{1,3})")
        test.expect(dstl_get_sms_count_from_memory(test.dut)[0] == int(test.sm_storage_capacity))

        test.log.step("Step 2.b: Free one place on SM on receiver, "
                      "write SMS to it and check if it is saved.")
        test.expect(dstl_delete_sms_message_from_index(test.dut, test.MSG_INDEX_1))
        pdu_2b = f'{test.dut.sim.sca_pdu}1100{test.dut.sim.pdu}0000FF{test.SMS_TEXT_2B}'
        test.expect(dstl_write_sms_to_memory(test.dut, sms_format="PDU", pdu=pdu_2b))
        test.read_message(test.MSG_INDEX_1, test.SMS_TEXT_2B)
        test.expect(dstl_get_sms_count_from_memory(test.dut)[0] == int(test.sm_storage_capacity))

        test.log.step("Step 3: Free one place on ME on receiver, "
                      "send two no-class SMSes to it and check if it is delivered.")
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
        test.expect(dstl_delete_sms_message_from_index(test.dut, test.MSG_INDEX_1))
        pdu_3_1st = f'{test.r1.sim.sca_pdu}1100{test.dut.sim.pdu}0000FF{test.SMS_TEXT_3_1ST}'
        test.expect(dstl_send_sms_message(test.r1, dstl_calculate_pdu_length(pdu_3_1st),
                                          sms_text=pdu_3_1st, sms_format="PDU",
                                          set_sms_format=False, set_sca=False))
        pdu_3_2nd = f'{test.r1.sim.sca_pdu}1100{test.dut.sim.pdu}0000FF{test.SMS_TEXT_3_2ND}'
        test.expect(dstl_send_sms_message(test.r1, dstl_calculate_pdu_length(pdu_3_2nd),
                                          sms_text=pdu_3_2nd, sms_format="PDU",
                                          set_sms_format=False, set_sca=False))
        test.verify_delivered_message(test.SMS_TEXT_3_1ST, r"CMTI:.*\",\s*(\d{1,3})")
        test.verify_message_when_fulfill_memory(test.SMS_TEXT_3_2ND, test.SMS_TEXT_3_PUSH, "ME")

        test.log.step("Step 4: Additional step for backward compatibility Fulfill memory "
                      "and send one additional SMS, free one place on ME "
                      "then check if it is delivered.")
        pdu_4 = f'{test.r1.sim.sca_pdu}1100{test.dut.sim.pdu}0000FF{test.SMS_TEXT_4_1ST}'
        test.expect(dstl_send_sms_message(test.r1, dstl_calculate_pdu_length(pdu_4), sms_text=pdu_4,
                                          sms_format="PDU", set_sms_format=False, set_sca=False))
        test.verify_message_when_fulfill_memory(test.SMS_TEXT_4_1ST, test.SMS_TEXT_4_PUSH, "ME")

        test.log.step("Step 5: Fulfill memory. Free one place on ME and "
                      "then send one additional class 2 SMS, wait if it is delivered (shall "
                      "not) then free two place on SM and send another one push Sms on SM "
                      "and both Sms shall be delivered.")
        test.expect(dstl_delete_sms_message_from_index(test.dut, test.MSG_INDEX_1))
        pdu_5 = f'{test.r1.sim.sca_pdu}1100{test.dut.sim.pdu}0012FF{test.SMS_TEXT_5}'
        test.expect(dstl_send_sms_message(test.r1, dstl_calculate_pdu_length(pdu_5), sms_text=pdu_5,
                                          sms_format="PDU", set_sms_format=False, set_sca=False))
        test.sleep(test.TIME_WAIT_IN_SECONDS_LONG)
        test.expect(not re.search(".*CMTI.*", test.dut.at1.last_response))
        test.expect(dstl_set_preferred_sms_memory(test.dut, "SM"))
        test.verify_message_when_fulfill_memory(test.SMS_TEXT_5, test.SMS_TEXT_5_PUSH, "SM")

    def cleanup(test):
        test.delete_sms_from_memory(test.dut, ["SM", "ME"])

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
        test.delete_sms_from_memory(module, ["SM", "ME"])
        test.expect(dstl_select_sms_message_format(module, 'PDU'))

    def delete_sms_from_memory(test, module, memory):
        for mem in memory:
            test.log.info(f"Delete SMS from memory: {mem}")
            test.expect(dstl_set_preferred_sms_memory(module, mem))
            test.expect(dstl_delete_all_sms_messages(module))

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
            test.expect(dstl_write_sms_to_memory(test.dut, sms_format="PDU"))
        test.log.info(f"===== check if memory {memory} is full =====")
        test.expect(dstl_get_sms_count_from_memory(test.dut)[0] == int(storage_capacity))

    def read_message(test, index, text):
        test.expect(dstl_read_sms_message(test.dut, index))
        regex = f'.*CMGR:.*\s*[\n\r].*{text}.*'
        test.log.info("Expected REGEX: {}".format(regex))
        test.expect(re.search(regex, test.dut.at1.last_response))

    def verify_delivered_message(test, text, regex):
        test.expect(dstl_check_urc(test.dut, ".*CMTI.*", timeout=test.SMS_TIMEOUT))
        sms_received = re.search(regex, test.dut.at1.last_response)
        if sms_received:
            test.read_message(sms_received[1], text)
        else:
            test.expect(False, msg="Message was not received")

    def verify_message_when_fulfill_memory(test, msg_1, msg_2_push, memory):
        if memory == "ME":
            test.sleep(test.TIME_WAIT_IN_SECONDS)
            test.dut.at1.read()  # some operators report that the memory is full
            # - read the last answer to clear the buffer before continuing the test
        test.expect(dstl_delete_sms_message_from_index(test.dut, test.MSG_INDEX_1))
        if memory == "SM":
            test.sleep(test.TIME_WAIT_IN_SECONDS)
        if dstl_check_urc(test.dut, ".*CMTI.*", timeout=test.SMS_TIMEOUT):
            test.verify_delivered_message(msg_1, rf'CMTI:.*"{memory}",\s*(1)')
        else:
            test.log.info("===== Send another SMS to push previous =====")
            test.expect(dstl_delete_sms_message_from_index(test.dut, test.MSG_INDEX_2))
            if memory == "SM":
                pdu_push = f'{test.r1.sim.sca_pdu}1100{test.dut.sim.pdu}0012FF{msg_2_push}'
            else:
                pdu_push = f'{test.r1.sim.sca_pdu}1100{test.dut.sim.pdu}0000FF{msg_2_push}'
            test.expect(dstl_send_sms_message(test.r1, dstl_calculate_pdu_length(pdu_push),
                                              sms_text=pdu_push, sms_format="PDU",
                                              set_sms_format=False, set_sca=False))
            test.verify_delivered_message(msg_2_push, rf'CMTI:.*"{memory}",\s*(1)')
            test.verify_delivered_message(msg_1, rf'CMTI:.*"{memory}",\s*(2)')
        if memory == "SM":
            message_capacity = test.sm_storage_capacity
        else:
            message_capacity = test.me_storage_capacity
        test.expect(dstl_get_sms_count_from_memory(test.dut)[0] == int(message_capacity))


if "__main__" == __name__:
    unicorn.main()