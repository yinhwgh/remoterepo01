#responsible: sebastian.lupkowski@globallogic.com, renata.bryla@globallogic.com
#location: Wroclaw
#TC0011140.001

import unicorn
import re
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.read_sms_message import dstl_read_sms_message
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.send_sms_message import dstl_send_sms_message_from_memory
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory


class Test(BaseTest):
    """
    SMS that should be sent:
    1) 0x09    0x00E7    LATIN SMALL LETTER C WITH CEDILLA
    2) 0x0A    0x000A    LINE FEED
    3) 0x0D    0x000D    CARRIAGE RETURN
    4) AB[LF][CR]CD
    5) AB[CR][LF]CD
    6) All "strange" characters
    7) All Latin capital and small letters and all digits and characters: ;:<=>?

    I) Write, read and send each above SMSes with following configuration:

    1) SMS class: no class; Data coding scheme = 7 bit

    a. AT+CSCS=GSM, coding: 7 bit => write SMS, read SMS
    b. AT+CSCS=UCS2, coding: 7 bit => read SMS
    c. AT+CSCS=GSM, coding: 7 bit => send SMS (cmgs)
    d. AT+CSCS=GSM => read SMS on remote and compare content

    2) SMS class: no class; Data coding scheme = 8 bit

    a. AT+CSCS=GSM, coding: 8 bit => write SMS, read SMS
    b. AT+CSCS=UCS2, coding: 8 bit => read SMS
    c. AT+CSCS=GSM, coding: 8 bit => send SMS (cmgs)
    d. AT+CSCS=GSM => read SMS on remote and compare content

    3) SMS class: no class; Data coding scheme = UCS2

    a. AT+CSCS=GSM, coding: UCS2 => write SMS, read SMS
    b. AT+CSCS=UCS2, coding: UCS2 => read SMS
    c. AT+CSCS=GSM, coding: UCS2  => send SMS (cmgs)
    d. AT+CSCS=GSM => read SMS on remote and compare content

    II) Delete all SMSes.

    III) Check length of the message in 16-bit coding (based on IPIS100330284)
    1) Set <dcs> 16bit for SMS class 0 : AT+CSMP=17,167,0,24
    2) Set character set GSM: AT+CSCS="GSM"
    3) Write message to memory with own number: AT+CMGW="own_number"
    4) Read message: AT+CMGR=<index> and check length
    5) Send message from memory: AT+CMSS=<index>, wait for CMT message and check length
    6) Set character set UCS2: AT+CSCS="UCS2"
    7) Send message from memory: AT+CMSS=<index>, wait for CMT message and check length
    8) Set PDU format: AT+CMGF=0
    9) Send message from memory: AT+CMSS=<index>, wait for CMT message and check length
    10) Set character set GSM: AT+CSCS="GSM"
    11) Send message from memory: AT+CMSS=<index>, wait for CMT message and check length
    12) Read message: AT+CMGR=<index> and check length

    IV) Delete all SMSes.
    """

    contents7bit = ["\u0009", "\u000A", "\u000D", "\u0041\u0042\u000A\u000D\u0043\u0044",
                    "\u0041\u0042\u000D\u000A\u0043\u0044",
                    "~!@#$%^&*()_+@=-[]\<>,./?;':\"{}|",
                    "1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM;:<=>?"]
    contents8bit = ["E7", "0A", "0D", "41420A0D4344", "41420D0A4344",
                    "7E21402324255E262A28295F2B603D2D5B5D5C3C3E2C2E2F3F3B273A227B7D7C",
                    "3132333435363738393071776572747975696F706173646667686A6B6C7A786376626E6D51574552545955494F504153"
                    "444647484A4B4C5A584356424E4D3B3A3C3D3E3F"]
    contents16bit = ["00E7", "000A", "000D", "00410042000A000D00430044", "00410042000D000A00430044",
                     "007E00210040002300240025005E0026002A00280029005F002B0060003D002D005B005D005C003C003E002C002E"
                     "002F003F003B0027003A0022007B007D007C",
                     "003100320033003400350036003700380039003000710077006500720074007900750069006F0070006100730064006"
                     "600670068006A006B006C007A0078006300760062006E006D00510057004500520054005900550049004F005000410053"
                     "0044004600470048004A004B004C005A0058004300560042004E004D003B003A003C003D003E003F"]
    content_7bit_in_ucs2 = "00FC002100A1002300A4002500DC0026002A0028002900A7002B00A1003D002D00C400D100D6003C003E002C" \
                           "002E002F003F003B0027003A002200E400F100F6"
    contents7bit_text = ["09", "0A", "0D", "AB.0A.0DCD", "AB.0D.0ACD",
                         "~!@#\$%\^&\*\(\)_\+@=-\[\].5C<>,\.\/\?;':.22\{\}\|",
                         "1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM;:<=>\?"]
    substeps = ['1) 0x09    0x00E7    LATIN SMALL LETTER C WITH CEDILLA', '2) 0x0A    0x000A    LINE FEED',
                '3) 0x0D    0x000D    CARRIAGE RETURN', '4) AB[LF][CR]CD', '5) AB[CR][LF]CD',
                '6) All "strange" characters', '7)All Latin capital and small letters and all digits and '
                                               'characters: ;:<=>?']
    timeout = 120
    receive_timeout = 360

    def setup(test):
        test.log.h2("Starting TP for TC0011140.001 - UsingAlphaText")
        test.prepare_module(test.dut)
        test.prepare_module(test.r1)

    def run(test):
        test.log.step('I) Write, read and send each above SMSes with following configuration:')
        test.log.step('1) SMS class: no class; Data coding scheme = 7 bit')
        test.set_csmp('0')
        test.execute_substeps(test.contents7bit, '7 bit')

        test.log.step('2) SMS class: no class; Data coding scheme = 8 bit')
        test.set_csmp('4')
        test.execute_substeps(test.contents8bit, '8 bit')

        test.log.step('3) SMS class: no class; Data coding scheme = UCS2')
        test.set_csmp('8')
        test.execute_substeps(test.contents16bit, 'UCS2')

        test.log.step('II) Delete all SMSes.')
        dstl_delete_all_sms_messages(test.dut)
        dstl_delete_all_sms_messages(test.r1)

        test.log.step('III) Check length of the message in 16-bit coding (based on IPIS100330284)')
        test.expect(test.dut.at1.send_and_verify('AT+CSDH=1', '.*OK.*'))

        test.log.step('1) Set <dcs> 16bit for SMS class 0 : AT+CSMP=17,167,0,24')
        test.set_csmp('24', False)

        test.log.step('2) Set character set GSM: AT+CSCS="GSM"')
        test.expect(test.dut.at1.send_and_verify('AT+CSCS="GSM"', '.*OK.*'))

        test.log.step('3) Write message to memory with own number: AT+CMGW="own_number"')
        msg_index = test.write_text_message('003100320033', False)

        if test.expect(msg_index != -1):
            test.log.step('4) Read message: AT+CMGR=<index> and check length')
            test.expect(dstl_read_sms_message(test.dut, msg_index))
            test.expect(re.search(r'.*145,3\s*[\n\r]003100320033\s*[\n\r].*', test.dut.at1.last_response))

            test.log.step('5) Send message from memory: AT+CMSS=<index>, wait for CMT message and check length')
            test.expect(dstl_send_sms_message_from_memory(test.dut, msg_index))
            test.expect(dstl_check_urc(test.dut, 'CMT:.*145,3.*003100320033.*', timeout=test.timeout))

            test.log.step('6) Set character set UCS2: AT+CSCS="UCS2"')
            test.expect(test.dut.at1.send_and_verify('AT+CSCS="UCS2"', '.*OK.*'))

            test.log.step('7) Send message from memory: AT+CMSS=<index>, wait for CMT message and check length')
            test.expect(dstl_send_sms_message_from_memory(test.dut, msg_index))
            test.expect(dstl_check_urc(test.dut, 'CMT:.*145,3.*003100320033.*', timeout=test.timeout))

            test.log.step('8) Set PDU format: AT+CMGF=0')
            test.expect(dstl_select_sms_message_format(test.dut, 'PDU'))

            test.log.step('9) Send message from memory: AT+CMSS=<index>, wait for CMT message and check length')
            test.expect(dstl_send_sms_message_from_memory(test.dut, msg_index))
            test.expect(dstl_check_urc(test.dut, 'CMT:.*06003100320033.*', timeout=test.timeout))

            test.log.step('10) Set character set GSM: AT+CSCS="GSM"')
            test.expect(test.dut.at1.send_and_verify('AT+CSCS="GSM"', '.*OK.*'))

            test.log.step('11) Send message from memory: AT+CMSS=<index>, wait for CMT message and check length')
            test.expect(dstl_send_sms_message_from_memory(test.dut, msg_index))
            test.expect(dstl_check_urc(test.dut, 'CMT:.*06003100320033.*', timeout=test.timeout))

            test.log.step('12) Read message: AT+CMGR=<index> and check length')
            test.expect(dstl_read_sms_message(test.dut, msg_index))
            test.expect(re.search(r'.*CMGR:.*[\r\n].*06003100320033.*', test.dut.at1.last_response))

        else:
            test.log.error("Message not saved")

    def cleanup(test):
        test.log.step('IV) Delete all SMSes.')
        dstl_delete_all_sms_messages(test.dut)
        dstl_delete_all_sms_messages(test.r1)
        test.restore_settings(test.dut)
        test.restore_settings(test.r1)

    def prepare_module(test, module):
        dstl_detect(module)
        dstl_get_imei(module)
        dstl_get_bootloader(module)
        test.expect(dstl_register_to_network(module))
        test.expect(module.at1.send_and_verify('AT+CMEE=2', '.*OK.*'))
        test.expect(dstl_select_sms_message_format(module))
        test.expect(module.at1.send_and_verify('AT+CNMI=2,1', '.*OK.*'))
        test.expect(dstl_set_scfg_urc_dst_ifc(module))
        test.expect(dstl_set_preferred_sms_memory(module, 'ME'))
        test.expect(dstl_delete_all_sms_messages(module))

    def restore_settings(test, module):
        test.log.info('Restore settings')
        test.expect(module.at1.send_and_verify('AT+CSMP=17,167,0,0', '.*OK.*'))
        test.expect(module.at1.send_and_verify('AT&F', '.*OK.*'))
        test.expect(module.at1.send_and_verify('AT&W', '.*OK.*'))

    def write_text_message(test, text, remote=True):
        if remote:
            number = test.r1.sim.int_voice_nr
        else:
            number = test.dut.sim.int_voice_nr
        test.expect(test.dut.at1.send_and_verify('AT+CMGW="{}"'.format(number), '.*>.*',
                                                 wait_for='.*>.*'))
        if test.expect(test.dut.at1.send_and_verify(text, end="\u001A", expect='.*OK.*')):
            return int(re.search(r'(\+CMGW: )(\d{1,3})', test.dut.at1.last_response).group(2))
        else:
            return -1

    def send_sms_from_dut(test, text):
        if test.expect(test.dut.at1.send_and_verify('AT+CMGS="{}"'.format(test.r1.sim.int_voice_nr), '.*>.*',
                                                    wait_for='.*>.*')):
            test.expect(test.dut.at1.send_and_verify(text, end="\u001A", expect='.*OK.*', wait_for='.*OK.*',
                                                     timeout=test.timeout))

    def get_cmti_index(test):
        test.log.info("Waiting up to 360 seconds for CMTI URC")
        if test.expect(dstl_check_urc(test.r1, ".*CMTI.*", timeout=test.receive_timeout)):
            return int(re.search(r'(\+CMTI: \".*\",\s*)(.*)', test.r1.at1.last_response).group(2))
        else:
            return -1

    def set_csmp(test, dcs, remote=True):
        test.expect(test.dut.at1.send_and_verify("AT+CSMP=17,167,0,{}".format(dcs), ".*OK.*"))
        if remote:
            test.expect(test.r1.at1.send_and_verify("AT+CSMP=17,167,0,{}".format(dcs), ".*OK.*"))

    def execute_substeps(test, contents, coding):
        for content in contents:

            test.log.info('=== EXECUTING: {} ==='.format(test.substeps[contents.index(content)]))
            test.log.step('a. AT+CSCS=GSM, coding: {} => write SMS, read SMS'.format(coding))
            test.expect(test.dut.at1.send_and_verify('AT+CSCS="GSM"', '.*OK.*'))
            msg_index = test.write_text_message(content)

            if msg_index > -1:
                test.expect(dstl_read_sms_message(test.dut, msg_index))
                if coding == '7 bit':
                    test.expect(re.search(r".*{}[\r\n]+".format(test.contents7bit_text[contents.index(content)]),
                                          test.dut.at1.last_response))
                    test.log.info("Expected result: {}".format(test.contents7bit_text[contents.index(content)]))
                else:
                    test.expect(re.search(r".*{}[\r\n]+".format(content), test.dut.at1.last_response))
                    test.log.info("Expected result: {}".format(content))

                test.log.step('b. AT+CSCS=UCS2, coding: {} => read SMS'.format(coding))
                test.expect(test.dut.at1.send_and_verify('AT+CSCS="UCS2"', '.*OK.*'))
                test.expect(dstl_read_sms_message(test.dut, msg_index))
                if contents.index(content) == 5 and coding == '7 bit':
                    # according to AT-Spec in text mode it's not possible to use escape sequences, so special characters
                    # are coded using PC's coding scheme and this exception is needed
                    test.expect(re.search(r".*{}[\r\n]+".format(test.content_7bit_in_ucs2),
                                          test.dut.at1.last_response))
                    test.log.info("Expected result: {}".format(test.content_7bit_in_ucs2))
                else:
                    test.expect(re.search(r".*{}[\r\n]+".format(test.contents16bit[contents.index(content)]),
                                      test.dut.at1.last_response))
                    test.log.info("Expected result: {}".format(test.contents16bit[contents.index(content)]))

                test.log.step('c. AT+CSCS=GSM, coding: {} => send SMS (cmgs)'.format(coding))
                test.expect(test.dut.at1.send_and_verify('AT+CSCS="GSM"', '.*OK.*'))
                test.send_sms_from_dut(content)

                test.log.step('d. AT+CSCS=GSM => read SMS on remote and compare content')
                rem_msg_index = test.get_cmti_index()
                if rem_msg_index > -1:
                    test.expect(test.r1.at1.send_and_verify('AT+CSCS="GSM"', '.*OK.*'))
                    test.expect(dstl_read_sms_message(test.r1, rem_msg_index))
                    if coding == '7 bit':
                        test.expect(re.search(r".*{}[\r\n]+".format(test.contents7bit_text[contents.index(content)]),
                                              test.r1.at1.last_response))
                        test.log.info("Expected result: {}".format(test.contents7bit_text[contents.index(content)]))
                    else:
                        test.expect(re.search(r".*{}[\r\n]+".format(content), test.r1.at1.last_response))
                        test.log.info("Expected result: {}".format(content))
                else:
                    test.expect(False, msg="No CMTI URC found")


if "__main__" == __name__:
    unicorn.main()