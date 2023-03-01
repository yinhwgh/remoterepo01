# responsible: mariusz.znaczko@globallogic.com
# location: Wroclaw
# TC0095332.002

# feature: LM0000079.001, LM0000081.001, LM0000083.001, LM0000088.001, LM0000095.001, LM0000096.001,
# LM0000099.001, LM0000101.001, LM0000107.001, LM0000109.001, LM0000110.001, LM0000788.001, LM0001223.001,
# LM0001229.001, LM0001230.001,  LM0001231.001, LM0001233.001, LM0001234.001, LM0001238.001, LM0001240.001,
# LM0001241.001, LM0001242.001, LM0001501.001, LM0001935.001, LM0002383.001, LM0002384.001, LM0003219.003,
# LM0004451.003, LM0004455.002, LM0004455.003, LM0004455.005, LM0007422.001, LM0007425.001

import re
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.character_set import dstl_set_character_set
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.configure_sms_pdu_parameters import dstl_calculate_pdu_length
from dstl.sms.configure_sms_text_mode_parameters import dstl_set_sms_text_mode_parameters, \
    dstl_configure_sms_event_reporting, dstl_show_sms_text_mode_parameters
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.read_sms_message import dstl_read_sms_message
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.send_sms_message import dstl_send_sms_message, dstl_send_sms_message_from_memory
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.write_sms_to_memory import dstl_write_sms_to_memory


