# responsible: marcin.kossak@globallogic.com
# location: Koszalin
# TC0091825.001

from typing import Union
import re
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.scfg_sms import dstl_scfg_set_sms_auto_acknl, ListSmsAcknl
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.configuration.character_set import dstl_set_character_set
from dstl.configuration.reset_to_factory_default_state import \
    dstl_reset_settings_to_factory_default_values
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.configuration.store_user_defined_profile import dstl_store_user_defined_profile
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.security.set_sim_waiting_for_pin1 import dstl_set_sim_waiting_for_pin1
from dstl.sms.configure_sms_pdu_parameters import dstl_calculate_pdu_length
from dstl.sms.configure_sms_text_mode_parameters import dstl_configure_sms_event_reporting, \
    dstl_show_sms_text_mode_parameters, dstl_hide_sms_text_mode_parameters
from dstl.sms.configure_sms_text_mode_parameters import dstl_set_sms_text_mode_parameters
from dstl.sms.delete_sms import dstl_delete_all_sms_messages, dstl_delete_sms_message_from_index
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.select_message_service import dstl_set_message_service
from dstl.sms.send_sms_message import dstl_send_sms_message_from_memory
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.write_sms_to_memory import dstl_write_sms_to_memory
from dstl.sms.list_sms_message import dstl_list_supported_sms_status, \
    dstl_list_sms_messages_from_preferred_memory
from dstl.sms.sms_parameters import ListSmsMode, ListPDUMessagesInMemory, ListTextMessagesInMemory, \
    CsdhMode


