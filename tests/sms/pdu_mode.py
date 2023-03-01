# responsible: renata.bryla@globallogic.com
# location: Wroclaw
# TC0010476.001

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
from dstl.sms.configure_sms_pdu_parameters import dstl_calculate_pdu_length, \
    dstl_convert_number_to_pdu_number
from dstl.sms.configure_sms_text_mode_parameters import dstl_set_sms_text_mode_parameters
from dstl.sms.delete_sms import dstl_delete_all_sms_messages, dstl_delete_sms_message_from_index
from dstl.sms.read_sms_message import dstl_read_sms_message
from dstl.sms.select_message_service import dstl_set_message_service
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.send_sms_message import dstl_send_sms_message_from_memory, dstl_send_sms_message
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.sms_functions import dstl_enable_sms_urc
from dstl.sms.write_sms_to_memory import dstl_write_sms_to_memory


class Test(BaseTest):
    """
    TC0010476.001   PDUMode
    Write sms with different formats of receiver's address and content and send to them to another
    test module in PDU mode. Check the content of sent sms on receiving module.

    Check the following scenarios:
    0) write sms with incorrect PDU length as parameter of at+cmgw
    1) write sms 160,70,162 characters length with receiver's address
    2) write sms without receiver's address
    Send on of previously written sms with at+cmss :
    3) without receiver's address and format <toda>, and then with receiver's address
       but without format <toda>
    4) with correct national and international format <toda> of receiver's address ,
    5) with <toda> not corresponding to receiver's address
       (national address and international <toda> and vice versa)
    6) repeat 4 with directly sending (at+cmgs)
    7) repeat 5 with directly sending (at+cmgs)
    Read all received sms on second module with detailed description (at+csdh=1)
       and without (at+csdh=0)
    (not applicable for CDMA2k)
    """

    sms_timeout = 180
    sms_70_char = "4637D8181D9687C7F4B27CCE2EBBCF74740E1693CD6835DB0D9783C564335ACD76C3E56031D98" \
                  "C56B3DD7039584C36A3D56C375C0E1693CD6835DB0D978301"
    sms_70_char_text = "70characterslength9012345678901234567890123456789012345678901234567890"
    sms_160_char = "A0311B6C8C0ECBC3637A593E6797DD673A7A1E93CD6835DB0D9783C564335ACD76C3E56031D98" \
                   "C56B3DD7039584C36A3D56C375C0E1693CD6835DB0D9783C564335ACD76C3E56031D98C56B3D" \
                   "D7039584C36A3D56C375C0E1693CD6835DB0D9783C564335ACD76C3E56031D98C56B3DD70395" \
                   "84C36A3D56C375C0E1693CD6835DB0D9783C564335ACD76C3E560"
    sms_160_char_text = "160characterslengths1234567890123456789012345678901234567890123456789" \
                        "0123456789012345678901234567890123456789012345678901234567890123456789" \
                        "012345678901234567890"
    sms_162_char = "A2319B6C8C0ECBC3637A593E6797DD67347D1E0E87C3E170381C0E87C3E170381C0E87C3E170" \
                   "381C0E87C3E170381C0E87C3E170381C0E87C3E170381C0E87C3E170381C0E87C3E170381C0E" \
                   "87C3E170381C0E87C3E170381C0E87C3E170381C0E87C3E170381C0E87C3E170381C0E87C3E17" \
                   "0381C0E87C3E170381C0E87C3E170381C0E87C3E170381C0E87C3"
    sms_without_address = "1DD4F29C0EBAA7E9E8779D0E9297C7E5B4BD2C0785C96479793E07"
    sms_without_address_text = "Test without receiver address"

    def setup(test):
        test.prepare_module_to_test(test.dut, "===== Prepare DUT module to the test =====")
        test.prepare_module_to_test(test.r1, "===== Prepare REMOTE module to the test =====")

    def run(test):
        test.log.info("===== Start TS for TC: TC0010476.001 PDUMode =====")
        test.log.info("===== Check the following scenarios: =====")
        test.log.step("0) write sms with incorrect PDU length as parameter of at+cmgw")
        test.pdu = f'{test.dut.sim.sca_pdu}1100{test.r1.sim.pdu}0000FF' \
                   f'{"1469F7F82D9797C77410945805B1CBEE331D0D"}'
        test.expect(dstl_write_sms_to_memory(test.dut, sms_format="PDU",
                    length=int(dstl_calculate_pdu_length(test.pdu) + 10), pdu=test.pdu,
                    exp_resp=">.*|.*CMS ERROR"))

        test.log.step("1) write sms 160,70,162 characters length with receiver's address")
        test.log.info("===== write sms 160 characters length with receiver's address =====")
        test.pdu_160_char = f'{test.dut.sim.sca_pdu}1100{test.r1.sim.pdu}0000FF{test.sms_160_char}'
        msg_index_1 = test.expect(dstl_write_sms_to_memory(test.dut, sms_format="PDU",
                                  return_index=True, pdu=test.pdu_160_char))
        test.log.info("===== write sms 70 characters length with receiver's address =====")
        test.pdu_70_char = f'{test.dut.sim.sca_pdu}1100{test.r1.sim.pdu}0000FF{test.sms_70_char}'
        msg_index_2 = test.expect(dstl_write_sms_to_memory(test.dut, sms_format="PDU",
                                  return_index=True, pdu=test.pdu_70_char))
        test.log.info("===== write sms 162 characters length with receiver's address =====")
        test.pdu_162_char = f'{test.dut.sim.sca_pdu}1100{test.r1.sim.pdu}0000FF{test.sms_162_char}'
        test.expect(dstl_write_sms_to_memory(test.dut, sms_format="PDU", pdu=test.pdu_162_char,
                                             exp_resp=">.*|.*CMS ERROR"))

        test.log.step("2) write sms without receiver's address")
        test.pdu_without_receiver_addr = \
            f'{test.dut.sim.sca_pdu}110000810000FF{test.sms_without_address}'
        msg_index_3 = test.expect(dstl_write_sms_to_memory(test.dut, sms_format="PDU",
                                  return_index=True, pdu=test.pdu_without_receiver_addr))

        test.log.info("===== Send on of previously written sms with at+cmss: =====")
        test.log.step("3) without receiver's address and format <toda>, "
                      "and then with receiver's address but without format <toda>")
        test.log.info("===== Send previously sms without receiver's address and format <toda>=====")
        test.log.info("===== sms with 160 characters length =====")

        test.expect(dstl_send_sms_message_from_memory(test.dut, msg_index_1[0]))
        test.read_sms(test.sms_160_char_text)
        test.log.info("===== sms with sms 70 characters length =====")
        test.expect(dstl_send_sms_message_from_memory(test.dut, msg_index_2[0]))
        test.read_sms(test.sms_70_char_text)
        test.log.info("===== sms with without receiver's address -> should NOT be accepted =====")
        test.expect(not dstl_send_sms_message_from_memory(test.dut, msg_index_3[0]))

        test.log.info("===== Send previously sms with receiver's address "
                      "but without format <toda> =====")
        test.log.info("===== sms with 160 characters length =====")
        test.expect(dstl_send_sms_message_from_memory(test.dut, msg_index_1[0],
                                                      destination_addr=test.r1.sim.int_voice_nr))
        test.read_sms(test.sms_160_char_text)
        test.log.info("===== sms with sms 70 characters length =====")
        test.expect(dstl_send_sms_message_from_memory(test.dut, msg_index_2[0],
                                                      destination_addr=test.r1.sim.int_voice_nr))
        test.read_sms(test.sms_70_char_text)
        test.log.info("===== sms with without receiver's address =====")
        test.expect(dstl_send_sms_message_from_memory(test.dut, msg_index_3[0],
                                                      destination_addr=test.r1.sim.int_voice_nr))
        test.read_sms(test.sms_without_address_text)

        test.log.step("4) with correct national and international format <toda> "
                      "of receiver's address")
        test.log.info("===== Send previously sms with correct national format <toda> =====")
        test.log.info("===== sms with 160 characters length =====")
        test.send_msg_from_mem_with_toda(msg_index_1[0], test.r1.sim.nat_voice_nr, "129", ".*OK.*",
                                         test.sms_160_char_text)
        test.log.info("===== sms with sms 70 characters length =====")
        test.send_msg_from_mem_with_toda(msg_index_2[0], test.r1.sim.nat_voice_nr, "129", ".*OK.*",
                                         test.sms_70_char_text)
        test.log.info("===== sms with without receiver's address =====")
        test.send_msg_from_mem_with_toda(msg_index_3[0], test.r1.sim.nat_voice_nr, "129", ".*OK.*",
                                         test.sms_without_address_text)

        test.log.info("===== Send previously sms with correct international format <toda> =====")
        test.log.info("===== sms with 160 characters length =====")
        test.send_msg_from_mem_with_toda(msg_index_1[0], test.r1.sim.int_voice_nr, "145", ".*OK.*",
                                         test.sms_160_char_text)
        test.log.info("===== sms with sms 70 characters length =====")
        test.send_msg_from_mem_with_toda(msg_index_2[0], test.r1.sim.int_voice_nr, "145", ".*OK.*",
                                         test.sms_70_char_text)
        test.log.info("===== sms with without receiver's address =====")
        test.send_msg_from_mem_with_toda(msg_index_3[0], test.r1.sim.int_voice_nr, "145", ".*OK.*",
                                         test.sms_without_address_text)

        test.log.step("5) with <toda> not corresponding to receiver's address \n"
                      "(national address and international <toda> and vice versa)")
        test.log.info("===== Send sms with national address and international <toda> =====")
        test.log.info("===== sms with 160 characters length =====")
        test.send_msg_from_mem_with_toda(msg_index_1[0], test.r1.sim.nat_voice_nr, "145",
                                         ".*OK.*|.*CMS ERROR:.*", test.sms_160_char_text)
        test.log.info("===== sms with sms 70 characters length =====")
        test.send_msg_from_mem_with_toda(msg_index_2[0], test.r1.sim.nat_voice_nr, "145",
                                         ".*OK.*|.*CMS ERROR:.*", test.sms_70_char_text)
        test.log.info("===== sms with without receiver's address =====")
        test.send_msg_from_mem_with_toda(msg_index_3[0], test.r1.sim.nat_voice_nr, "145",
                                         ".*OK.*|.*CMS ERROR:.*", test.sms_without_address_text)

        test.log.info("===== Send sms with international address and national <toda> =====")
        test.log.info("===== sms with 160 characters length =====")
        test.send_msg_from_mem_with_toda(msg_index_1[0], test.r1.sim.int_voice_nr, "129",
                                         ".*OK.*|.*CMS ERROR:.*", test.sms_160_char_text)
        test.log.info("===== sms with sms 70 characters length =====")
        test.send_msg_from_mem_with_toda(msg_index_2[0], test.r1.sim.int_voice_nr, "129",
                                         ".*OK.*|.*CMS ERROR:.*", test.sms_70_char_text)
        test.log.info("===== sms with without receiver's address =====")
        test.send_msg_from_mem_with_toda(msg_index_3[0], test.r1.sim.int_voice_nr, "129",
                                         ".*OK.*|.*CMS ERROR:.*", test.sms_without_address_text)

        test.log.step("6) repeat 4 with directly sending (at+cmgs)")
        test.log.info("===== Send sms directly with correct national format <toda> =====")
        nat_nr_pdu = dstl_convert_number_to_pdu_number(test.r1.sim.nat_voice_nr)
        test.send_sms_pdu(nat_nr_pdu, "16F3F61C447F83DC617AFAED0EB341EE7A5B5C9603",
                          ".*OK.*", "sms to national number")

        test.log.info("===== Send sms directly with correct international format <toda> =====")
        int_number_pdu = test.r1.sim.pdu
        test.send_sms_pdu(int_number_pdu, "1BF3F61C447F83D26E7A59EE0ED3D36F77980D72D7DBE2B21C",
                          ".*OK.*", "sms to international number")

        test.log.step("7) repeat 5 with directly sending (at+cmgs)")
        test.log.info("===== Send sms directly with national address and international <toda>=====")
        nat_nr_int_toda_pdu = nat_nr_pdu[0:2] + "91" + nat_nr_pdu[4:]
        test.send_sms_pdu(nat_nr_int_toda_pdu,
                          "30F3F61C744FD3D12077989E7EBBC36C50984C9697E77350D84D06A5DDF4B2DC1DA6A7"
                          "DFEE301B447F93C3", ".*OK.*|.*CMS ERROR:.*",
                          "sms with national address and international toda")

        test.log.info("===== Send sms with directly international address and national <toda>=====")
        int_nr_nat_toda_pdu = int_number_pdu[0:2] + "81" + int_number_pdu[4:]
        test.send_sms_pdu(int_nr_nat_toda_pdu,
                          "30F3F61C744FD3D1A0B49B5E96BBC3F4F4DB1D6683C264B2BC3C9F83C26E32C81DA6A7"
                          "DFEE301B447F93C3", ".*OK.*|.*CMS ERROR:.*",
                          "sms with international address and national toda")

    def cleanup(test):
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_delete_all_sms_messages(test.r1))

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
        test.expect(dstl_set_preferred_sms_memory(module, "ME"))
        test.expect(dstl_delete_all_sms_messages(module))
        if module == test.dut:
            test.expect(dstl_select_sms_message_format(module, 'PDU'))
        else:
            test.expect(dstl_select_sms_message_format(module))

    def read_sms(test, msg_content, msg_delivery_dependent_of_network=False):
        dstl_check_urc(test.r1, ".*CMTI.*", timeout=test.sms_timeout)
        sms_received = re.search(r"CMTI.*\",\s*(\d)", test.r1.at1.last_response)
        if sms_received:
            test.log.info("===== Read received sms on second module "
                          "with detailed description (at+csdh=1) =====")
            test.expect(test.dut.at1.send_and_verify("AT+CSDH=1", ".*OK.*"))
            test.expect(dstl_read_sms_message(test.r1, sms_received[1]))
            test.log.info("Expected phrase : .*{}.*".format(msg_content))
            test.expect(re.search(".*{}.*".format(msg_content), test.r1.at1.last_response))
            test.log.info("===== Read received sms on second module "
                          "without detailed description (at+csdh=0) =====")
            test.expect(test.dut.at1.send_and_verify("AT+CSDH=0", ".*OK.*"))
            test.expect(dstl_read_sms_message(test.r1, sms_received[1]))
            test.log.info("Expected phrase : .*{}.*".format(msg_content))
            test.expect(re.search(".*{}.*".format(msg_content), test.r1.at1.last_response))
            test.expect(dstl_delete_sms_message_from_index(test.r1, sms_received[1]))
        else:
            if msg_delivery_dependent_of_network:
                test.log.info("Message has NOT been delivered (dependent on the network)")
            else:
                test.expect(False, msg="Message was not received")

    def send_msg_from_mem_with_toda(test, msg_index, dest_addr, toda, exp_resp, text):
        test.expect(dstl_send_sms_message_from_memory(test.dut, msg_index, dest_addr, toda=toda,
                                                      exp_resp=exp_resp))
        msg_response_content = re.search(".*CMSS:.*", test.dut.at1.last_response)
        if msg_response_content:
            test.read_sms(text, msg_delivery_dependent_of_network=True)
        else:
            test.log.info("Message has NOT been sent (dependent on the network)")

    def send_sms_pdu(test, dest_addr, pdu_content, exp_resp, text):
        pdu = '{}1100{}0000FF{}'.format(test.dut.sim.sca_pdu, dest_addr, pdu_content)
        test.expect(dstl_send_sms_message(test.dut, dstl_calculate_pdu_length(pdu), sms_text=pdu,
                                          sms_format="PDU", set_sms_format=False, set_sca=False,
                                          first_expect=".*>.*", exp_resp=exp_resp))
        msg_response_content = re.search(".*CMGS:.*", test.dut.at1.last_response)
        if msg_response_content:
            test.read_sms(text, msg_delivery_dependent_of_network=True)
        else:
            test.log.info("Message has NOT been sent (dependent on the network)")


if "__main__" == __name__:
    unicorn.main()