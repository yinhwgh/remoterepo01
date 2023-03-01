# responsible: renata.bryla@globallogic.com
# location: Wroclaw
# TC0011201.001

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
from dstl.sms.configure_sms_text_mode_parameters import dstl_show_sms_text_mode_parameters, \
    dstl_configure_sms_event_reporting, dstl_read_sms_event_reporting_configuration, \
    dstl_enable_sms_class_0_display, dstl_confirm_acknowledgement_new_sms_deliver
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.list_sms_message import dstl_list_sms_messages_from_preferred_memory
from dstl.sms.read_sms_message import dstl_read_sms_message
from dstl.sms.select_message_service import dstl_set_message_service
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.send_sms_message import dstl_send_sms_message
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory


class Test(BaseTest):
    """
    TC0011201.001   SendReceiveIndication8bitPDU
    Test sending and receiving 8 Bit encoded SMSes with indication (CNMI) in PDU mode.

    Test the command AT+CNMI with the following values:
    1) AT+CNMI=0,0,0,0,1 and Class 0 until Class 3 and No-Class
    2) AT+CNMI=0,1,0,0,1 and Class 0 until Class 3 and No-Class
    3) AT+CNMI=0,2,0,0,1 and Class 0 until Class 3 and No-Class
    4) AT+CNMI=0,3,0,0,1 and Class 0 until Class 3 and No-Class
    5) AT+CNMI=1,0,0,0,1 and Class 0 until Class 3 and No-Class
    6) AT+CNMI=1,1,0,0,1 and Class 0 until Class 3 and No-Class
    7) AT+CNMI=1,2,0,0,1 and Class 0 until Class 3 and No-Class
    8) AT+CNMI=1,3,0,0,1 and Class 0 until Class 3 and No-Class

    Please perform this scenario with DUT as receiver and repeat with DUT as sender.

    Expected result:
    In case 1-5 no indication is shown,
    in other +CMTI: information appears (in case of SMS class 0 +CMT:).
    SMS class 2 must be saved on SIM.
    """

    SMS_TIMEOUT = 180
    DELAY_AFTER_CNMA = 15
    MODE_0 = "0"
    MODE_1 = "1"
    MT_0 = "0"
    MT_1 = "1"
    MT_2 = "2"
    MT_3 = "3"
    TEXT_8BIT_CLASS_0 = "636C6173732030"
    TEXT_8BIT_CLASS_1 = "636C6173732031"
    TEXT_8BIT_CLASS_2 = "636C6173732032"
    TEXT_8BIT_CLASS_3 = "636C6173732033"
    TEXT_8BIT_CLASS_NONE = "636C617373204E6F6E65"
    SMS_CLASS_0 = "0"
    SMS_CLASS_1 = "1"
    SMS_CLASS_2 = "2"
    SMS_CLASS_3 = "3"
    SMS_CLASS_NONE = "None"

    def setup(test):
        test.prepare_module_to_test(test.dut, "===== Prepare DUT module to the test =====")
        test.prepare_module_to_test(test.r1, "===== Prepare REMOTE module to the test =====")

    def run(test):
        test.log.step("Test the command AT+CNMI with the following values:")
        test.execute_all_steps("===== scenario with DUT as RECEIVER =====", test.r1, test.dut)
        test.execute_all_steps("===== scenario with DUT as SENDER =====", test.dut, test.r1)

    def cleanup(test):
        pass

    def delete_sms_from_memory(test, module, memory):
        for mem in memory:
            test.log.info("Delete SMS from memory: {}".format(mem))
            test.expect(dstl_set_preferred_sms_memory(module, mem))
            test.expect(dstl_delete_all_sms_messages(module))

    def prepare_module_to_test(test, module, text):
        test.log.info(text)
        dstl_detect(module)
        dstl_get_imei(module)
        dstl_get_bootloader(module)
        dstl_set_scfg_urc_dst_ifc(module)
        test.expect(dstl_register_to_network(module), critical=True)
        test.expect(dstl_set_error_message_format(module))
        test.expect(dstl_set_character_set(module, "GSM"))
        test.expect(dstl_set_message_service(module))
        test.expect(dstl_show_sms_text_mode_parameters(module))
        test.delete_sms_from_memory(module, ["SM", "ME"])
        test.expect(dstl_set_sms_center_address(module, module.sim.sca_int))
        test.expect(dstl_enable_sms_class_0_display(module))
        test.expect(dstl_select_sms_message_format(module, "PDU"))

    def execute_all_steps(test, info, sender, receiver):
        test.log.info(f"===== ===== =====\n{info}\n===== ===== =====")
        test.log.step("Step 1) AT+CNMI=0,0,0,0,1 and Class 0 until Class 3 and No-Class")
        test.configure_and_send_sms(sender, receiver, test.MODE_0, test.MT_0)

        test.log.step("Step 2) AT+CNMI=0,1,0,0,1 and Class 0 until Class 3 and No-Class")
        test.configure_and_send_sms(sender, receiver, test.MODE_0, test.MT_1)

        test.log.step("Step 3) AT+CNMI=0,2,0,0,1 and Class 0 until Class 3 and No-Class")
        test.configure_and_send_sms(sender, receiver, test.MODE_0, test.MT_2)

        test.log.step("Step 4) AT+CNMI=0,3,0,0,1 and Class 0 until Class 3 and No-Class")
        test.configure_and_send_sms(sender, receiver, test.MODE_0, test.MT_3)

        test.log.step("Step 5) AT+CNMI=1,0,0,0,1 and Class 0 until Class 3 and No-Class")
        test.configure_and_send_sms(sender, receiver, test.MODE_1, test.MT_0)

        test.log.step("Step 6) AT+CNMI=1,1,0,0,1 and Class 0 until Class 3 and No-Class")
        test.configure_and_send_sms(sender, receiver, test.MODE_1, test.MT_1)

        test.log.step("Step 7) AT+CNMI=1,2,0,0,1 and Class 0 until Class 3 and No-Class")
        test.configure_and_send_sms(sender, receiver, test.MODE_1, test.MT_2)

        test.log.step("Step 8) AT+CNMI=1,3,0,0,1 and Class 0 until Class 3 and No-Class")
        test.configure_and_send_sms(sender, receiver, test.MODE_1, test.MT_3)

    def execute_scenario_for_one_class(test, sender, receiver, mode, mt, sms_class):
        if sms_class == test.SMS_CLASS_0:
            msg_content = test.TEXT_8BIT_CLASS_0
            dcs = "14"
            content_length = "07"
        elif sms_class == test.SMS_CLASS_1:
            msg_content = test.TEXT_8BIT_CLASS_1
            dcs = "15"
            content_length = "07"
        elif sms_class == test.SMS_CLASS_2:
            msg_content = test.TEXT_8BIT_CLASS_2
            dcs = "16"
            content_length = "07"
        elif sms_class == test.SMS_CLASS_3:
            msg_content = test.TEXT_8BIT_CLASS_3
            dcs = "17"
            content_length = "07"
        else:
            msg_content = test.TEXT_8BIT_CLASS_NONE
            dcs = "04"
            content_length = "0A"

        test.log.info("===== set CNMI settings on receiver module =====")
        test.expect(dstl_configure_sms_event_reporting(receiver, mode, mt, "0", "0", "1"))
        test.log.info(f"===== prepare PDU on sender module for SMS class {sms_class} "
                      f"and send SMS =====")

        pdu = f'{sender.sim.sca_pdu}1100{receiver.sim.pdu}00{dcs}FF{content_length}{msg_content}'
        test.expect(dstl_send_sms_message(sender, dstl_calculate_pdu_length(pdu), sms_text=pdu,
                                          sms_format="PDU", set_sms_format=False, set_sca=False))
        test.verify_sms(receiver, mode, mt, sms_class)

    def configure_and_send_sms(test, sender, receiver, mode, mt):
        test.execute_scenario_for_one_class(sender, receiver, mode, mt, test.SMS_CLASS_0)
        test.execute_scenario_for_one_class(sender, receiver, mode, mt, test.SMS_CLASS_1)
        test.execute_scenario_for_one_class(sender, receiver, mode, mt, test.SMS_CLASS_2)
        test.execute_scenario_for_one_class(sender, receiver, mode, mt, test.SMS_CLASS_3)
        test.execute_scenario_for_one_class(sender, receiver, mode, mt, test.SMS_CLASS_NONE)
        test.delete_sms_from_memory(receiver, ["SM", "ME"])

    def verify_sms(test, module, mode, mt, sms_class):
        test.log.info("===== verify SMS =====")
        if sms_class == test.SMS_CLASS_0:
            msg_content = test.TEXT_8BIT_CLASS_0
            dcs = "14"
            content_length = "07"
        elif sms_class == test.SMS_CLASS_1:
            msg_content = test.TEXT_8BIT_CLASS_1
            dcs = "15"
            content_length = "07"
        elif sms_class == test.SMS_CLASS_2:
            msg_content = test.TEXT_8BIT_CLASS_2
            dcs = "16"
            content_length = "07"
        elif sms_class == test.SMS_CLASS_3:
            msg_content = test.TEXT_8BIT_CLASS_3
            dcs = "17"
            content_length = "07"
        else:
            msg_content = test.TEXT_8BIT_CLASS_NONE
            dcs = "04"
            content_length = "0A"

        if mode == test.MODE_0 or mt == test.MT_0:
            test.log.info("SMS should be stored. No +CMTI and +CMT. Waiting 180s")
            test.sleep(test.SMS_TIMEOUT)
            test.expect(not re.search(".*CMT.*", module.at1.last_response))
            if sms_class == test.SMS_CLASS_2:
                test.expect(dstl_set_preferred_sms_memory(module, "SM"))
            test.expect(dstl_list_sms_messages_from_preferred_memory(module, 4))
            if mt == test.MT_1 and sms_class == test.SMS_CLASS_0:
                if module == test.dut:
                    test.log.info(f"Automatic Acknowledgement expected. \n"
                                  f"NO FIND message .*{msg_content}.*")
                    test.expect(not re.search(f".*{msg_content}.*", module.at1.last_response))
                else:
                    test.log.info("On Remote module can be exist problem with save message class 0 "
                                  "in memory \n"
                                  "-> on Remote module SMS verification NOT will be realized") 
            else:
                test.log.info(rf"Expected phrase : .*{dcs}\d{{14}}{content_length}{msg_content}.*")
                test.expect(re.search(rf".*{dcs}\d{{14}}{content_length}{msg_content}.*",
                                      module.at1.last_response))
            if sms_class == test.SMS_CLASS_2:
                test.expect(dstl_set_preferred_sms_memory(module, "ME"))
        else:
            if mt == test.MT_1 and sms_class == test.SMS_CLASS_0:
                test.log.info(f"SMS shouldn't be stored. Wait for +CMT. \n"
                              f"Automatic Acknowledgement expected. Execute CNMA not needed. \n"
                              f"List SMS message - expected - NO FIND message .*{msg_content}.*")
                test.expect(dstl_check_urc(module,
                                           rf".*CMT:.*{dcs}\d{{14}}{content_length}{msg_content}.*",
                                           timeout=test.SMS_TIMEOUT))
                test.expect(dstl_list_sms_messages_from_preferred_memory(module, 4))
                test.expect(not re.search(f".*{msg_content}.*", module.at1.last_response))
            elif (sms_class == test.SMS_CLASS_0) or \
                    (mt == test.MT_2 and sms_class != test.SMS_CLASS_2) or \
                    (mt == test.MT_3 and sms_class == test.SMS_CLASS_0) or \
                    (mt == test.MT_3 and sms_class == test.SMS_CLASS_3):
                test.log.info("SMS shouldn't be stored. Wait for +CMT. \n"
                              "After SMS-DELIVER message - confirm CMT via AT+CNMA")
                test.expect(dstl_confirm_acknowledgement_new_sms_deliver(module, sms_format="PDU",
                            msg_text=rf"{dcs}\d{{14}}{content_length}{msg_content}"))
                test.sleep(test.DELAY_AFTER_CNMA)
                test.log.info(f"After confirm CMT message via CNMA - SMS shouldn't be stored. \n"
                              f"NO FIND message .*{msg_content}.*")
                test.expect(dstl_list_sms_messages_from_preferred_memory(module, 4))
                test.expect(not re.search(f".*{msg_content}.*", module.at1.last_response))
            else:
                test.log.info("SMS should be stored. Wait for +CMTI.")
                if sms_class == test.SMS_CLASS_2:
                    regex = r'CMTI.*"SM",\s*(\d)'
                else:
                    regex = r'CMTI.*"ME",\s*(\d)'
                test.expect(dstl_check_urc(module, ".*CMTI.*", timeout=test.SMS_TIMEOUT*2))
                sms_received = re.search(regex, module.at1.last_response)
                if sms_received:
                    if sms_class == test.SMS_CLASS_2:
                        test.expect(dstl_set_preferred_sms_memory(module, "SM"))
                    test.log.info("===== Read received sms on receiver module =====")
                    test.expect(dstl_read_sms_message(module, sms_received[1]))
                    test.log.info(rf"Expected phrase: .*{dcs}\d{{14}}{content_length}{msg_content}.*")
                    test.expect(re.search(rf".*{dcs}\d{{14}}{content_length}{msg_content}.*",
                                          module.at1.last_response))
                    if sms_class == test.SMS_CLASS_2:
                        test.expect(dstl_set_preferred_sms_memory(module, "ME"))
                else:
                    test.expect(False, msg="Message was not received")
        test.verify_cnmi_settings(module, mode, mt, sms_class)

    def verify_cnmi_settings(test, module, mode, mt, sms_class):
        if (mode == test.MODE_0 and mt == test.MT_2 and sms_class != test.SMS_CLASS_2) or \
            (mode == test.MODE_0 and mt == test.MT_3 and sms_class == test.SMS_CLASS_0) or \
                (mode == test.MODE_0 and mt == test.MT_3 and sms_class == test.SMS_CLASS_3):
            expected_mt = test.MT_0
        else:
            expected_mt = mt
        test.log.info("===== verify CNMI settings =====")
        current_cnmi_settings = test.expect(dstl_read_sms_event_reporting_configuration(module))
        expected_cnmi_settings = \
            {"mode": f"{mode}", "mt": f"{expected_mt}", "bm": "0", "ds": "0", "bfr": "1"}
        test.log.info(f'Expected CNMI settings: {expected_cnmi_settings}')
        if current_cnmi_settings == expected_cnmi_settings:
            test.log.info("CNMI settings as expected")
            test.expect(True)
        else:
            test.expect(False, msg="CNMI settings NOT as expected")


if "__main__" == __name__:
    unicorn.main()