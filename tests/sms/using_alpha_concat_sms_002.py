#responsible: renata.bryla@globallogic.com
#location: Wroclaw
#TC0010529.002

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
from dstl.sms.send_sms_message import dstl_send_sms_message_from_memory
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory


class Test(BaseTest):
    """ TC0010529.002 UsingAlphaConcatSms

    test alphabets which are used for concatenated sms: gsm, 8-bit and ucs2 with min, max and illegal text length
    and then try to send and receive.

    Precondition: Two modules, logged on to network. Provider supports concatenated short messages.

    STEPS FOR GSM7bit - ieia=16 bit and 8bit
    1. write SMS with max Length+2: 152+2 characters - ieia=16 bit
    2. write SMS with max Length : 152 characters - ieia=16 bit
    3. write SMS with min Length : 1 character - ieia=16 bit
    Repeat steps 1-3 for ieia = 8 bit (max length: 153)
    4. Read saved SMS – GSM

    STEPS FOR UCS2 - ieia=16 bit and 8bit
    1. Write SMS with max Length+2: 66+2 characters - ieia=16 bit
    2. Write SMS with max Length: 66 characters - ieia=16 bit
    3. Write SMS with min Length: 1 character - ieia=16 bit
    Repeat steps 1-3 for ieia = 8 bit (max length: 67)
    4. Read saved SMS - UCS2

    STEPS FOR GSM 8bit - ieia=16 bit and 8bit
    1. Write SMS with max Length+2: 133+2 characters - ieia=16 bit
    2. Write SMS with max Length: 133 characters - ieia=16 bit
    3. Write SMS with min Length : 1 character - ieia=16 bit
    Repeat steps 1-3 for ieia = 8 bit (max length: 134)
    4. Read saved SMS - GSM 8bit

    5a. send concatenated SMS which ieia = 16 bit
    5b. Send concatenated SMS which ieia = 8 bit
    6. Read received text messages
    7. send concatenated sms that consists of 2 (IEIa 8 bit) and 5 (IEIa 16 bit) segments

    8. Additional step according to the IPIS100130372 - after set AT^SCMW write command without mandatory parameters
    and AT+CSCA? module should NOT hangs up
    8.1 Check properly set of AT^SCMW write command and set AT+CSCA? then.
    8.2 Negative scenario: set AT^SCMW write command without some mandatory arguments and set AT+CSCA? then.
    Module should NOT hangs up!
    8.3 Set some at command to check if module has not hang up.
    """

    TIMEOUT_SHORT = 60
    TIMEOUT_SMS = 120
    TIMEOUT_SMS_LONG = 360
    STEPS = [{"descr": "GSM7bit", "char_set": "GSM", "dcs": "0"},
             {"descr": "UCS2", "char_set": "UCS2", "dcs": "8"},
             {"descr": "GSM8bit", "char_set": "GSM", "dcs": "4"}]
    list_index_scmw_8_bit = []
    list_index_scmw_16_bit = []
    list_index_cmti_8_bit = []
    list_index_cmti_16_bit = []
    SAVED_MSG_8_BIT_GSM7BIT = [{"seq": "1", "max": "255", "ieia": "8", "ref": "255",
                                "msg_text": "long153+2characters012345678901234567890123456789012345678901234567890"
                                            "1234567890123456789012345678901234567890123456789012345678901234567890"
                                            "123456789012345", "response": "ERROR"},
                               {"seq": "1", "max": "255", "ieia": "8", "ref": "255",
                                "msg_text": "max153char123456789012345678901234567890123456789012345678901234567890"
                                            "1234567890123456789012345678901234567890123456789012345678901234567890"
                                            "1234567890123", "response": "OK", "length": "153"},
                               {"seq": "2", "max": "255", "ieia": "8", "ref": "255",
                                "msg_text": "a", "response": "OK", "length": "1"}]
    SAVED_MSG_16_BIT_GSM7BIT = [{"seq": "1", "max": "255", "ieia": "16", "ref": "65535",
                                 "msg_text": "long152+2characters012345678901234567890123456789012345678901234567890"
                                             "1234567890123456789012345678901234567890123456789012345678901234567890"
                                             "12345678901234", "response": "ERROR"},
                                {"seq": "1", "max": "255", "ieia": "16", "ref": "65535",
                                 "msg_text": "max152char123456789012345678901234567890123456789012345678901234567890"
                                             "1234567890123456789012345678901234567890123456789012345678901234567890"
                                             "123456789012", "response": "OK", "length": "152"},
                                {"seq": "2", "max": "255", "ieia": "16", "ref": "65535",
                                 "msg_text": "z", "response": "OK", "length": "1"}]
    SAVED_MSG_8_BIT_UCS2 = [{"seq": "3", "max": "255", "ieia": "8", "ref": "255",
                             "msg_text": "0074006F006F0020006C006F006E006700200066006F00720020007500630073003200200061"
                                         "006E0064002000490045004900410020003800200062006900740020002D0020004100420043"
                                         "004400450046004700480049004A004B004C004D004E00300031003200330034003500360037"
                                         "003800390030003100320033003400350036003700380039", "response": "ERROR"},
                            {"seq": "3", "max": "255", "ieia": "8", "ref": "255",
                             "msg_text": "006D006100780020006C0065006E00670068007400200066006F007200200075006300730032"
                                         "00200061006E0064002000490045004900410020003800200062006900740020002D0020004F"
                                         "00500052005300540055005700580059005A0030003100320033003400350036003700380039"
                                         "0030003100320033003400350036003700380039", "response": "OK", "length": "67"},
                            {"seq": "4", "max": "255", "ieia": "8", "ref": "255",
                             "msg_text": "0062", "response": "OK", "length": "1"}]
    SAVED_MSG_16_BIT_UCS2 = [{"seq": "3", "max": "255", "ieia": "16", "ref": "65535",
                              "msg_text": "0074006F006F0020006C006F006E006700200066006F00720020007500630073003200200061"
                                          "006E00640020004900450049004100200031003600200062006900740020002D002000610062"
                                          "0063006400650066006700680069006A006B006C003000310032003300340035003600370038"
                                          "00390030003100320033003400350036003700380039", "response": "ERROR"},
                             {"seq": "3", "max": "255", "ieia": "16", "ref": "65535",
                              "msg_text": "006D006100780020006C0065006E00670068007400200066006F007200200075006300730032"
                                          "00200061006E00640020004900450049004100200031003600200062006900740020002D0020"
                                          "006D006E006F0070007200730074007500300031003200330034003500360037003800390030"
                                          "003100320033003400350036003700380039", "response": "OK", "length": "66"},
                             {"seq": "4", "max": "255", "ieia": "16", "ref": "65535",
                              "msg_text": "0078", "response": "OK", "length": "1"}]
    SAVED_MSG_8_BIT_GSM8BIT = [{"seq": "5", "max": "255", "ieia": "8", "ref": "255",
                                "msg_text": "746F6F206C6F6E6720666F72203862697420616E642049454941203820626974202D204142"
                                            "434445464748494A4B30313233343536373839303132333435363738393031323334353637"
                                            "38393031323334353637383930313233343536373839303132333435363738393031323334"
                                            "35363738393031323334353637383930313233343536373839", "response": "ERROR"},
                               {"seq": "5", "max": "255", "ieia": "8", "ref": "255",
                                "msg_text": "6D6178206C656E67687420666F72203862697420616E642049454941203820626974202D20"
                                            "4C4D4E4F505253303132333435363738393031323334353637383930313233343536373839"
                                            "30313233343536373839303132333435363738393031323334353637383930313233343536"
                                            "3738393031323334353637383930313233343536373839",
                                "response": "OK", "length": "134"},
                               {"seq": "6", "max": "255", "ieia": "8", "ref": "255", "msg_text": "41",
                                "response": "OK", "length": "1"}]
    SAVED_MSG_16_BIT_GSM8BIT = [{"seq": "5", "max": "255", "ieia": "16", "ref": "65535",
                                 "msg_text": "746F6F206C6F6E6720666F72203862697420616E64204945494120313620626974202D20"
                                             "616263646566676869303132333435363738393031323334353637383930313233343536"
                                             "373839303132333435363738393031323334353637383930313233343536373839303132"
                                             "333435363738393031323334353637383930313233343536373839",
                                 "response": "ERROR"},
                                {"seq": "5", "max": "255", "ieia": "16", "ref": "65535",
                                 "msg_text": "6D6178206C656E67687420666F72203862697420616E6420494549412031362062697420"
                                             "2D206A6B6C6D6E3031323334353637383930313233343536373839303132333435363738"
                                             "393031323334353637383930313233343536373839303132333435363738393031323334"
                                             "35363738393031323334353637383930313233343536373839",
                                 "response": "OK", "length": "133"},
                                {"seq": "6", "max": "255", "ieia": "16", "ref": "65535", "msg_text": "76",
                                 "response": "OK", "length": "1"}]
    SAVED_MSG_STEP_8_1 = {"seq": "0", "max": "0", "ieia": "8", "ref": "0", "msg_text": "test step 8.1",
                          "response": "OK", "length": "13"}
    SAVED_MSG_STEP_8_2 = {"response": "ERROR"}

    def setup(test):
        test.prepare_module_to_test(test.dut, "===== Preparation of DUT module =====")
        test.prepare_module_to_test(test.r1, "===== Preparation of REMOTE module =====")
        test.REMOTE_NUMBER = test.r1.sim.int_voice_nr
        test.REMOTE_NUMBER_UCS2 = _convert_number_to_ucs2(test.r1.sim.int_voice_nr)
        test.DUT_NUMBER = test.dut.sim.int_voice_nr
        test.DUT_NUMBER_UCS2 = _convert_number_to_ucs2(test.dut.sim.int_voice_nr)

    def run(test):
        test.log.h2("Starting TP for TC0010529.002 UsingAlphaConcatSms")
        test.execute_steps_1_4(test.STEPS[0], test.SAVED_MSG_16_BIT_GSM7BIT, test.SAVED_MSG_8_BIT_GSM7BIT)
        test.execute_steps_1_4(test.STEPS[1], test.SAVED_MSG_16_BIT_UCS2, test.SAVED_MSG_8_BIT_UCS2)
        test.execute_steps_1_4(test.STEPS[2], test.SAVED_MSG_16_BIT_GSM8BIT, test.SAVED_MSG_8_BIT_GSM8BIT)
        test.execute_steps_5_6()
        test.execute_step_7()
        test.execute_step_8()

    def cleanup(test):
        test.restore_values(test.dut)
        test.restore_values(test.r1)

    def restore_values(test, module):
        test.delete_sms_from_memory(module)
        test.expect(module.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT&W", ".*OK.*"))

    def prepare_module_to_test(test, module, text):
        test.log.info(text)
        dstl_detect(module)
        dstl_get_imei(module)
        dstl_get_bootloader(module)
        dstl_set_scfg_urc_dst_ifc(module)
        test.expect(dstl_register_to_network(module), critical=True)
        test.expect(module.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
        test.expect(dstl_select_sms_message_format(module))
        test.expect(module.at1.send_and_verify('AT+CSCS="GSM"', ".*OK.*"))
        test.expect(dstl_set_sms_center_address(module, module.sim.sca_int))
        test.expect(module.at1.send_and_verify("AT+CSMS=1", ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT+CSDH=1", "OK"))
        test.delete_sms_from_memory(module)

    def delete_sms_from_memory(test, module):
        test.expect(dstl_set_preferred_sms_memory(module, "ME"))
        test.expect(dstl_delete_all_sms_messages(module))

    def set_dcs_via_csmp(test, module, dcs):
        test.expect(module.at1.send_and_verify("AT+CSMP=17,167,0,{}".format(dcs), ".*OK.*"))

    def set_character_set(test, module, alphabet):
        test.expect(module.at1.send_and_verify("AT+CSCS=\"{}\"".format(alphabet), "OK"))

    def check_sca_values(test):
        test.expect(test.dut.at1.send_and_verify("AT+CSCA?", r'.*CSCA: "\{}",145.*OK.*'.format(test.dut.sim.sca_int)))

    def get_sms_index(test, module, regex, command):
        response_content = test.expect(re.search(regex, module.at1.last_response))
        if response_content:
            msg_index = response_content.group(1)
            test.log.info("Index for the {} is: {}".format(command, msg_index))
            return int(msg_index)
        else:
            return test.log.error("Fail to get value of: {}".format(command))

    def send_concat_msg_from_memory(test, index_list, list_index_cmti):
        if len(index_list) == 6:
            test.log.info("Send messages from DUT memory with indexes: {}".format(index_list))
            for item in index_list:
                test.expect(dstl_send_sms_message_from_memory(test.dut, item))
                test.expect(dstl_check_urc(test.r1, ".*CMTI.*", timeout=test.TIMEOUT_SMS_LONG))
                list_index_cmti.append(test.get_sms_index(test.r1, r".*CMTI.*,\s*(\d{1,3})", "CMTI"))
                test.expect(test.r1.at1.send_and_verify("AT+CPMS?", ".*OK.*"))
            return list_index_cmti
        else:
            test.expect(False, msg="NOT all expected messages in memory - step will be omitted")

    def write_concat_msg(test, content_dict, da_number, list_index_scmw):
        if content_dict == test.SAVED_MSG_STEP_8_2:
            test.expect(test.dut.at1.send_and_verify('AT^SCMW="{}"'.format(da_number), expect='.*{}.*'.format(
                content_dict['response']), timeout=test.TIMEOUT_SHORT))
        else:
            test.expect(test.dut.at1.send_and_verify('AT^SCMW="{}",,,{},{},{},{}'.format(
                da_number, content_dict['seq'], content_dict['max'], content_dict['ieia'], content_dict['ref']),
                expect='.*>.*'))
            test.expect(test.dut.at1.send_and_verify(content_dict['msg_text'], end="\u001A", expect='.*{}.*'.format(
                content_dict['response']), timeout=test.TIMEOUT_SHORT))
            if content_dict['response'] == 'OK':
                list_index_scmw.append(test.get_sms_index(test.dut, r".*SCMW:\s*(\d{1,3})", "SCMW"))
                return list_index_scmw

    def read_concat_msg(test, module, index, content_dict, char_set):
        if index is not None:
            test.expect(module.at1.send_and_verify('AT^SCMR={}'.format(index), ".*OK.*"))
            if module == test.dut:
                status = "STO UNSENT"
                da_number = test.REMOTE_NUMBER
            else:
                status = "REC UNREAD"
                da_number = test.DUT_NUMBER
            if char_set == "UCS2":
                if module == test.dut:
                    da_number = test.REMOTE_NUMBER_UCS2
                else:
                    da_number = test.DUT_NUMBER_UCS2
                regex = r"\^SCMR:\s*\"{}\",\"{}\",.*{},{},{},{},{}\s*[\n\r].*{}\s*".format(
                    status, da_number, content_dict["length"], content_dict["seq"], content_dict["max"],
                    content_dict["ieia"], content_dict["ref"], content_dict["msg_text"])
            else:
                regex = r"\^SCMR:\s*\"{}\",\"\{}\",.*{},{},{},{},{}\s*[\n\r].*{}\s*".format(
                    status, da_number, content_dict["length"], content_dict["seq"], content_dict["max"],
                    content_dict["ieia"], content_dict["ref"], content_dict["msg_text"])
            test.log.info("Expected REGEX: {}".format(regex))
            test.expect(re.search(regex, module.at1.last_response))
        else:
            test.expect(False, msg="Message not in memory")

    def send_concat_msg_directly(test, max, ieia, ref):
        for segment in range(1, (max + 1)):
            test.log.info("*** send SMS {}/{} ***".format(segment, max))
            test.expect(test.dut.at1.send_and_verify("AT^SCMS=\"{}\",,{},{},{},{}".format(
                test.r1.sim.int_voice_nr, segment, max, ieia, ref), expect=">"))
            test.expect(test.dut.at1.send_and_verify("SCMS segment {} IEIA: {} and REF: {}".format(segment, ieia, ref),
                        end="\u001A", expect=".*OK.*", timeout=test.TIMEOUT_SMS))
            if dstl_check_urc(test.r1, ".*CMTI.*", timeout=test.TIMEOUT_SMS_LONG):
                sms_index = test.get_sms_index(test.r1, r".*CMTI.*,\s*(\d{1,3})", "CMTI")
                test.expect(test.r1.at1.send_and_verify('AT^SCMR={}'.format(sms_index), ".*OK.*"))
                regex = r"\^SCMR:\s*\"REC UNREAD\",\"\{}\",.*,{},{},{},{}\s*[\n\r].*{}\s*".format(
                    test.DUT_NUMBER, segment, max, ieia, ref,
                    "SCMS segment {} IEIA: {} and REF: {}".format(segment, ieia, ref))
                test.log.info("Expected REGEX: {}".format(regex))
                test.expect(re.search(regex, test.r1.at1.last_response))
            else:
                test.log.error("Message was not received")

    def execute_steps_1_3(test, steps_dict, list_dict_saved, list_index_scmw):
        if list_dict_saved == test.SAVED_MSG_16_BIT_UCS2 or list_dict_saved == test.SAVED_MSG_8_BIT_UCS2:
            da_number = test.REMOTE_NUMBER_UCS2
        else:
            da_number = test.REMOTE_NUMBER
        test.log.info("===== STEPS FOR {} - ieia = {} bit =====".format(steps_dict["descr"], list_dict_saved[0]["ieia"]))
        test.log.step("Step 1. write SMS with max Length+2: {}+2 characters - ieia={} bit".format(
            list_dict_saved[1]["length"], list_dict_saved[0]["ieia"]))
        test.write_concat_msg(list_dict_saved[0], da_number, [])
        test.log.step("Step 2. write SMS with max Length : {} characters - ieia={} bit".format(
            list_dict_saved[1]["length"], list_dict_saved[1]["ieia"]))
        test.write_concat_msg(list_dict_saved[1], da_number, list_index_scmw)
        test.log.step("Step 3. write SMS with min Length : 1 character - ieia={} bit".format(
            list_dict_saved[2]["ieia"]))
        test.write_concat_msg(list_dict_saved[2], da_number, list_index_scmw)

    def execute_steps_1_4(test, steps_dict, list_dict_saved_16bit, list_dict_saved_8bit):
        test.log.step("STEPS FOR {} - ieia=16bit and 8bit".format(steps_dict["descr"]))
        test.set_character_set(test.dut, steps_dict["char_set"])
        test.set_dcs_via_csmp(test.dut, steps_dict["dcs"])
        test.execute_steps_1_3(steps_dict, list_dict_saved_16bit, test.list_index_scmw_16_bit)

        test.log.step("Repeat steps 1-3 for ieia = 8 bit (max length: {})".format(list_dict_saved_8bit[1]["length"]))
        test.execute_steps_1_3(steps_dict, list_dict_saved_8bit, test.list_index_scmw_8_bit)

        test.log.step("Step 4. Read saved SMS for {}".format(steps_dict["descr"]))
        if steps_dict["descr"] == "GSM7bit":
            index_list = [test.list_index_scmw_16_bit[0], test.list_index_scmw_16_bit[1],
                          test.list_index_scmw_8_bit[0], test.list_index_scmw_8_bit[1]]
        elif steps_dict["descr"] == "UCS2":
            index_list = [test.list_index_scmw_16_bit[2], test.list_index_scmw_16_bit[3],
                          test.list_index_scmw_8_bit[2], test.list_index_scmw_8_bit[3]]
        else:
            index_list = [test.list_index_scmw_16_bit[4], test.list_index_scmw_16_bit[5],
                          test.list_index_scmw_8_bit[4], test.list_index_scmw_8_bit[5]]
        if len(index_list) == 4:
            test.log.info("Read messages on DUT with indexes: {}".format(index_list))
            test.log.info("===== Read sms with max Length : {} characters - ieia=16 bit =====".format(
                list_dict_saved_16bit[1]["length"]))
            test.read_concat_msg(test.dut, index_list[0], list_dict_saved_16bit[1], steps_dict["char_set"])
            test.log.info("===== Read sms with min Length : 1 character ieia=16 bit =====")
            test.read_concat_msg(test.dut, index_list[1], list_dict_saved_16bit[2], steps_dict["char_set"])
            test.log.info("===== Read sms with max Length : {} characters - ieia=8 bit =====".format(
                list_dict_saved_8bit[1]["length"]))
            test.read_concat_msg(test.dut, index_list[2], list_dict_saved_8bit[1], steps_dict["char_set"])
            test.log.info("===== Read sms with min Length : 1 character - ieia=8 bit =====")
            test.read_concat_msg(test.dut, index_list[3], list_dict_saved_8bit[2], steps_dict["char_set"])
        else:
            test.expect(False, msg="Message not in memory index")

    def execute_steps_5_6(test):
        test.log.step("Step 5a. send concatenated SMS which ieia = 16 bit")
        test.send_concat_msg_from_memory(test.list_index_scmw_16_bit, test.list_index_cmti_16_bit)

        test.log.step("Step 5b. Send concatenated SMS which ieia = 8 bit")
        test.send_concat_msg_from_memory(test.list_index_scmw_8_bit, test.list_index_cmti_8_bit)

        test.log.step("Step 6. Read received text messages")
        test.log.info("===== Read messages for ieia=16 bit on REMOTE module - indexes: {} =====".format(
            test.list_index_cmti_16_bit))
        if len(test.list_index_cmti_16_bit) == 6:
            test.log.info("===== Read sms with max Length - alphabet: GSM7bit =====")
            test.read_concat_msg(test.r1, test.list_index_cmti_16_bit[0], test.SAVED_MSG_16_BIT_GSM7BIT[1], "GSM")
            test.log.info("===== Read sms with min Length - alphabet: GSM7bit =====")
            test.read_concat_msg(test.r1, test.list_index_cmti_16_bit[1], test.SAVED_MSG_16_BIT_GSM7BIT[2], "GSM")
            test.log.info("===== Read sms with max Length - alphabet: UCS2 =====")
            test.read_concat_msg(test.r1, test.list_index_cmti_16_bit[2], test.SAVED_MSG_16_BIT_UCS2[1], "GSM")
            test.log.info("===== Read sms with min Length - alphabet: UCS2 =====")
            test.read_concat_msg(test.r1, test.list_index_cmti_16_bit[3], test.SAVED_MSG_16_BIT_UCS2[2], "GSM")
            test.log.info("===== Read sms with max Length - alphabet: GSM7bit =====")
            test.read_concat_msg(test.r1, test.list_index_cmti_16_bit[4], test.SAVED_MSG_16_BIT_GSM8BIT[1], "GSM")
            test.log.info("===== Read sms with min Length - alphabet: GSM7bit =====")
            test.read_concat_msg(test.r1, test.list_index_cmti_16_bit[5], test.SAVED_MSG_16_BIT_GSM8BIT[2], "GSM")
        else:
            test.expect(False, msg="Message not in memory index")
        test.log.info("===== Read messages for ieia=8 bit on REMOTE module - indexes: {} =====".format(
            test.list_index_cmti_8_bit))
        if len(test.list_index_cmti_8_bit) == 6:
            test.log.info("===== Read sms with max Length - alphabet: GSM7bit =====")
            test.read_concat_msg(test.r1, test.list_index_cmti_8_bit[0], test.SAVED_MSG_8_BIT_GSM7BIT[1], "GSM")
            test.log.info("===== Read sms with min Length - alphabet: GSM7bit =====")
            test.read_concat_msg(test.r1, test.list_index_cmti_8_bit[1], test.SAVED_MSG_8_BIT_GSM7BIT[2], "GSM")
            test.log.info("===== Read sms with max Length - alphabet: UCS2 =====")
            test.read_concat_msg(test.r1, test.list_index_cmti_8_bit[2], test.SAVED_MSG_8_BIT_UCS2[1], "GSM")
            test.log.info("===== Read sms with min Length - alphabet: UCS2 =====")
            test.read_concat_msg(test.r1, test.list_index_cmti_8_bit[3], test.SAVED_MSG_8_BIT_UCS2[2], "GSM")
            test.log.info("===== Read sms with max Length - alphabet: GSM7bit =====")
            test.read_concat_msg(test.r1, test.list_index_cmti_8_bit[4], test.SAVED_MSG_8_BIT_GSM8BIT[1], "GSM")
            test.log.info("===== Read sms with min Length - alphabet: GSM7bit =====")
            test.read_concat_msg(test.r1, test.list_index_cmti_8_bit[5], test.SAVED_MSG_8_BIT_GSM8BIT[2], "GSM")
        else:
            test.expect(False, msg="Message not in memory index")

        test.log.info("***** 12 SMSes saved till now on both modules - CLEANING *****")
        test.delete_sms_from_memory(test.dut)
        test.delete_sms_from_memory(test.r1)
        test.list_index_cmti_8_bit.clear()
        test.list_index_cmti_16_bit.clear()

    def execute_step_7(test):
        test.log.step("Step 7. send concatenated sms that consists of 2 (IEIa 8 bit) and 5 (IEIa 16 bit) segments")
        test.set_dcs_via_csmp(test.dut, "0")
        test.set_dcs_via_csmp(test.r1, "0")
        test.log.info("===== Send 2 part CONCAT SMS IEIA=8 bit and ref_nr 255 =====")
        test.send_concat_msg_directly(2, "8", "255")
        test.log.info("===== Send 5 part CONCAT SMS IEIA=16 bit and ref_nr 65535 =====")
        test.send_concat_msg_directly(5, "16", "65535")

    def execute_step_8(test):
        test.log.step("Step 8. Additional step according to the IPIS100130372 - after set AT^SCMW write command "
                      "without mandatory parameters and AT+CSCA? module should NOT hangs up")

        test.log.step("Step 8.1 Check properly set of AT^SCMW write command and set AT+CSCA? then.")
        test.write_concat_msg(test.SAVED_MSG_STEP_8_1, "123456789", [])
        test.check_sca_values()

        test.log.step("Step 8.2 Negative scenario: set AT^SCMW write command without some mandatory arguments "
                      "and set AT+CSCA? then. Module should NOT hangs up!")
        test.write_concat_msg(test.SAVED_MSG_STEP_8_2, "123456789", [])
        test.check_sca_values()

        test.log.step("Step 8.3 Set some at command to check if module has not hang up.")
        for index in range(1, 4):
            test.expect(test.dut.at1.send_and_verify("AT", ".*OK.*"))


if "__main__" == __name__:
    unicorn.main()