class Test(BaseTest):
    """ TC0091825.001 TpAtCmglBasic
    This procedure provides the possibility of basic tests for the test and write command of +CMGL.

    1) Check command without PIN authentication (AT+CMGL of types: test, exec and write)

    2) Invalid parameters with PIN authentication:
    2.1) Check invalid parameters for the text mode (AT+CMGF=1) mode
    (AT+CMGL="HALLO", AT+CMGL=1, AT+CMGL= and AT+CMGL="").
    2.2) Check invalid parameters for PDU mode (AT+CMGF=0) mode
    (AT+CMGL=, AT+CMGL="", AT+CMGL=-1, AT+CMGL=7).

    3) Command usage not requiring SMSes in memory with PIN authentication:
    3.1) Check a test (AT+CMGL=?) and execute (AT+CMGL) commands in the PDU mode.
    3.2) Check a test and execute commands in the text mode.

    4) Tests on an empty memory with PIN authentication:
    4.1) Check write command for all supported parameters
    (AT+CMGL="STO UNSENT", "STO SENT", "REC UNREAD", "REC READ" and "ALL") in the text mode.
    4.2) Check write command for all supported parameters (from AT+CMGL=0 to AT+CMGL=4)
    in the PDU mode.

    5) Tests with SMS in memory:
    5.1) Write 2 SMSes in memory (AT+CMGW) as unsent and send one of them to yourself (AT+CMSS).
    5.2) Read the list of unsent SMSes (AT+CMGL="STO UNSENT") in the text mode.
    5.3) Read the list of sent SMSes (AT+CMGL="STO SENT") in the text mode.
    5.4) Read the unread SMS list (AT+CMGL="REC UNREAD") in the text mode.
    5.5) Read the read SMS list (AT+CMGL="REC READ") in the text mode.
    5.6) Send one already sent SMS from memory to yourself and read the list of SMSes in all statuses
    in the text mode (AT+CMGL="ALL") - it should contain SMSes of all statuses.
    5.7) Read the list of unsent SMSes in PDU mode (AT+CMGL=2).
    5.8) Read the list of sent SMSes in PDU mode (AT+CMGL3).
    5.9) Read the list of read SMSes in PDU mode (AT+CMGL=1).
    5.10) Send a new SMS to yourself and read the list of unread SMSes in PDU mode (AT+CMGL=0).
    5.11) Send a new SMS to yourself and list SMSes of all statuses in PDU mode (AT+CMGL=4).
    """

    sms_timeout = 360
    sms_in_memory_index = []
    # list of statuses in special order
    status_list_text = [ListTextMessagesInMemory.STO_UNSENT, ListTextMessagesInMemory.STO_SENT,
                        ListTextMessagesInMemory.REC_READ, ListTextMessagesInMemory.REC_UNREAD,
                        ListTextMessagesInMemory.ALL]
    status_list_pdu = [ListPDUMessagesInMemory.STO_UNSENT, ListPDUMessagesInMemory.STO_SENT,
                       ListPDUMessagesInMemory.REC_READ, ListPDUMessagesInMemory.REC_UNREAD,
                       ListPDUMessagesInMemory.ALL]

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_urc_dst_ifc(test.dut)
        test.expect(dstl_set_sim_waiting_for_pin1(test.dut))
        test.expect(dstl_set_error_message_format(test.dut))

    def run(test):
        test.log.h2("Starting TP TC0091825.001 TpAtCmglBasic")
        test.log.step('1) Check command without PIN authentication '
                      '(AT+CMGL of types: test, exec and write)')
        test.expect(dstl_list_supported_sms_status(
            test.dut, exp_resp=".*CMS ERROR: SIM PIN required.*"))
        test.expect(dstl_list_sms_messages_from_preferred_memory(
            test.dut, exp_resp=".*CMS ERROR: SIM PIN required.*"))
        test.expect(dstl_list_sms_messages_from_preferred_memory(
            test.dut, message_status="ALL", exp_resp=".*CMS ERROR: SIM PIN required.*"))

        test.log.step('2) Invalid parameters with PIN authentication')
        test.prepare_module_to_test_with_pin()
        test.log.step('2.1) Check invalid parameters for the text mode (AT+CMGF=1) mode '
                      '(AT+CMGL="HALLO", AT+CMGL=1, AT+CMGL= and AT+CMGL="")')
        test.expect(dstl_select_sms_message_format(test.dut, sms_format=ListSmsMode.Text.name))
        invalid_values = ['HALLO', 1, '', '=""']
        for single_value in invalid_values:
            test.expect(dstl_list_sms_messages_from_preferred_memory(
                test.dut, message_status=single_value, exp_resp=".*CMS ERROR.*"))

        test.log.step('2.2) Check invalid parameters for PDU mode (AT+CMGF=0) mode '
                      '(AT+CMGL=, AT+CMGL="", AT+CMGL=-1, AT+CMGL=7).')
        test.expect(dstl_select_sms_message_format(test.dut, sms_format=ListSmsMode.PDU.name))
        invalid_values = ["", '=""', -1, 7]
        for single_value in invalid_values:
            test.expect(dstl_list_sms_messages_from_preferred_memory(
                test.dut, message_status=single_value, exp_resp=".*CMS ERROR.*"))

        test.log.step('3) Command usage not requiring SMSes in memory with PIN authentication')
        test.log.step('3.1) Check a test (AT+CMGL=?) and execute (AT+CMGL) commands '
                      'in the PDU mode.')
        test.expect(dstl_select_sms_message_format(test.dut, sms_format=ListSmsMode.PDU.name))
        test.check_test_and_exec_command_on_empty_memory(ListSmsMode.PDU.name)

        test.log.step('3.2) Check a test and execute commands in the text mode.')
        test.expect(dstl_select_sms_message_format(test.dut, sms_format=ListSmsMode.Text.name))
        test.check_test_and_exec_command_on_empty_memory(ListSmsMode.Text.name)

        test.log.step('4) Tests on an empty memory with PIN authentication')
        test.log.step('4.1) Check write command for all supported parameters (AT+CMGL="STO UNSENT",'
                      ' "STO SENT", "REC UNREAD", "REC READ" and "ALL") in the text mode.')
        test.expect(dstl_select_sms_message_format(test.dut, sms_format=ListSmsMode.Text.name))
        test.check_write_command_with_empty_memory(ListSmsMode.Text.value, test.status_list_text)

        test.log.step('4.2) Check write command for all supported parameters '
                      '(from AT+CMGL=0 to AT+CMGL=4) in the PDU mode.')
        test.expect(dstl_select_sms_message_format(test.dut, sms_format=ListSmsMode.PDU.name))
        test.check_write_command_with_empty_memory(ListSmsMode.PDU.value, test.status_list_pdu)

        test.log.step('5) Tests with SMS in memory')
        test.log.info("===== Steps 5.2 - 5.6 will be executed with and without SMS header "
                      "(CSDH=1 and CSDH=0) =====")

        test.log.step('5.1) Write 2 SMSes in memory (AT+CMGW) as unsent '
                      'and send one of them to yourself (AT+CMSS).')
        for i in range(0, 2):
            sms_index = dstl_write_sms_to_memory(test.dut, "Test CMGL command", "TEXT",
                                                 return_index=True)
            if test.expect(sms_index is not False):
                test.sms_in_memory_index.append(sms_index[0])
            else:
                test.expect(False, msg='Problem with write sms to memory')

        if len(test.sms_in_memory_index) == 2:
            test.send_msg_from_memory(test.sms_in_memory_index[1], 2)
        else:
            test.expect(False, msg="===== CMGW command NOT accepted =====")

        if len(test.sms_in_memory_index) == 3:
            for mode in [CsdhMode.SHOW_DETAILED_HEADER_ON.value,
                         CsdhMode.SHOW_DETAILED_HEADER_OFF.value]:
                test.log.info("***** Tests CMGL command with SMS in memory and AT+CSDH={} *****"
                              .format(mode))
                if mode == CsdhMode.SHOW_DETAILED_HEADER_ON.value:
                    test.expect(dstl_show_sms_text_mode_parameters(test.dut))
                else:
                    test.expect(dstl_hide_sms_text_mode_parameters(test.dut))
                test.log.step('5.2) Read the list of unsent SMSes (AT+CMGL="STO UNSENT") '
                              'in the text mode.')
                test.check_cmgl_in_text(mode, ListTextMessagesInMemory.STO_UNSENT,
                                        test.sms_in_memory_index[0],
                                        [ListTextMessagesInMemory.STO_UNSENT],
                                        test.dut.sim.int_voice_nr)
                test.log.step('5.3) Read the list of sent SMSes (AT+CMGL="STO SENT") '
                              'in the text mode.')
                test.check_cmgl_in_text(mode, ListTextMessagesInMemory.STO_SENT,
                                        test.sms_in_memory_index[1],
                                        [ListTextMessagesInMemory.STO_SENT],
                                        test.dut.sim.int_voice_nr)
                test.log.step('5.4) Read the unread SMS list (AT+CMGL="REC UNREAD") '
                              'in the text mode.')
                if mode == ListSmsMode.Text.value:
                    index_rec_unread = test.sms_in_memory_index[2]
                else:
                    index_rec_unread = test.sms_in_memory_index[3]
                test.check_cmgl_in_text(mode, ListTextMessagesInMemory.REC_UNREAD,
                                        index_rec_unread,
                                        [ListTextMessagesInMemory.REC_UNREAD],
                                        test.dut.sim.int_voice_nr)
                test.log.step('5.5) Read the read SMS list (AT+CMGL="REC READ") in the text mode.')
                if mode == CsdhMode.SHOW_DETAILED_HEADER_OFF.value:
                    test.delete_one_sms_rec_read(test.sms_in_memory_index[3])
                test.check_cmgl_in_text(mode, ListTextMessagesInMemory.REC_READ,
                                        test.sms_in_memory_index[2],
                                        [ListTextMessagesInMemory.REC_READ],
                                        test.dut.sim.int_voice_nr)
                test.log.step('5.6) Send one already sent SMS from memory to yourself '
                              'and read the list of SMSes in all statuses in the text mode '
                              '(AT+CMGL="ALL") - it should contain SMSes of all statuses.')
                test.send_msg_from_memory(test.sms_in_memory_index[1], 3)
                test.check_cmgl_in_text(mode, ListTextMessagesInMemory.ALL,
                                        test.sms_in_memory_index,
                                        test.status_list_text,
                                        test.dut.sim.int_voice_nr)
                test.log.info("***** List default <stat> - execute EXEC command CMGL "
                              "- expected messages with status REC UNREAD *****")
                if len(test.sms_in_memory_index) == 4:
                    test.delete_one_sms_rec_read(test.sms_in_memory_index[3])
                test.send_msg_from_memory(test.sms_in_memory_index[1], 3)
                test.check_cmgl_in_text(mode, None, test.sms_in_memory_index[3],
                                        [ListTextMessagesInMemory.REC_UNREAD],
                                        test.dut.sim.int_voice_nr)
                test.delete_one_sms_rec_read(test.sms_in_memory_index[3])
                test.send_msg_from_memory(test.sms_in_memory_index[1], 3)

            if len(test.sms_in_memory_index) == 4:
                test.delete_one_sms_rec_read(test.sms_in_memory_index[3])
            test.log.info("===== Tests CMGL command with SMS in memory with PDU mode =====")
            test.expect(dstl_select_sms_message_format(test.dut, sms_format=ListSmsMode.PDU.name))
            test.log.step('5.7) Read the list of unsent SMSes in PDU mode (AT+CMGL=2).')
            test.check_cmgl_in_pdu(ListPDUMessagesInMemory.STO_UNSENT,
                                   [ListPDUMessagesInMemory.STO_UNSENT],
                                   test.sms_in_memory_index[0])
            test.log.step('5.8) Read the list of sent SMSes in PDU mode (AT+CMGL=3).')
            test.check_cmgl_in_pdu(ListPDUMessagesInMemory.STO_SENT,
                                   [ListPDUMessagesInMemory.STO_SENT],
                                   test.sms_in_memory_index[1])
            test.log.step('5.9) Read the list of read SMSes in PDU mode (AT+CMGL=1).')
            test.check_cmgl_in_pdu(ListPDUMessagesInMemory.REC_READ,
                                   [ListPDUMessagesInMemory.REC_READ],
                                   test.sms_in_memory_index[2])
            test.log.step('5.10) Send a new SMS to yourself and read the list of unread SMSes '
                          'in PDU mode (AT+CMGL=0).')
            test.send_msg_from_memory(test.sms_in_memory_index[1], 3)
            test.check_cmgl_in_pdu(ListPDUMessagesInMemory.REC_UNREAD,
                                   [ListPDUMessagesInMemory.REC_UNREAD],
                                   test.sms_in_memory_index[3])
            if len(test.sms_in_memory_index) == 4:
                test.delete_one_sms_rec_read(test.sms_in_memory_index[3])
            test.log.step('5.11) Send a new SMS to yourself and list SMSes of all statuses '
                          'in PDU mode (AT+CMGL=4).')
            test.send_msg_from_memory(test.sms_in_memory_index[1], 3)
            test.check_cmgl_in_pdu(ListPDUMessagesInMemory.ALL, test.status_list_pdu,
                                   test.sms_in_memory_index)
            test.log.info("***** List default <stat> - execute EXEC command CMGL "
                          "- expected messages with status REC UNREAD *****")
            if len(test.sms_in_memory_index) == 4:
                test.delete_one_sms_rec_read(test.sms_in_memory_index[3])
            test.send_msg_from_memory(test.sms_in_memory_index[1], 3)
            test.check_cmgl_in_pdu(None, [ListPDUMessagesInMemory.REC_UNREAD],
                                   test.sms_in_memory_index[3])
        else:
            test.expect(False, msg="===== Steps 5.2 - 5.11 CANNOT be realized "
                                   "- messages NOT in memory =====")

    def cleanup(test):
        test.log.info('===== Delete SMS from memory and restore values =====')
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_reset_settings_to_factory_default_values(test.dut))
        test.expect(dstl_store_user_defined_profile(test.dut))

    def prepare_module_to_test_with_pin(test):
        test.log.info("===== Prepare module to test with PIN authentication =====")
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_set_character_set(test.dut, 'GSM'))
        test.expect(dstl_scfg_set_sms_auto_acknl(test.dut,
                                                 ListSmsAcknl.NO_AUTOMATIC_ACKNOWLEDGEMENT))
        test.expect(dstl_set_sms_center_address(test.dut, test.dut.sim.sca_int))
        test.expect(dstl_set_message_service(test.dut, "1"))
        test.expect(dstl_configure_sms_event_reporting(test.dut, "2", "1"))
        test.expect(dstl_show_sms_text_mode_parameters(test.dut))
        test.expect(dstl_set_sms_text_mode_parameters(test.dut, '17', '167', '0', '0'))
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
        test.expect(dstl_delete_all_sms_messages(test.dut))

    def send_msg_from_memory(test, msg_index, index_list):
        test.expect(dstl_send_sms_message_from_memory(test.dut, msg_index, exp_resp=r".*OK.*"))
        msg_response_content = re.search(".*CMSS:.*", test.dut.at1.last_response)
        if msg_response_content:
            test.expect(dstl_check_urc(test.dut, ".*CMTI.*", timeout=test.sms_timeout))
            sms_index_received = re.search(r"CMTI:.*\",\s*(\d{1,3})", test.dut.at1.last_response)
            test.sms_in_memory_index.insert(index_list, sms_index_received[1])
        else:
            test.expect(False, msg="===== CMSS command NOT accepted =====")

    def delete_one_sms_rec_read(test, index):
        test.log.info("===== Delete one SMS with status REC READ =====")
        test.expect(dstl_delete_sms_message_from_index(test.dut, index))
        test.sms_in_memory_index.pop(int(index))

    def check_write_command_with_empty_memory(test, format_mode, status):
        if format_mode == ListSmsMode.Text.value:
            for single_status in status:
                test.expect(dstl_list_sms_messages_from_preferred_memory(test.dut, single_status))
                test.expect(not re.search(".*CMGL:.*", test.dut.at1.last_response))
        else:
            for single_status in status:
                test.expect(dstl_list_sms_messages_from_preferred_memory(test.dut, single_status))
                test.expect(not re.search(".*CMGL:.*", test.dut.at1.last_response))

    def check_test_and_exec_command_on_empty_memory(test, sms_format):
        if sms_format == ListSmsMode.Text.name:
            exp_resp = r'.*\+CMGL: \("REC UNREAD","REC READ","STO UNSENT","STO SENT","ALL"\).*OK.*'
        else:
            exp_resp = r".*\+CMGL: \(0(-|,1,2,3,)4\).*"
        test.expect(dstl_list_supported_sms_status(test.dut, exp_resp=exp_resp))
        test.expect(dstl_list_sms_messages_from_preferred_memory(test.dut, message_status=None))
        test.expect(not re.search(".*CMGL:.*", test.dut.at1.last_response))

    def check_cmgl_in_text(test, mode: int,
                           cmd_parameter: Union[str,
                                                None,
                                                ListPDUMessagesInMemory,
                                                ListTextMessagesInMemory],
                           index_list: list,
                           status: list,
                           voice_nr: str):
        """method to check text expected response
        :param mode:
            CsdhMode.SHOW_DETAILED_HEADER_ON.value,
            CsdhMode.SHOW_DETAILED_HEADER_OFF.value
        :param cmd_parameter: The parameter defines the status of SMS messages to be read
            REC_UNREAD: str = "REC UNREAD"  # for SMS reading commands
            REC_READ: str = "REC READ"
            STO_UNSENT: str = "STO UNSENT"  # for SMS writing commands
            STO_SENT: str = "STO SENT"
            ALL: str = "ALL"
        :param index_list: list of expected statuses like,
        :param status: list of ListTextMessagesInMemory elements
        :param voice_nr: phone number
        """
        test.expect(dstl_list_sms_messages_from_preferred_memory(test.dut,
                                                                 message_status=cmd_parameter))
        if mode == CsdhMode.SHOW_DETAILED_HEADER_OFF.value:
            for item in index_list:
                regex_status_rec = r"\+CMGL: {},\"{}\",\"\{}\",,\".*\"\s*[\n\r]{}.*".\
                    format(item, status[index_list.index(item)].value, voice_nr, "Test CMGL command")
                regex_status_sto = r"\+CMGL: {},\"{}\",\"\{}\",,\s*[\n\r]{}.*".\
                    format(item, status[index_list.index(item)].value, voice_nr, "Test CMGL command")
                if test.sms_in_memory_index.index(item) < 2:
                    test.log.info("Expected REGEX: {}".format(regex_status_sto))
                    test.expect(re.search(regex_status_sto, test.dut.at1.last_response))
                else:
                    test.log.info("Expected REGEX: {}".format(regex_status_rec))
                    test.expect(re.search(regex_status_rec, test.dut.at1.last_response))
        else:
            for item in index_list:
                regex_status_rec = r"\+CMGL: {},\"{}\",\"\{}\",,\".*\",145,17\s*[\n\r]{}.*".\
                    format(item, status[index_list.index(item)].value, voice_nr, "Test CMGL command")
                regex_status_sto = r"\+CMGL: {},\"{}\",\"\{}\",,,145,17\s*[\n\r]{}.*".\
                    format(item, status[index_list.index(item)].value, voice_nr, "Test CMGL command")

                if test.sms_in_memory_index.index(item) < 2:
                    test.log.info("Expected REGEX: {}".format(regex_status_sto))
                    test.expect(re.search(regex_status_sto, test.dut.at1.last_response))
                else:
                    test.log.info("Expected REGEX: {}".format(regex_status_rec))
                    test.expect(re.search(regex_status_rec, test.dut.at1.last_response))

    def check_cmgl_in_pdu(test, command: Union[str,
                                               None,
                                               ListPDUMessagesInMemory,
                                               ListTextMessagesInMemory],
                          status: list,
                          index_list: list):
        """method to check pdu expected response
        :param command: The parameter defines the status of SMS messages to be read
                REC_UNREAD: int = 0  # for SMS reading commands
                REC_READ: int = 1
                STO_UNSENT: int = 2  # for SMS writing commands
                STO_SENT: int = 3
                ALL: int = 4
        :param status: list of ListPDUMessagesInMemory elements
        :param index_list: list of expected statuses like,
        """
        test.expect(dstl_list_sms_messages_from_preferred_memory(test.dut, command))
        for item in index_list:
            msg_content = re.search(r"\S+{}".format("D4F29C0E1A368F4CD0F8DD6E87DD64"),
                                    test.dut.at1.last_response)[0]
            if msg_content:
                if index_list == test.sms_in_memory_index:
                    regex_pdu = r"\+CMGL: {},{},,.*\s*[\n\r].*{}.*{}\s*[\n\r].*".\
                        format(item, status[index_list.index(item)].value, test.dut.sim.pdu,
                               "D4F29C0E1A368F4CD0F8DD6E87DD64")
                else:
                    regex_pdu = r"\+CMGL: {},{},,{}\s*[\n\r].*{}.*{}\s*[\n\r].*". \
                        format(item, status[index_list.index(item)].value,
                               dstl_calculate_pdu_length(msg_content), test.dut.sim.pdu,
                               "D4F29C0E1A368F4CD0F8DD6E87DD64")
                test.log.info("Expected REGEX: {}".format(regex_pdu))
                test.expect(re.search(regex_pdu, test.dut.at1.last_response))
            else:
                test.expect(False, msg="Message not found")


if "__main__" == __name__:
    unicorn.main()