class SmoketestSms(BaseTest):
    """
    Intention:
    Simple check of send and receive SMS.
    Precondition:
    Module (DUT), Remote, Register DUT and remote to the network,
    Set proper Service Center Address via CSCA
    Enable SMS URCs via CNMI=2,1
    Set SMS text parameters via CSMP e.g. CSMP=17,167,0,0
    Clear all SMS from memory via AT+CMGD

    Description:
    1. Send SMS in "Text" mode directly from DUT to Remote.
    2. Send SMS in "Text" mode directly from Remote to DUT.
    3. Send SMS in "PDU" mode directly from DUT to Remote.
    4. Send SMS in "PDU" mode directly from Remote to DUT.
    5. Change SMS format via AT+CMGF to "Text" and save a message to "ME" memory using AT+CMGW
     on DUT (with remote number).
    6. Send SMS from "ME" memory using AT+CMSS from DUT to remote -Text Mode.
    7. Change SMS format to PDU via AT+CMGF.
    8: Send SMS from "ME" memory using AT+CMSS from DUT to remote -PDU Mode.
    9. Clear memory from saved messages on DUT and remote.

    Expected results:
    1. SMS should be sent in "Text" mode from DUT and received on Remote successfully.
    2. SMS should be sent in "Text" mode from Remote and received on DUT successfully.
    3. SMS should be sent in "PDU" mode from DUT and received on Remote successfully.
    4. SMS should be sent in "PDU" mode from Remote and received on DUT successfully.
    5. SMS format is set correctly to "Text" mode and message should be saved in "ME" memory.
    6. SMS sent correctly from "ME" memory in "Text" mode.
    7. SMS format is set correctly to "PDU" mode.
    8. SMS sent correctly from "ME" memory in "PDU" mode.
    9. All saved SMS messages has been deleted from Remote and DUT.
    """

    def setup(test):
        test.prepare_module(test.dut)
        test.prepare_module(test.r1)
        test.pdu_content = '1BF3F61C447F83D26E7A59EE0ED3D36F77980D72D7DBE2B21C'

    def run(test):
        test.log.step('Step 1: Send SMS in "Text" mode directly from DUT to Remote. ')
        test.expect(dstl_send_sms_message(test.dut, test.r1.sim.int_voice_nr, 'Test message',
                                          sms_format='Text'))
        test.expect(dstl_check_urc(test.r1, ".*CMTI.*"))
        message_index = re.search('CMTI:\s\"\S+\",\s*(\d{1,3})', test.r1.at1.last_response)
        if message_index:
            test.expect(re.search('Test message', dstl_read_sms_message(test.r1,
                                                                        message_index.group(1))))
        else:
            test.expect(False, msg="MSG not delivered or impossible to get MSG index!")

        test.log.step('Step 2: Send SMS in "Text" mode directly from Remote to DUT. ')
        test.expect(dstl_send_sms_message(test.r1, test.dut.sim.int_voice_nr, 'Test message',
                                          sms_format='Text'))
        test.expect(dstl_check_urc(test.dut, ".*CMTI.*"))
        message_index = re.search('CMTI:\s\"\S+\",\s*(\d{1,3})', test.dut.at1.last_response)
        if message_index:
            test.expect(re.search('Test message', dstl_read_sms_message(test.dut,
                                                                        message_index.group(1))))
        else:
            test.expect(False, msg="MSG not delivered or impossible to get MSG index!")

        test.log.step('Step 3: Send SMS in "PDU" mode directly from DUT to Remote. ')
        pdu = '{}1100{}0000FF{}'.format(test.dut.sim.sca_pdu, test.r1.sim.pdu, test.pdu_content)
        test.expect(dstl_select_sms_message_format(test.r1, sms_format='PDU'))
        dstl_send_sms_message(test.dut, dstl_calculate_pdu_length(pdu), sms_text=pdu,
                              sms_format="PDU", set_sms_format=True)
        test.expect(dstl_check_urc(test.r1, ".*CMTI.*"))
        message_index = re.search('CMTI:\s\"\S+\",\s*(\d{1,3})', test.r1.at1.last_response)
        if message_index:
            test.expect(re.search(test.pdu_content, dstl_read_sms_message(test.r1,
                                                                          message_index.group(1))))
        else:
            test.expect(False, msg="MSG not delivered or impossible to get MSG index!")

        test.log.step('Step 4: Send SMS in "PDU" mode directly from Remote to DUT. ')
        pdu = '{}1100{}0000FF{}'.format(test.r1.sim.sca_pdu, test.dut.sim.pdu, test.pdu_content)
        dstl_send_sms_message(test.r1, dstl_calculate_pdu_length(pdu), sms_text=pdu,
                              sms_format="PDU", set_sms_format=True)
        test.expect(dstl_check_urc(test.dut, ".*CMTI.*"))
        message_index = re.search('CMTI:\s\"\S+\",\s*(\d{1,3})', test.dut.at1.last_response)
        if message_index:
            test.expect(re.search(test.pdu_content, dstl_read_sms_message(test.dut,
                                                                          message_index.group(1))))
        else:
            test.expect(False, msg="MSG not delivered or impossible to get MSG index!")

        test.log.step('Step 5: Change SMS format via AT+CMGF to "Text" and save a message'
                      ' to "ME" memory using AT+CMGW on DUT (with remote number). ')
        test.expect(dstl_select_sms_message_format(test.dut))
        test.expect(dstl_select_sms_message_format(test.r1))
        test.expect(dstl_set_preferred_sms_memory(test.dut, preferred_storage='ME'))
        index = dstl_write_sms_to_memory(test.dut, sms_text='Test message',
                                         phone_num=test.r1.sim.int_voice_nr, return_index=True)

        test.log.step('Step 6: Send SMS from "ME" memory using AT+CMSS from'
                      ' DUT to remote -Text Mode.')
        test.expect(dstl_send_sms_message_from_memory(test.dut, index[0]))
        test.expect(dstl_check_urc(test.r1, ".*CMTI.*"))
        message_index = re.search('CMTI:\s\"\S+\",\s*(\d{1,3})', test.r1.at1.last_response)
        if message_index:
            test.expect(re.search('Test message', dstl_read_sms_message(test.r1,
                                                                        message_index.group(1))))
        else:
            test.expect(False, msg="MSG not delivered or impossible to get MSG index!")

        test.log.step('Step 7: Change SMS format to PDU via AT+CMGF. ')
        test.expect(dstl_select_sms_message_format(test.dut, sms_format='PDU'))
        test.expect(dstl_select_sms_message_format(test.r1, sms_format='PDU'))

        test.log.step('Step 8: Send SMS from "ME" memory using AT+CMSS from'
                      ' DUT to remote -PDU Mode.')
        # encoded 'Test message'
        expected_pdu_msg = '0CD4F29C0E6A97E7F3F0B90C'
        test.expect((dstl_send_sms_message_from_memory(test.dut, index[0])))
        test.expect(dstl_check_urc(test.r1, ".*CMTI.*"))
        message_index = re.search('CMTI:\s\"\S+\",\s*(\d{1,3})', test.r1.at1.last_response)
        if message_index:
            test.expect(re.search(expected_pdu_msg, dstl_read_sms_message(test.r1,
                                                                          message_index.group(1))))
        else:
            test.expect(False, msg="MSG not delivered or impossible to get MSG index!")

    def cleanup(test):
        test.log.step('Step 9: Clear memory from saved messages on DUT and remote.')
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_delete_all_sms_messages(test.r1))

    def prepare_module(test, device):
        dstl_detect(device)
        dstl_get_imei(device)
        test.expect(dstl_register_to_network(device))
        test.expect(dstl_select_sms_message_format(device))
        test.expect(dstl_set_preferred_sms_memory(device, preferred_storage='ME'))
        test.expect(dstl_delete_all_sms_messages(device))
        test.expect(dstl_set_character_set(device, 'GSM'))
        test.expect(dstl_set_sms_text_mode_parameters(device, "17", "167", "0", "0"))
        test.expect(dstl_configure_sms_event_reporting(device, "2", "1"))
        test.expect(dstl_set_sms_center_address(device, device.sim.sca_int))
        test.expect(dstl_show_sms_text_mode_parameters(device))


if "__main__" == __name__:
    unicorn.main()
