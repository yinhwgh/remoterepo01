#responsible: sebastian.lupkowski@globallogic.com
#location: Wroclaw
#TC0011202.001

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
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory


class Test(BaseTest):
    """
    TC0011202.001    UsingAlphaPDU
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

    a. AT+CMGF=0, AT+CSCS=GSM, coding: 7 bit => write SMS, read SMS
    b. AT+CMGF=1, AT+CSCS=GSM, coding: 7 bit => read SMS
    c. AT+CMGF=0, AT+CSCS=UCS2, coding: 7 bit => read SMS
    d. AT+CMGF=1, AT+CSCS=UCS2, coding: 7 bit => read SMS
    e. AT+CMGF=0, AT+CSCS=GSM, coding: 7 bit => send SMS (cmgs)
    f. AT+CMGF=1, AT+CSCS=GSM => read SMS on remote and compare content

    2) SMS class: no class; Data coding scheme = 8 bit

    a. AT+CMGF=0, AT+CSCS=GSM, coding: 8 bit => write SMS, read SMS
    b. AT+CMGF=1, AT+CSCS=GSM, coding: 8 bit => read SMS
    c. AT+CMGF=0, AT+CSCS=UCS2, coding: 8 bit => read SMS
    d. AT+CMGF=1, AT+CSCS=UCS2, coding: 8 bit => read SMS
    e. AT+CMGF=0, AT+CSCS=GSM, coding: 8 bit => send SMS (cmgs)
    f. AT+CMGF=1, AT+CSCS=GSM => read SMS on remote and compare content

    3) SMS class: no class; Data coding scheme = UCS2

    a. AT+CMGF=0, AT+CSCS=GSM, coding: UCS2 => write SMS, read SMS
    b. AT+CMGF=1, AT+CSCS=GSM, coding: UCS2 => read SMS
    c. AT+CMGF=0, AT+CSCS=UCS2, coding: UCS2 => read SMS
    d. AT+CMGF=1, AT+CSCS=UCS2, coding: UCS2 => read SMS
    e. AT+CMGF=0, AT+CSCS=GSM, coding: UCS2  => send SMS (cmgs)
    f. AT+CMGF=1, AT+CSCS=GSM => read SMS on remote and compare content

    II) Delete all SMSes.

    (Rhea only) III) Send two SMSes to Tln1 - IPIS100062711
    """

    contents7bit = ["0109", "010A", "010D", "0641A1A2312402", "06416143312402",
                    "289B5E083012943614930A958AAC00BDD686B7F16D5E3C1FCBF5FAED4E3AD106B5496D80",
                    "4431D98C56B3DD703958FC5E96D3F3F5F41B1E9E93CD67B47ACDD6E3C776B1BB1DBD16A5D46C35F98406A744E311A95C32"
                    "B5D8A155E86CEE74BC9EEF07"]
    contents8bit = ["01E7", "010A", "010D", "0641420A0D4344", "0641420D0A4344",
                    "207E21402324255E262A28295F2B603D2D5B5D5C3C3E2C2E2F3F3B273A227B7D7C",
                    "443132333435363738393071776572747975696F706173646667686A6B6C7A786376626E6D51574552545955494F504153"
                    "444647484A4B4C5A584356424E4D3B3A3C3D3E3F"]
    contents16bit = ["0200E7", "02000A", "02000D", "0C00410042000A000D00430044", "0C00410042000D000A00430044",
                     "40007E00210040002300240025005E0026002A00280029005F002B0060003D002D005B005D005C003C003E002C002E"
                     "002F003F003B0027003A0022007B007D007C",
                     "88003100320033003400350036003700380039003000710077006500720074007900750069006F0070006100730064006"
                     "600670068006A006B006C007A0078006300760062006E006D00510057004500520054005900550049004F005000410053"
                     "0044004600470048004A004B004C005A0058004300560042004E004D003B003A003C003D003E003F"]
    contents7bit_text = ["09", "0A", "0D", "AB.0A.0DCD", "AB.0D.0ACD",
                         ".*1B=!.00#.02%.1B.14&\\*\\(\\).11\\+.00=-.1B<.1B>.1B.<>,.*\\?;':.22.1B\\(.1B\\).1B@.*",
                         "1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM;:<=>?"]
    substeps = ['1) 0x09    0x00E7    LATIN SMALL LETTER C WITH CEDILLA', '2) 0x0A    0x000A    LINE FEED',
                '3) 0x0D    0x000D    CARRIAGE RETURN', '4) AB[LF][CR]CD', '5) AB[CR][LF]CD',
                '6) All "strange" characters', '7)All Latin capital and small letters and all digits and '
                                               'characters: ;:<=>?']
    pdu_coding = {
        '7 bit': '0000FF',
        '8 bit': '0004FF',
        'UCS2': '0008FF'
    }

    def setup(test):
        test.log.h2("Starting TP for TC0011202.001 - UsingAlphaPDU")
        test.prepare_module(test.dut)
        test.prepare_module(test.r1)

    def run(test):
        test.log.step('I) Write, read and send each above SMSes with following configuration:')
        test.log.step('1) SMS class: no class; Data coding scheme = 7 bit')
        test.execute_substeps(test.contents7bit, '7 bit')

        test.log.step('2) SMS class: no class; Data coding scheme = 8 bit')
        test.execute_substeps(test.contents8bit, '8 bit')

        test.log.step('3) SMS class: no class; Data coding scheme = UCS2')
        test.execute_substeps(test.contents16bit, 'UCS2')

    def cleanup(test):
        test.log.step('II) Delete all SMSes.')
        dstl_delete_all_sms_messages(test.dut)
        dstl_delete_all_sms_messages(test.r1)

    def prepare_module(test, module):
        dstl_detect(module)
        test.expect(dstl_get_imei(module))
        test.expect(dstl_get_bootloader(module))
        test.expect(dstl_register_to_network(module))
        test.expect(module.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
        test.expect(module.at1.send_and_verify('AT+CNMI=2,1', '.*OK.*'))
        test.expect(dstl_set_scfg_urc_dst_ifc(module))
        test.expect(dstl_set_preferred_sms_memory(module, 'ME'))
        dstl_delete_all_sms_messages(module)

    def get_pdu_length(test, pdu):
        if len(pdu) > 43:  # minimal length of correct PDU payload
            return (len(pdu) - ((int(pdu[1]) + 1) * 2)) // 2
        else:  # in case of invalid PDU payload
            return 0

    def write_pdu_message(test, pdu):
        test.expect(test.dut.at1.send_and_verify('AT+CMGW={}'.format(test.get_pdu_length(pdu)), '.*>.*',
                                                 wait_for='.*>.*'))
        if test.expect(test.dut.at1.send_and_verify(pdu, end="\u001A", expect='.*OK.*')):
            return int(re.search(r'(\+CMGW: )(\d{1,3})', test.dut.at1.last_response).group(2))
        else:
            return -1

    def send_sms_from_dut(test, pdu):
        if test.expect(test.dut.at1.send_and_verify('AT+CMGS={}'.format(test.get_pdu_length(pdu)), '.*>.*',
                                                    wait_for='.*>.*')):
            test.expect(test.dut.at1.send_and_verify(pdu, end="\u001A", expect='.*OK.*'))

    def get_cmti_index(test):
        test.log.info("Waiting up to 360 seconds for CMTI URC")
        if test.expect(dstl_check_urc(test.r1, ".*CMTI.*", timeout=360)):
            return int(re.search(r'(\+CMTI: \".*\",\s*)(.*)', test.r1.at1.last_response).group(2))
        else:
            return -1

    def execute_substeps(test, contents, coding):
        for content in contents:
            message = '{}1100{}{}{}'.format(test.dut.sim.sca_pdu, test.r1.sim.pdu, test.pdu_coding[coding], content)

            test.log.info('=== EXECUTING: {} ==='.format(test.substeps[contents.index(content)]))
            test.log.step('a. AT+CMGF=0, AT+CSCS=GSM, coding: {} => write SMS, read SMS'.format(coding))
            test.expect(dstl_select_sms_message_format(test.dut, 'PDU'))
            test.expect(test.dut.at1.send_and_verify('AT+CSCS="GSM"', '.*OK.*'))
            msg_index = test.write_pdu_message(message)

            if msg_index > -1:
                test.expect(test.dut.at1.send_and_verify('AT+CMGR={}'.format(msg_index), message))
                test.log.step('b. AT+CMGF=1, AT+CSCS=GSM, coding: {} => read SMS'.format(coding))
                test.expect(dstl_select_sms_message_format(test.dut, 'Text'))
                test.expect(test.dut.at1.send_and_verify('AT+CSCS?', '.*GSM.*'))
                test.expect(dstl_read_sms_message(test.dut, msg_index))
                if coding == '7 bit':
                    test.expect(re.search(r".*{}.*".format(test.contents7bit_text[contents.index(content)]),
                                          test.dut.at1.last_response))
                else:
                    test.expect(re.search(r".*{}.*".format(content[2:]), test.dut.at1.last_response))

                test.log.step('c. AT+CMGF=0, AT+CSCS=UCS2, coding: {} => read SMS'.format(coding))
                test.expect(dstl_select_sms_message_format(test.dut, 'PDU'))
                test.expect(test.dut.at1.send_and_verify('AT+CSCS="UCS2"', '.*OK.*'))
                test.expect(dstl_read_sms_message(test.dut, msg_index))
                test.expect(re.search(r".*{}.*".format(content), test.dut.at1.last_response))

                test.log.step('d. AT+CMGF=1, AT+CSCS=UCS2, coding: {} => read SMS'.format(coding))
                test.expect(dstl_select_sms_message_format(test.dut, 'Text'))
                test.expect(test.dut.at1.send_and_verify('AT+CSCS?', '.*UCS2.*'))
                test.expect(dstl_read_sms_message(test.dut, msg_index))
                if contents.index(content) == 5:
                    regex = test.contents16bit[5][2:56] + '.' + test.contents16bit[5][57:]
                else:
                    regex = test.contents16bit[contents.index(content)][2:]
                test.expect(re.search(r".*{}.*".format(regex), test.dut.at1.last_response))

                test.log.step('e. AT+CMGF=0, AT+CSCS=GSM, coding: {} => send SMS (cmgs)'.format(coding))
                test.expect(dstl_select_sms_message_format(test.dut, 'PDU'))
                test.expect(test.dut.at1.send_and_verify('AT+CSCS="GSM"', '.*OK.*'))
                test.send_sms_from_dut(message)

                test.log.step('f. AT+CMGF=1, AT+CSCS=GSM => read SMS on remote and compare content')
                rem_msg_index = test.get_cmti_index()
                if rem_msg_index > -1:
                    test.expect(dstl_select_sms_message_format(test.r1, 'Text'))
                    test.expect(test.r1.at1.send_and_verify('AT+CSCS="GSM"', '.*OK.*'))
                    test.expect(dstl_read_sms_message(test.r1, rem_msg_index))
                    if coding == '7 bit':
                        test.expect(re.search(r".*{}.*".format(test.contents7bit_text[contents.index(content)]),
                                              test.r1.at1.last_response))
                    else:
                        test.expect(re.search(r".*{}.*".format(content[2:]), test.r1.at1.last_response))
                else:
                    test.expect(False, msg="No CMTI URC found")


if "__main__" == __name__:
    unicorn.main()
