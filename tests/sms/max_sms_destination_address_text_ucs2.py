# responsible: renata.bryla@globallogic.com
# location: Wroclaw
# TC0094929.001

import unicorn
import re
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.character_set import dstl_set_character_set
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.configure_sms_text_mode_parameters import dstl_set_sms_text_mode_parameters
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.read_sms_message import dstl_read_sms_message
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.send_sms_message import dstl_send_sms_message, dstl_send_sms_message_from_memory
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.write_sms_to_memory import dstl_write_sms_to_memory


class Test(BaseTest):
    """ TC0094929.001   MaxSmsDestinationAddressTextUcs2
    Check a module behavior with usage of longer parameter.
    According to E.164 recommendation maximum length is 15 digits plus prefix
    (up to 5 digits e.g. in Finland or one "+" sign instead digital prefix).

    1. Set character set with at+cscs="UCS2" command.
    2. Write to memory message with 20 digits
    i.e. at+cmgw="00310032003300340035003600370038003900300031003200330034003500360037003800390030"
    3. Write to memory message with 15 digits and "+"
    i.e. at+cmgw="002B003100320033003400350036003700380039003000310032003300340035"
    4. Write to memory message with 30 digits
    i.e. at+cmgw="0031003200330034003500360037003800390030003100320033003400350036003700380039
                  00300031003200330034003500360037003800390030"
    5. Read messages written to memory and check if <da> is correct
    6. Send message with 20 digits by at+cmgs command
    i.e. at+cmgs="00310032003300340035003600370038003900300031003200330034003500360037003800390030"
    7. Send message with 15 digits and "+" by at+cmgs command
    i.e. at+cmgs="002B003100320033003400350036003700380039003000310032003300340035"
    8. Send message with 30 digits by at+cmgs command
    i.e. at+cmgs="003100320033003400350036003700380039003000310032003300340035003600370038003900
                  300031003200330034003500360037003800390030"
    9. Send from memory message from point 2 with new 20 digits
    i.e.at+cmss=0,"00310032003300340035003600370038003900300031003200330034003500360037003800390030"
    10. Send from memory message from point 2 with new 15 digits and "+"
    i.e. at+cmss=0,"002B003100320033003400350036003700380039003000310032003300340035"
    11. Send from memory message from point 2 with new 30 digits
    i.e. at+cmss=0,"003100320033003400350036003700380039003000310032003300340035003600370038003900
                    300031003200330034003500360037003800390030"
    12. Send from memory message from point 2 without changing
    i.e. at+cmss=0
    If module support concatenated messages execute below steps for this structure:
    13. Write to storage concatenated message with 20 digit i.e.
    at^scmw="00310032003300340035003600370038003900300031003200330034003500360037003800390030",,,
             1,2,8,255
    at^scmw="00310032003300340035003600370038003900300031003200330034003500360037003800390030",,,
             2,2,8,255
    14. Write to storage concatenated message with 30 digits : i.e.
    at^scmw="003100320033003400350036003700380039003000310032003300340035003600370038003900300031
             003200330034003500360037003800390030",,,1,2,8,255
    at^scmw="003100320033003400350036003700380039003000310032003300340035003600370038003900300031
             003200330034003500360037003800390030",,,2,2,8,255
    15. Read messages written to memory and check if <da> is correct
    16. Send concatenated message with 20 digits : i.e.
    at^scms="00310032003300340035003600370038003900300031003200330034003500360037003800390030",,
             1,2,8,255
    at^scms="00310032003300340035003600370038003900300031003200330034003500360037003800390030",,
             2,2,8,255
    17. Send concatenated message with 30 digits : i.e.
    at^scms="003100320033003400350036003700380039003000310032003300340035003600370038003900300031
             003200330034003500360037003800390030",,1,2,8,255
    at^scms="003100320033003400350036003700380039003000310032003300340035003600370038003900300031
             003200330034003500360037003800390030",,2,2,8,255
    18. Try to send from memory concatenated message from point 13
    i.e. at+cmss=2, at+cmss=3
    """

    TIME_WAIT_IN_SECONDS = 30
    SMS_TIMEOUT = 180
    OK_RESPONSE = ".*OK.*"
    ERROR_RESPONSE = ".*ERROR.*"
    OK_OR_CMS_ERROR_RESPONSE = ".*OK.*|.*CMS ERR.*"
    UCS2_NR_20 = "00310032003300340035003600370038003900300031003200330034003500360037003800390030"
    UCS2_NR_15 = "002B003100320033003400350036003700380039003000310032003300340035"
    UCS2_NR_30 = "0031003200330034003500360037003800390030003100320033003400350036003700380039" \
                 "00300031003200330034003500360037003800390030"
    MSG_FOR_UCS2_20 = "0032003000200064006900670069007400730020006D006500730073006100670065"
    MSG_FOR_UCS2_15 = "0031003500200064006900670069007400730020006D006500730073006100670065"

    def setup(test):
        test.prepare_module_to_test()

    def run(test):
        test.log.info('Start TS for TC: MaxSmsDestinationAddressTextUcs2')
        test.log.step('1. Set character set with at+cscs="UCS2" command.')
        test.expect(dstl_set_character_set(test.dut, 'UCS2'))

        test.log.step('2. Write to memory message with 20 digits \n'
                      f'i.e. at+cmgw="{test.UCS2_NR_20}"')
        cmgw_index_1 = test.expect(dstl_write_sms_to_memory(test.dut, sms_text=test.MSG_FOR_UCS2_20,
                                   sms_format="Text", return_index=True, phone_num=test.UCS2_NR_20))

        test.log.step('3. Write to memory message with 15 digits and "+" \n'
                      f'i.e. at+cmgw="{test.UCS2_NR_15}"')
        cmgw_index_2 = test.expect(dstl_write_sms_to_memory(test.dut, sms_text=test.MSG_FOR_UCS2_15,
                                   sms_format="Text", return_index=True, phone_num=test.UCS2_NR_15))

        test.log.step('4. Write to memory message with 30 digits \n'
                      f'i.e. at+cmgw="{test.UCS2_NR_30}"')
        test.expect(dstl_write_sms_to_memory(test.dut, sms_text="", sms_format="Text",
                    phone_num=test.UCS2_NR_30, exp_resp="CMS ERROR"))

        test.log.step('5. Read messages written to memory and check if <da> is correct')
        test.log.info("Read 1st saved message via CMGR")
        test.expect(dstl_read_sms_message(test.dut, cmgw_index_1[0]))
        test.log.info(f'Expected phrase : .*STO UNSENT.*{test.UCS2_NR_20}.*')
        test.expect(re.search(f'.*STO UNSENT.*{test.UCS2_NR_20}.*', test.dut.at1.last_response))
        test.log.info("Read 2nd saved message via CMGR")
        test.expect(dstl_read_sms_message(test.dut, cmgw_index_2[0]))
        test.log.info(f'Expected phrase : .*STO UNSENT.*{test.UCS2_NR_15}.*')
        test.expect(re.search(f'.*STO UNSENT.*{test.UCS2_NR_15}.*', test.dut.at1.last_response))

        test.log.step('6. Send message with 20 digits by at+cmgs command \n'
                      f'i.e. at+cmgs="{test.UCS2_NR_20}"')
        test.send_sms("CMGS", "", test.UCS2_NR_20, test.MSG_FOR_UCS2_20,
                      test.OK_OR_CMS_ERROR_RESPONSE)
        test.sleep(test.TIME_WAIT_IN_SECONDS)

        test.log.step('7. Send message with 15 digits and "+" by at+cmgs command \n'
                      f'i.e. at+cmgs="{test.UCS2_NR_15}"')
        test.send_sms("CMGS", "", test.UCS2_NR_15, test.MSG_FOR_UCS2_15,
                      test.OK_OR_CMS_ERROR_RESPONSE)
        test.sleep(test.TIME_WAIT_IN_SECONDS)

        test.log.step('8. Send message with 30 digits by at+cmgs command \n'
                      f'i.e. at+cmgs="{test.UCS2_NR_30}"')
        test.send_sms("CMGS", "", test.UCS2_NR_30, "", test.ERROR_RESPONSE)
        test.sleep(test.TIME_WAIT_IN_SECONDS)

        test.log.step('9. Send from memory message from point 2 with new 20 digits \n'
                      f'i.e. at+cmss=0,"{test.UCS2_NR_20}"')
        test.send_sms("CMSS new number", cmgw_index_1[0], test.UCS2_NR_20, test.MSG_FOR_UCS2_20,
                      test.OK_OR_CMS_ERROR_RESPONSE)
        test.sleep(test.TIME_WAIT_IN_SECONDS)

        test.log.step('10. Send from memory message from point 2 with new 15 digits and "+" \n'
                      f'i.e. at+cmss=0,"{test.UCS2_NR_15}"')
        test.send_sms("CMSS new number", cmgw_index_1[0], test.UCS2_NR_15, test.MSG_FOR_UCS2_15,
                      test.OK_OR_CMS_ERROR_RESPONSE)
        test.sleep(test.TIME_WAIT_IN_SECONDS)

        test.log.step('11. Send from memory message from point 2 with new 30 digits \n'
                      f'i.e. at+cmss=0,"{test.UCS2_NR_30}"')
        test.send_sms("CMSS new number", cmgw_index_1[0], test.UCS2_NR_30, "", test.ERROR_RESPONSE)
        test.sleep(test.TIME_WAIT_IN_SECONDS)

        test.log.step('12. Send from memory message from point 2 without changing \n'
                      'i.e. at+cmss=0')
        test.send_sms("CMSS", cmgw_index_1[0], "", "", test.OK_OR_CMS_ERROR_RESPONSE)
        test.sleep(test.TIME_WAIT_IN_SECONDS)

        test.log.step('If module support concatenated messages execute below steps '
                      'for this structure:')
        if test.dut.project.upper() == "SERVAL":
            test.log.info('Concatenated SMS not supported')
            test.log.info('Omitted steps:')
            test.log.info('13. Write to storage concatenated message with 20 digits')
            test.log.info('14. Write to storage concatenated message with 30 digits ')
            test.log.info('15. Read messages written to memory and check if <da> is correct')
            test.log.info('16. Send concatenated message with 20 digits ')
            test.log.info('17. Send concatenated message with 30 digits ')
            test.log.info('Try to send from memory concatenated message from point 13')
        else:
            test.expect(False, msg="At this moment steps for concatenated messages "
                                   "NOT implemented !!!")

    def cleanup(test):
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_set_character_set(test.dut, 'GSM'))

    def prepare_module_to_test(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_bootloader(test.dut)
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_select_sms_message_format(test.dut))
        test.expect(dstl_set_sms_text_mode_parameters(test.dut, "17", "167", "0", "0"))

    def send_sms(test, command, index, number, msg_text, msg_response):
        if msg_response == test.OK_OR_CMS_ERROR_RESPONSE:
            exp_resp = f'.*>.*|{msg_response}'
        else:
            exp_resp = f'{msg_response}'

        if command == "CMSS new number":
            test.expect(dstl_send_sms_message_from_memory(test.dut, index, destination_addr=number,
                                                          exp_resp=exp_resp))
        elif command == "CMSS": 
            test.expect(dstl_send_sms_message_from_memory(test.dut, index, exp_resp=exp_resp))
        else:
            test.expect(dstl_send_sms_message(test.dut, number, sms_text=msg_text,
                                              set_sms_format=False, set_sca=False,
                                              first_expect='.*>.*|{}'.format(msg_response),
                                              exp_resp=msg_response))

        if msg_response == test.OK_OR_CMS_ERROR_RESPONSE:
            msg_accepted = re.search(r".*OK.*", test.dut.at1.last_response)
            if msg_accepted:
                test.log.info("Message is accepted by module, "
                              "but probably rejected by network because of random number")
            else:
                test.expect(not re.search(".*CME ERROR.*", test.dut.at1.last_response))
                test.log.info("Message has been or NOT sent (dependent on the network)")
        else:
            test.expect(not re.search(".*CME ERROR.*", test.dut.at1.last_response))
            test.log.info("Message has NOT been accepted - as expected")


if "__main__" == __name__:
    unicorn.main()