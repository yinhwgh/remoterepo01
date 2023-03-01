#responsible: renata.bryla@globallogic.com
#location: Wroclaw
#TC0094885.001, TC0094885.002

import re
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.read_sms_message import dstl_read_sms_message
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.sms_functions import dstl_send_sms_message
from dstl.sms.write_sms_to_memory import dstl_write_sms_to_memory


class Test(BaseTest):
    """
    TC0094885.001 / TC0094885.002   UncompressedCompressedSms

    To check if uncompressed/compressed messages can be:
    - Set on DUT
    - Send by DUT
    - Received on DUT
    """

    SMS_TIMEOUT = 360
    UNCOMPRESSED_7BIT = [{"dcs": "0", "class": "Class None", "text": "999"},
                         {"dcs": "16", "class": "Class 0", "text": "000"},
                         {"dcs": "17", "class": "Class 1", "text": "111"},
                         {"dcs": "18", "class": "Class 2", "text": "222"},
                         {"dcs": "19", "class": "Class 3", "text": "333"},
                         {"dcs": "240", "class": "Class 0", "text": "000"},
                         {"dcs": "241", "class": "Class 1", "text": "111"},
                         {"dcs": "242", "class": "Class 2", "text": "222"},
                         {"dcs": "243", "class": "Class 3", "text": "333"}]
    UNCOMPRESSED_8BIT = [{"dcs": "4", "class": "Class None", "text": "393939"},
                         {"dcs": "20", "class": "Class 0", "text": "303030"},
                         {"dcs": "21", "class": "Class 1", "text": "313131"},
                         {"dcs": "22", "class": "Class 2", "text": "323232"},
                         {"dcs": "23", "class": "Class 3", "text": "333333"},
                         {"dcs": "244", "class": "Class 0", "text": "303030"},
                         {"dcs": "245", "class": "Class 1", "text": "313131"},
                         {"dcs": "246", "class": "Class 2", "text": "323232"},
                         {"dcs": "247", "class": "Class 3", "text": "333333"}]
    UNCOMPRESSED_16BIT = [{"dcs": "8", "class": "Class None", "text": "003900390039"},
                          {"dcs": "24", "class": "Class 0", "text": "003000300030"},
                          {"dcs": "25", "class": "Class 1", "text": "003100310031"},
                          {"dcs": "26", "class": "Class 2", "text": "003200320032"},
                          {"dcs": "27", "class": "Class 3", "text": "003300330033"}]
    COMPRESSED_7BIT = [{"dcs": "32", "class": "Class None", "text": "999"},
                       {"dcs": "48", "class": "Class 0", "text": "000"},
                       {"dcs": "49", "class": "Class 1", "text": "111"},
                       {"dcs": "50", "class": "Class 2", "text": "222"},
                       {"dcs": "51", "class": "Class 3", "text": "333"}]
    COMPRESSED_8BIT = [{"dcs": "36", "class": "Class None", "text": "393939"},
                       {"dcs": "52", "class": "Class 0", "text": "303030"},
                       {"dcs": "53", "class": "Class 1", "text": "313131"},
                       {"dcs": "54", "class": "Class 2", "text": "323232"},
                       {"dcs": "55", "class": "Class 3", "text": "333333"}]
    COMPRESSED_16BIT = [{"dcs": "40", "class": "Class None", "text": "003900390039"},
                        {"dcs": "56", "class": "Class 0", "text": "003000300030"},
                        {"dcs": "57", "class": "Class 1", "text": "003100310031"},
                        {"dcs": "58", "class": "Class 2", "text": "003200320032"},
                        {"dcs": "59", "class": "Class 3", "text": "003300330033"}]

    def setup(test):
        test.preparation(test.dut, "===== Preparation of DUT module =====")
        test.preparation(test.r1, "===== Preparation of REMOTE module =====")

    def run(test):
        if test.dut.project.upper() == "VIPER":
            test.log.h2("Starting TP TC0094885.002 UncompressedCompressedSms")
        else:
            test.log.h2("Starting TP TC0094885.001 UncompressedCompressedSms")
        test.log.step("Step 1. Prepare modules - on DUT and Remote set:[\n]"
                      "- ME as preferred message storage,[\n]"
                      "- text message format,[\n]"
                      '- AT^SCFG="SMS/AutoAck",0 (if supported on module),[\n]'
                      "- event reporting configuration at+cnmi=2,1,[\n]"
                      "- show SMS text mode parameters AT+CSDH=1[\n]"
                      "- properly SCA number")
        test.prepare_modules_to_test(test.dut, "===== Prepare DUT module to the test =====")
        test.prepare_modules_to_test(test.r1, "===== Prepare REMOTE module to the test =====")

        test.log.step("Uncompressed")
        test.log.step("Step 2. On DUT set below uncompressed 7bit Data Coding Schemes values[\n]"
                      "and send 1 SMS with each settings to Remote:[\n]"
                      "- at+csmp=17,167,0,0 (class none)[\n]"
                      "- at+csmp=17,167,0,16 (class 0)[\n]"
                      "- at+csmp=17,167,0,17 (class 1)[\n]"
                      "- at+csmp=17,167,0,18 (class 2)[\n]"
                      "- at+csmp=17,167,0,19 (class 3)[\n]"
                      "- at+csmp=17,167,0,240 (class 0)[\n]"
                      "- at+csmp=17,167,0,241 (class 1)[\n]"
                      "- at+csmp=17,167,0,242 (class 2)[\n]"
                      "- at+csmp=17,167,0,243 (class 3)")
        test.execute_step_for_uncompressed_sms(test.UNCOMPRESSED_7BIT, test.dut, test.r1)

        test.log.step("Step 3. On Remote set same uncompressed 7bit Data Coding Schemes values (from point 2)[\n]"
                      "and send 1 SMS with each setting to DUT")
        test.execute_step_for_uncompressed_sms(test.UNCOMPRESSED_7BIT, test.r1, test.dut)

        test.log.step("Step 4. On DUT set below uncompressed 8bit Data Coding Schemes values[\n]"
                      "and send 1 SMS with each settings to Remote:[\n]"
                      "- at+csmp=17,167,0,4 (class none)[\n]"
                      "- at+csmp=17,167,0,20 (class 0)[\n]"
                      "- at+csmp=17,167,0,21 (class 1)[\n]"
                      "- at+csmp=17,167,0,22 (class 2)[\n]"
                      "- at+csmp=17,167,0,23 (class 3)[\n]"
                      "- at+csmp=17,167,0,244 (class 0)[\n]"
                      "- at+csmp=17,167,0,245 (class 1)[\n]"
                      "- at+csmp=17,167,0,246 (class 2)[\n]"
                      "- at+csmp=17,167,0,247 (class 3)")
        test.execute_step_for_uncompressed_sms(test.UNCOMPRESSED_8BIT, test.dut, test.r1)

        test.log.step("Step 5. On Remote set same uncompressed 8bit Data Coding Schemes values (from point 4)[\n]"
                      "and send 1 SMS with each setting to DUT")
        test.execute_step_for_uncompressed_sms(test.UNCOMPRESSED_8BIT, test.r1, test.dut)

        test.log.step("Step 6. On DUT set below uncompressed 8bit Data Coding Schemes values[\n]"
                      "and send 1 SMS with each settings to Remote:[\n]"
                      "- at+csmp=17,167,0,8 (class none)[\n]"
                      "- at+csmp=17,167,0,24 (class 0)[\n]"
                      "- at+csmp=17,167,0,25 (class 1)[\n]"
                      "- at+csmp=17,167,0,26 (class 2)[\n]"
                      "- at+csmp=17,167,0,27 (class 3)")
        test.execute_step_for_uncompressed_sms(test.UNCOMPRESSED_16BIT, test.dut, test.r1)

        test.log.step("Step 7. On Remote set same uncompressed 16bit Data Coding Schemes values (from point 6)[\n]"
                      "and send 1 SMS with each setting to DUT")
        test.execute_step_for_uncompressed_sms(test.UNCOMPRESSED_16BIT, test.r1, test.dut)

        test.log.step("Compressed (if supported on DUT and in the network)")
        test.log.step("Step 8. On DUT set below compressed 7bit Data Coding Schemes values, save into memory "
                      "and read message on DUT,[\n]try to send 1 SMS to own number (if sending possible "
                      "wait for CMTI or CMT on DUT and read message without verifying dcs and data "
                      "- only OK is expected) with each settings:[\n]"
                      "- at+csmp=17,167,0,32 (class none)[\n]"
                      "- at+csmp=17,167,0,48 (class 0)[\n]"
                      "- at+csmp=17,167,0,49 (class 1)[\n]"
                      "- at+csmp=17,167,0,50 (class 2)[\n]"
                      "- at+csmp=17,167,0,51 (class 3)")
        test.execute_step_for_compressed_sms(test.COMPRESSED_7BIT)

        test.log.step("Step 9. On DUT set below compressed 8bit Data Coding Schemes values, save into memory "
                      "and read message on DUT,[\n]try to send 1 SMS to own number (if sending possible "
                      "wait for CMTI or CMT on DUT and read message without verifying dcs and data "
                      "- only OK is expected) with each settings:[\n]"
                      "- at+csmp=17,167,0,36 (class none)[\n]"
                      "- at+csmp=17,167,0,52 (class 0)[\n]"
                      "- at+csmp=17,167,0,53 (class 1)[\n]"
                      "- at+csmp=17,167,0,54 (class 2)[\n]"
                      "- at+csmp=17,167,0,55 (class 3)")
        test.execute_step_for_compressed_sms(test.COMPRESSED_8BIT)

        test.log.step("Step 10. On DUT set below compressed 16bit Data Coding Schemes values, save into memory "
                      "and read message on DUT,[\n]try to send 1 SMS to own number (if sending possible "
                      "wait for CMTI or CMT on DUT and read message without verifying dcs and data "
                      "- only OK is expected) with each settings:[\n]"
                      "- at+csmp=17,167,0,40 (class none)[\n]"
                      "- at+csmp=17,167,0,56 (class 0)[\n]"
                      "- at+csmp=17,167,0,57 (class 1)[\n]"
                      "- at+csmp=17,167,0,58 (class 2)[\n]"
                      "- at+csmp=17,167,0,59 (class 3)")
        test.execute_step_for_compressed_sms(test.COMPRESSED_16BIT)

    def cleanup(test):
        test.restore_values(test.dut)
        test.restore_values(test.r1)

    def preparation(test, module, text):
        test.log.info(text)
        dstl_detect(module)
        dstl_get_imei(module)
        dstl_get_bootloader(module)
        dstl_set_scfg_urc_dst_ifc(module)
        test.expect(dstl_register_to_network(module), critical=True)
        test.delete_sms_from_memory(module, ["SM", "ME"])
        test.expect(module.at1.send_and_verify('AT+CSCS="GSM"', ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT^SSDA=1", ".*O.*"))

    def prepare_modules_to_test(test, module, text):
        test.log.info(text)
        test.log.info("Setting ME as preferred message storage")
        test.expect(dstl_set_preferred_sms_memory(module, "ME"))
        test.log.info("Setting text message format")
        test.expect(dstl_select_sms_message_format(module))
        test.log.info('Setting AT^SCFG="SMS/AutoAck",0 (if supported on module)')
        test.expect(module.at1.send_and_verify('AT^SCFG="SMS/AutoAck",0', ".*O.*"))
        test.log.info("Setting event reporting configuration at+cnmi=2,1")
        test.expect(module.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*"))
        test.log.info("Setting show SMS text mode parameters AT+CSDH=1")
        test.expect(module.at1.send_and_verify("AT+CSDH=1", "OK"))
        test.log.info("Setting properly SCA number")
        test.expect(dstl_set_sms_center_address(module, module.sim.sca_int))

    def delete_sms_from_memory(test, module, memory):
        for mem in memory:
            test.log.info("Delete SMS from memory: {}".format(mem))
            test.expect(dstl_set_preferred_sms_memory(module, mem))
            test.expect(dstl_delete_all_sms_messages(module))

    def restore_values(test, module):
        test.expect(module.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT&W", ".*OK.*"))

    def execute_step_for_uncompressed_sms(test, list_dict, sender, receiver):
        if sender == test.dut:
            sender_name = "DUT"
            receiver_name = "REMOTE"
        else:
            sender_name = "REMOTE"
            receiver_name = "DUT"
        for item in list_dict:
            test.log.step("step: - at+csmp=17,167,0,{} ({})".format(item["dcs"], item["class"]))
            test.log.info("===== Setting data coding scheme to dcs: {} =====".format(item["dcs"]))
            test.expect(sender.at1.send_and_verify("AT+CSMP=17,167,0,{}".format(item["dcs"]), ".*OK.*"))
            test.log.info("===== Sending text message from sender: {} to receiver: {} =====".format(
                sender_name, receiver_name))
            test.expect(dstl_send_sms_message(sender, receiver.sim.int_voice_nr, item["text"]))
            test.log.info("===== Check received message on receiver: {} =====".format(receiver_name))
            if item["class"] == "Class 0":
                regex_cmt = ".*CMT:.*\"\{0}\",,\".*\",\d{{1,3}},\d{{1,3}},\d{{1,3}},{1},\".*\",\d{{1,3}},\d{{1,3}}\s*" \
                            "[\n\r]{2}.*".format(sender.sim.int_voice_nr, item["dcs"], item["text"])
                test.expect(dstl_check_urc(receiver, regex_cmt, timeout=test.SMS_TIMEOUT))
            else:
                test.expect(dstl_check_urc(receiver, ".*CMTI.*", timeout=test.SMS_TIMEOUT))
                sms_received = re.search(r"CMTI:.*\",\s*(\d{1,3})", receiver.at1.last_response)
                if item["class"] == "Class 2":
                    test.expect(dstl_set_preferred_sms_memory(receiver, "SM"))
                if sms_received:
                    test.expect(dstl_read_sms_message(receiver, sms_received[1]))
                    regex_cmti = ".*CMGR:.*\"REC UNREAD\",\"\{0}\",,\".*\",\d{{1,3}},\d{{1,3}},\d{{1,3}},{1},\".*\"," \
                                 "\d{{1,3}},\d{{1,3}}\s*[\n\r]{2}.*".format(sender.sim.int_voice_nr, item["dcs"],
                                                                            item["text"])
                    test.log.info("Expected REGEX: {}".format(regex_cmti))
                    test.expect(re.search(regex_cmti, receiver.at1.last_response))
                else:
                    test.expect(False, msg="Message was not received")
                if item["class"] == "Class 2":
                    test.expect(dstl_set_preferred_sms_memory(receiver, "ME"))
        test.delete_sms_from_memory(receiver, ["SM", "ME"])

    def execute_step_for_compressed_sms(test, list_dict):
        for item in list_dict:
            test.log.step("step: - at+csmp=17,167,0,{} ({})".format(item["dcs"], item["class"]))
            test.log.info("===== Setting data coding scheme to dcs: {} =====".format(item["dcs"]))
            test.expect(test.dut.at1.send_and_verify("AT+CSMP=17,167,0,{}".format(item["dcs"]), ".*OK.*"))
            test.log.info("===== Saved message into memory and read message on DUT =====")
            test.expect(dstl_write_sms_to_memory(test.dut, item["text"]))
            sms_saved = re.search(r"CMGW:\s*(\d{1,3})", test.dut.at1.last_response)
            if sms_saved:
                test.expect(dstl_read_sms_message(test.dut, sms_saved[1]))
                regex_msg_saved = ".*CMGR:.*\"STO UNSENT\",\"\{0}\",,\d{{1,3}},\d{{1,3}},\d{{1,3}},{1},\d{{1,3}}," \
                                  "\".*\",\d{{1,3}},\d{{1,3}}\s*[\n\r]{2}.*".format(test.dut.sim.int_voice_nr,
                                                                                    item["dcs"], item["text"])
                test.log.info("Expected REGEX: {}".format(regex_msg_saved))
                test.expect(re.search(regex_msg_saved, test.dut.at1.last_response))
            test.log.info("===== Try to send 1 SMS to own number (if sending possible wait for CMTI or CMT on DUT "
                          "and read message without verifying dcs and data - only OK is expected) =====")
            test.expect(test.dut.at1.send_and_verify('AT+CMGS="{}"'.format(test.dut.sim.int_voice_nr), expect=">"))
            test.expect(test.dut.at1.send_and_verify(item["text"], end="\u001A", expect=".*OK.*|.*ERROR.*",
                                                   timeout=test.SMS_TIMEOUT))
            msg_response_content = re.search(".*CMGS.*", test.dut.at1.last_response)
            if msg_response_content:
                test.log.info("CMGS command accepted - wait for CMTI or CMT on DUT (dependent on the network)")
                urc = dstl_check_urc(test.dut, ".*CMT.*", timeout=test.SMS_TIMEOUT)
                if urc and "CMTI:" in test.dut.at1.last_response:
                    test.log.info("CMTI message has been received[\n]"
                                  "read message without verifying dcs and data - only OK is expected)")
                    sms_delivered = re.search(r"CMTI:.*\"(.*)\",\s*(\d{1,3})", test.dut.at1.last_response)
                    if "SM" in sms_delivered[1]:
                        test.expect(dstl_set_preferred_sms_memory(test.dut, "SM"))
                    test.expect(dstl_read_sms_message(test.dut, sms_delivered[2]))
                    if "SM" in sms_delivered[1]:
                        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
                elif urc and "CMT:"in test.dut.at1.last_response:
                    test.log.info("CMT message has been received")
                else:
                    test.expect(False, "Message has NOT been received")
            else:
                test.log.info("Message has NOT been sent (dependent on the network)")
        test.delete_sms_from_memory(test.dut, ["SM", "ME"])


if "__main__" == __name__:
    unicorn.main()