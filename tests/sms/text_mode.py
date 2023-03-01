#responsible: renata.bryla@globallogic.com
#location: Wroclaw
#TC0010475.001, TC0010475.003

import re
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.auxiliary_sms_functions import _convert_number_to_ucs2
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory


class Test(BaseTest):
    """
    TC0010475.001 / TC0010475.003   TextMode

    Write sms with different formats and content and send to them to another test module in text mode.
    Check the content of sent sms on receiving module.

    Step 1: write sms1 (160 characters) with address to memory.
    Step 1a: Send sms1 from memory
    Step 1b: Send sms1 from memory with different address.
    Step 2: write sms1 without receiver's address
    Step 3a: Send sms1 from memory without receiver's address and toda
    Step 3b: Send sms1 from memory with receiver's address but without toda
    Step 4a: Send sms1 from memory with correct national toda of receiver's address
    Step 4b: Send sms1 from memory with correct international toda of receiver's address
    Step 5a: Send sms1 from memory with incorrect national toda of receiver's address
    Step 5b: Send sms1 from memory with incorrect international toda of receiver's address
    Step 6a: Send sms1 directly without receiver's address and toda
    Step 6b: Send sms1 directly with receiver's address but without toda
    Step 6c: Send sms1 directly with correct national format toda of receiver's address
    Step 7a: Send sms1 directly with correct international toda of receiver's address
    Step 7b: Send sms1 directly with incorrect national toda of receiver's address
    Step 7c: Send sms1 directly with incorrect international toda of receiver's address

    Repeat steps 1-7c: use sms2 (70 characters) instead of sms1 with same scenarios

    Repeat step 1: write sms3 (162 characters) to memory - confirm sms3 was NOT saved OR sms3 was saved truncated.
    Try to send 162 characters message directly - it shouldn't be possible.

    Step 8: checking IPIS100091075 scenario - writing 160 characters long SMS in UCS2
    """

    sms_timeout = 180
    sms_1_160_char = "160znakow90123456789012345678901234567890123456789012345678901234567890123456789" \
                     "01234567890123456789012345678901234567890123456789012345678901234567890123456789"
    sms_2_70_char = "70znakow89012345678901234567890123456789012345678901234567890123456789"
    sms_3_162_char = "162znakow90123456789012345678901234567890123456789012345678901234567890123456789" \
                     "01234567890123456789012345678901234567890123456789012345678901234567890123456789aa"
    sms_160_char_ucs2 = "004E006F002E003400300020004100640064006900740069006F006E0061006C0020003100350030002000630068" \
                        "0061007200610063007400650072007300200074006F002000730065006E00640020006200650063006100750073" \
                        "006500200053004D0053002000680061007300200074006F002000680061007600650020006D006100780069006D" \
                        "0075006D0020006C0065006E006700740068002E00200049006E00200037002000620069007400200063006F0064" \
                        "0069006E00670020006D006100780069006D0075006D0020006C0065006E0067007400680020006F006600200073" \
                        "0068006F007200740020006D00650073007300610067006500200069007300200031003600300020006300680061" \
                        "007200610063007400650072007300200028004E006F002E0020002B00200031003500300029003000310032"

    def setup(test):
        test.prepare_module_to_test(test.dut, "===== Prepare DUT module to the test =====")
        test.prepare_module_to_test(test.r1, "===== Prepare REMOTE module to the test =====")

    def run(test):
        if test.dut.project.upper() == "VIPER":
            test.log.h2("Starting TP TC0010475.003 TextMode")
        else:
            test.log.h2("Starting TP TC0010475.001 TextMode")

        test.execute_step_1_7c("sms1 (160 characters)", test.sms_1_160_char)
        test.log.info("===== Delete ALL messages on both modules =====")
        test.delete_sms_from_memory(test.dut)
        test.delete_sms_from_memory(test.r1)

        test.log.step("Repeat steps 1-7c: use sms2 (70 characters) instead of sms1 with same scenarios")
        test.execute_step_1_7c("sms2 (70 characters)", test.sms_2_70_char)
        test.log.info("===== Delete ALL messages on both modules =====")
        test.delete_sms_from_memory(test.dut)
        test.delete_sms_from_memory(test.r1)

        test.log.step("Repeat step 1: write sms3 (162 characters) to memory - confirm sms3 was NOT saved OR sms3 was "
                      "saved truncated. [\r]Try to send 162 characters message directly - it shouldn't be possible.")
        test.write_or_send_sms("AT+CMGW=\"{}\"".format(test.r1.sim.nat_voice_nr), test.sms_3_162_char, ".*OK.*|.*ERROR.*")
        test.verify_messages(".*CMGW:.*", test.sms_3_162_char)
        test.write_or_send_sms("AT+CMGS=\"{}\",145".format(test.r1.sim.int_voice_nr), test.sms_3_162_char, ".*ERROR.*")

        test.log.step("Step 8: checking IPIS100091075 scenario - writing 160 characters long SMS in UCS2")
        test.expect(test.dut.at1.send_and_verify("AT+CSCS=\"UCS2\"", ".*OK.*"))
        test.write_or_send_sms("AT+CMGW=\"{}\"".format(_convert_number_to_ucs2(test.r1.sim.nat_voice_nr)),
                               test.sms_160_char_ucs2, ".*OK.*")
        test.verify_messages(".*CMGW:.*", test.sms_160_char_ucs2)

    def cleanup(test):
        test.delete_sms_from_memory(test.dut)
        test.dut.at1.send_and_verify("AT&F", ".*OK.*")
        test.dut.at1.send_and_verify("AT&W", ".*OK.*")
        test.delete_sms_from_memory(test.r1)
        test.r1.at1.send_and_verify("AT&F", ".*OK.*")
        test.r1.at1.send_and_verify("AT&W", ".*OK.*")

    def prepare_module_to_test(test, module, text):
        test.log.info(text)
        dstl_detect(module)
        dstl_get_imei(module)
        dstl_get_bootloader(module)
        dstl_set_scfg_urc_dst_ifc(module)
        test.expect(dstl_register_to_network(module), critical=True)
        test.expect(dstl_select_sms_message_format(module))
        test.expect(module.at1.send_and_verify('AT+CSCS="GSM"', ".*OK.*"))
        test.expect(module.at1.send_and_verify('AT^SCFG="SMS/AutoAck",0', ".*O.*"))
        test.expect(module.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))
        test.expect(dstl_set_sms_center_address(module, module.sim.sca_int))
        test.delete_sms_from_memory(module)

    def delete_sms_from_memory(test, module):
        test.log.info("Delete SMS from memory")
        dstl_set_preferred_sms_memory(module, "ME")
        dstl_delete_all_sms_messages(module)

    def execute_step_1_7c(test, sms_nr_of_characters, text_msg_content):
        test.log.step("Step 1: write {} with address to memory.".format(sms_nr_of_characters))
        test.write_or_send_sms("AT+CMGW=\"{}\"".format(test.r1.sim.nat_voice_nr), text_msg_content, ".*OK.*")
        cmgw_index_1 = test.verify_messages(".*CMGW:.*", text_msg_content)

        if cmgw_index_1 is not False:
            test.log.info("Timeout 10s before sending message from memory")
            test.sleep(10)
            test.log.step("Step 1a: Send {} from memory".format(sms_nr_of_characters[:4]))
            test.write_or_send_sms("AT+CMSS={}".format(cmgw_index_1), "", ".*OK.*")
            test.verify_messages(".*CMSS:.*", text_msg_content)

            test.log.info("Timeout 10s before sending message form memory with a different number")
            test.sleep(10)
            test.log.step("Step 1b: Send {} from memory with different address.".format(sms_nr_of_characters[:4]))
            test.write_or_send_sms("AT+CMSS={},\"{}\"".format(cmgw_index_1, test.r1.sim.int_voice_nr), "", ".*OK.*")
            test.verify_messages(".*CMSS:.*", text_msg_content)
        else:
            test.log.info("Steps 1a-1b CANNOT be realized - messages was NOT saved")

        test.log.step("Step 2: write {} without receiver's address".format(sms_nr_of_characters[:4]))
        test.write_or_send_sms("AT+CMGW", text_msg_content, ".*OK.*")
        cmgw_index_2 = test.verify_messages(".*CMGW:.*", text_msg_content)

        if cmgw_index_2 is not False:
            test.log.step("Step 3a: Send {} from memory without receiver's address and toda".
                          format(sms_nr_of_characters[:4]))
            test.write_or_send_sms("AT+CMSS={}".format(cmgw_index_2), "", ".*ERROR.*")

            test.log.step("Step 3b: Send {} from memory with receiver's address but without toda".
                          format(sms_nr_of_characters[:4]))
            test.write_or_send_sms("AT+CMSS={},\"{}\"".format(cmgw_index_2, test.r1.sim.int_voice_nr), "", ".*OK.*")
            test.verify_messages(".*CMSS:.*", text_msg_content)

            test.log.step("Step 4a: Send {} from memory with correct national toda of receiver's address".
                          format(sms_nr_of_characters[:4]))
            test.write_or_send_sms("AT+CMSS={},\"{}\",129".format(cmgw_index_2, test.r1.sim.nat_voice_nr), "", ".*OK.*")
            test.verify_messages(".*CMSS:.*", text_msg_content)

            test.log.step("Step 4b: Send {} from memory with correct international toda of receiver's address".
                          format(sms_nr_of_characters[:4]))
            test.write_or_send_sms("AT+CMSS={},\"{}\",145".format(cmgw_index_2, test.r1.sim.int_voice_nr), "", ".*OK.*")
            test.verify_messages(".*CMSS:.*", text_msg_content)

            test.log.step("Step 5a: Send {} from memory with incorrect national toda of receiver's address".
                          format(sms_nr_of_characters[:4]))
            test.write_or_send_sms("AT+CMSS={},\"{}\",129".format(cmgw_index_2, test.r1.sim.int_voice_nr), "",
                                   ".*OK.*|.*ERROR.*")
            test.verify_messages(".*CMSS:.*", text_msg_content)

            test.log.step("Step 5b: Send {} from memory with incorrect international toda of receiver's address".
                          format(sms_nr_of_characters[:4]))
            test.write_or_send_sms("AT+CMSS={},\"{}\",145".format(cmgw_index_2, test.r1.sim.nat_voice_nr), "",
                                   ".*OK.*|.*ERROR.*")
            test.verify_messages(".*CMSS:.*", text_msg_content)
        else:
            test.log.info("Steps 3a-5b CANNOT be realized - messages was NOT saved")

        test.log.step("Step 6a: Send {} directly without receiver's address and toda".format(sms_nr_of_characters[:4]))
        test.write_or_send_sms("AT+CMGS=", text_msg_content, ".*ERROR.*")

        test.log.step("Step 6b: Send {} directly with receiver's address but without toda".
                      format(sms_nr_of_characters[:4]))
        test.write_or_send_sms("AT+CMGS=\"{}\"".format(test.r1.sim.int_voice_nr), text_msg_content, ".*OK.*")
        test.verify_messages(".*CMGS:.*", text_msg_content)

        test.log.step("Step 6c: Send {} directly with correct national format toda of receiver's address".
                      format(sms_nr_of_characters[:4]))
        test.write_or_send_sms("AT+CMGS=\"{}\",129".format(test.r1.sim.nat_voice_nr), text_msg_content, ".*OK.*")
        test.verify_messages(".*CMGS:.*", text_msg_content)

        test.log.step("Step 7a: Send {} directly with correct international toda of receiver's address".
                      format(sms_nr_of_characters[:4]))
        test.write_or_send_sms("AT+CMGS=\"{}\",145".format(test.r1.sim.int_voice_nr), text_msg_content, ".*OK.*")
        test.verify_messages(".*CMGS:.*", text_msg_content)

        test.log.step("Step 7b: Send {} directly with incorrect national toda of receiver's address".
                      format(sms_nr_of_characters[:4]))
        test.write_or_send_sms("AT+CMGS=\"{}\",129".format(test.r1.sim.int_voice_nr), text_msg_content,
                               ".*OK.*|.*ERROR.*")
        test.verify_messages(".*CMGS:.*", text_msg_content)

        test.log.step("Step 7c: Send {} directly with incorrect international toda of receiver's address".
                      format(sms_nr_of_characters[:4]))
        test.write_or_send_sms("AT+CMGS=\"{}\",145".format(test.r1.sim.nat_voice_nr), text_msg_content,
                               ".*OK.*|.*ERROR.*")
        test.verify_messages(".*CMGS:.*", text_msg_content)

    def write_or_send_sms(test, command, msg_text, msg_response):
        if "CMSS" in command or command == "AT+CMGS=":
            test.expect(test.dut.at1.send_and_verify("{}".format(command), expect=msg_response,
                                                     timeout=test.sms_timeout))
        else:
            test.expect(test.dut.at1.send_and_verify('{}'.format(command), expect=">"))
            test.expect(test.dut.at1.send_and_verify(msg_text, end="\u001A", expect=msg_response,
                                                     timeout=test.sms_timeout))
        if msg_response == ".*ERROR.*":
            test.log.info("Message has NOT been accepted - as expected")
        elif msg_response == ".*OK.*|.*ERROR.*":
            test.log.info("Message has been or NOT save or sent (dependent on the network)")
        else:
            test.log.info("Message has been accepted - as expected")

    def verify_messages(test, expected_regex, msg_text):
        msg_response_content = re.search(expected_regex, test.dut.at1.last_response)
        if msg_response_content:
            if "CMGW" in expected_regex:
                test.log.info("{} command accepted - confirm that sms has been saved correctly".
                              format(expected_regex[2:6]))
                sms_index = re.search(r"CMGW:\s*(\d{1,3})", test.dut.at1.last_response)
                if msg_text == test.sms_3_162_char:
                    test.log.info("Message with 162 char accepted, but sms3 was saved truncated "
                                  "- read message without content verification")
                    test.expect(test.dut.at1.send_and_verify("AT+CMGR={}".format(sms_index[1]), ".*[\n\r].*OK.*"))
                else:
                    test.read_messages(test.dut, sms_index[1], msg_text)
                return sms_index[1]
            else:
                test.log.info("{} command accepted - wait for CMTI and read received SMS".
                              format(expected_regex[2:6]))
                urc = dstl_check_urc(test.r1, ".*CMTI.*", timeout=test.sms_timeout)
                if urc:
                    test.log.info("if CMTI occurs - read received SMS")
                    sms_index = re.search(r"CMTI:\s*\"ME\",\s*(\d{1,3})", test.r1.at1.last_response)
                    if sms_index:
                        test.read_messages(test.r1, sms_index[1], msg_text)
                    else:
                        test.expect(False, msg="SMS content incorrect")
                else:
                    test.log.info("Message has NOT been received (dependent on the network)")
                return False
        else:
            test.log.info("{} command NOT accepted".format(expected_regex[2:6]))
            return False

    def read_messages(test, module, index, text):
        test.expect(module.at1.send_and_verify("AT+CMGR={}".format(index), ".*[\n\r]{}.*OK.*".format(text)))


if "__main__" == __name__:
    unicorn.main()