# responsible: renata.bryla@globallogic.com
# location: Wroclaw
# TC0085070.001

import unicorn
import re

from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.character_set import dstl_set_character_set
from dstl.configuration.reset_to_factory_default_state import \
    dstl_reset_settings_to_factory_default_values
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.configuration.store_user_defined_profile import dstl_store_user_defined_profile
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.identification.get_imei import dstl_get_imei
from dstl.sms.configure_sms_text_mode_parameters import dstl_configure_sms_event_reporting
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.read_sms_message import dstl_read_sms_message
from dstl.sms.select_message_service import dstl_set_message_service
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.send_sms_message import dstl_send_sms_message_from_memory
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.write_sms_to_memory import dstl_write_sms_to_memory


class Test(BaseTest):
    """
    TC0085070.001    TpNationalLanguageIdentifier
    TC checks, if it is possible to write to memory a SMS using national language tables
    and read them from mem in PDU mode.

    Checking of Locking Shift mechanism:
    1. Write to mem a SMS containing one Turkish letter (0001011)
       using the mechanism of National Language Locking Shift Table of Turkish language
    2. Mixed letters, signs and numbers from Turkish National Language Locking Shift Table
       40 50(P) 60 70(p) 04 14 24 34(4) 2B(+).
    3. All Turkish specific letters from Locking Shift Table
       (40, 60, 04, 07, 0B, 0C, 1C, 1D)
    Checking of Single Shift mechanism:
    4. All Turkish letters from Turkish National Language Single Shift Table
       (53, 63, 73, 47, 67, 49, 69, 65)
    Checking of both Single Shift and Locking Shift mechanism:
    5. Mixed - Turkish letters from Locking Shift Table and Single Shift Table one from Locking,
       escape to Single, char from Single and next from Locking.
       In this case UserDataHeader is 7 bytes (56 bits) long: 06250101240101.
       It means that it fills all bits till septet boundary - no additional fill bits needed!
    Checking of Single Shift mechanism combined with chars from GSM 7 bit Default Alphabet:
    6. Chars from GSM 7 bit Default Alphabet (the same mechanism as in previous SMS,
       but instead of Locking National Table the Default 7 bit Table should be used)
       and Turkish National Language Single Shift Table after every <escape> char.
       In this case UserDataHeader is 4 bytes (32 bits) long: 03240101
    Checking of Locking Shift mechanism combined with chars from GSM 7 bit Default Extension Table:
    7. Turkish chars from Locking Shift Table and GSM 7 bit Default Extension Table
       after every <escape> char (the same as mechanism as in previous SMS, but instead of
       Single Shift National Table / the GSM 7 bit Default Extension Table should be used).
       In this case UserDataHeader is 4 bytes (32 bits) long: 03250101
    - case with only escape char without following char
    - case with 3 escape chars one after another
    8. Case with more that one LangIE in one SMS(last one used)
    9. SMS with a LangIE and empty text part and maximum text part
    10. SMS with a LangIE not yet defined
    11. SMS with LandIE and UCS coded (IE should be ignored)
    12. Sending of A letter with- and without SMS status report request
    """

    SMS_TIMEOUT = 180

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_set_scfg_urc_dst_ifc(test.dut)
        test.expect(dstl_register_to_network(test.dut), critical=True)
        test.expect(dstl_set_error_message_format(test.dut))
        test.expect(dstl_set_character_set(test.dut, character_set='GSM'))
        test.expect(dstl_set_message_service(test.dut))
        test.expect(dstl_configure_sms_event_reporting(test.dut, mode='2', mt='1'))
        test.expect(dstl_set_sms_center_address(test.dut, test.dut.sim.sca_int))
        test.expect(dstl_select_sms_message_format(test.dut, sms_format='PDU'))
        test.expect(dstl_set_preferred_sms_memory(test.dut, preferred_storage='ME'))
        test.expect(dstl_delete_all_sms_messages(test.dut))

    def run(test):
        test.log.step("Checking of Locking Shift mechanism:")
        test.log.step("1. Write to mem a SMS containing one Turkish letter (0001011) \nusing the "
                      "mechanism of National Language Locking Shift Table of Turkish language")
        test.write_read_send_sms("06032501015800")
        test.log.info("===== Check also Portuguese letter 0001011 (0x0B) =====")
        test.write_read_send_sms("06032501035800")

        test.log.step("2. Mixed letters, signs and numbers from Turkish National Language "
                      "Locking Shift Table \n40 50(P) 60 70(p) 04 14 24 34(4) 2B(+).")
        test.write_read_send_sms("0E032501010042C1700285445B01")

        test.log.step("3. All Turkish specific letters from Locking Shift Table \n"
                      "(40, 60, 04, 07, 0B, 0C, 1C, 1D)")
        test.write_read_send_sms("0D03250101008209870583D301")

        test.log.step("Checking of Single Shift mechanism:")
        test.log.step("4. All Turkish letters from Turkish National Language Single Shift Table \n"
                      "(53, 63, 73, 47, 67, 49, 69, 65)")
        test.write_read_send_sms("1503240101D84C37E3CD7C73DC9C37C94D7A5306")

        test.log.step("Checking of both Single Shift and Locking Shift mechanism:")
        test.log.step("5. Mixed - Turkish letters from Locking Shift Table and Single Shift Table\n"
                      "one from Locking, escape to Single, char from Single and next from Locking\n"
                      "In this case UserDataHeader is 7 bytes (56 bits) long: 06250101240101.\n"
                      "It means that it fills all bits till septet boundary - "
                      "no additional fill bits needed!")
        test.write_read_send_sms("2006250101240101C0CD14BC191336F3C3E6B8D89C199B246793EE6CCA")

        test.log.step("6. Chars from GSM 7 bit Default Alphabet (the same mechanism as in previous "
                      "SMS,\nbut instead of Locking National Table the Default 7 bit "
                      "Table should be used)\nand Turkish National Language Single Shift Table "
                      "after every <escape> char.\n"
                      "In this case UserDataHeader is 4 bytes (32 bits) long: 03240101")
        test.write_read_send_sms("1D03240101006EA6E0CD98B0991F36C7C5E6CCD824399B74675306")
        test.log.info("===== Check also Chars from GSM 7 bit Default Alphabet\n"
                      "and Spanish National Language Single Shift Table after every <escape> char\n"
                      "In this case UserDataHeader is 4 bytes (32 bits) long: 03240102=====")
        test.write_read_send_sms("1D03250102006E82E04D98B0A91E36F5C526C9D8A4399B6767F306")

        test.log.step("Checking of Locking Shift mechanism combined with chars from GSM 7 bit "
                      "Default Extension Table:")
        test.log.step("7. Turkish chars from Locking Shift Table and GSM 7 bit "
                      "Default Extension Table after every <escape> char\n"
                      "(the same as mechanism as in previous SMS, but instead of Single Shift "
                      "National Table the GSM 7 bit Default Extension Table should be used).\n"
                      "In this case UserDataHeader is 4 bytes (32 bits) long: 03250101\n"
                      "- case with only escape char without following char\n"
                      "- case with 3 escape chars one after another")
        test.write_read_send_sms("1D03250101006EA6E0CD98B0991F36C7C5E6CCD824399B74675306")
        test.log.info("===== - case with 3 escape chars one after another =====")
        test.write_read_send_sms("1503240101D84C37E3CD7C73DC9C379B4D7A5306")
        test.log.info("===== escape without following char =====")
        test.write_read_send_sms("0A03240101D84C37E30D")

        test.log.step("8. Case with more that one LangIE in one SMS(last one used)")
        test.log.info("===== Mixed - Turkish letters from Locking Shift Table and "
                      "Spanish from Single Shift Table\n "
                      "one from Locking, escape to Single, char from Single and next from Locking\n"
                      "In this case UserDataHeader is 7 bytes (56 bits) long: 06250101240102.\n"
                      "It means that it fills all bits till septet boundary "
                      "- no additional fill bits needed!")
        test.write_read_send_sms("2006250101240102C04D10BC091336D5C3A6BED824199B346743E96C12")

        test.log.step("9. SMS with a LangIE and empty text part and maximum text part")
        test.log.info("===== SMS with a LangIE and empty text part =====")
        test.write_read_send_sms("050325010100")
        test.log.info("===== SMS with a LangIE and maximum text part =====")
        test.write_read_send_sms("A003250101F8FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"
                                 "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"
                                 "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"
                                 "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"
                                 "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF01")

        test.log.step("10. SMS with a LangIE not yet defined")
        test.log.info("===== SMS with a LangIE not yet defined : 00000100 - 04 =====")
        test.write_read_send_sms("06032501040802")

        test.log.step("11. SMS with LandIE and UCS coded (IE should be ignored)")
        test.log.info("===== A letter sent = UCS: 0041 =====")
        test.write_read_send_sms("06032501010041", is_ucs2=True)

        test.log.step("12. Sending of A letter with- and without SMS status report request")
        test.log.info("===== sending of A letter without SMS status report request =====")
        test.write_read_send_sms("06032501010802")
        test.log.info("===== sending of A letter with SMS status report request =====")
        test.expect(dstl_configure_sms_event_reporting(
            test.dut, mode='2', mt='1', bm="0", ds="1", bfr="1"))
        test.write_read_send_sms("06032501010802", is_status_report=True)

    def cleanup(test):
        test.expect(dstl_reset_settings_to_factory_default_values(test.dut))
        test.expect(dstl_store_user_defined_profile(test.dut))

    def prepare_pdu(test, msg_content, ucs2=False, status_report=False):
        dcs = "08" if ucs2 else "00"
        sr = "71" if status_report else "51"
        return f"{test.dut.sim.sca_pdu}{sr}00{test.dut.sim.pdu}00{dcs}00{msg_content}"

    def write_read_send_sms(test, msg_content_pdu, is_ucs2=False, is_status_report=False):
        pdu_msg = test.prepare_pdu(msg_content_pdu, ucs2=is_ucs2, status_report=is_status_report)

        cmgw = dstl_write_sms_to_memory(test.dut, return_index=True, sms_format="PDU", pdu=pdu_msg)
        if test.expect(cmgw is not None):
            test.verify_sms(cmgw[0], pdu_msg)
            test.expect(dstl_send_sms_message_from_memory(test.dut, cmgw[0]))
            if test.expect(dstl_check_urc(test.dut, ".*CMTI.*", timeout=test.SMS_TIMEOUT)):
                cmti = re.search(r".*CMTI.*,\s*(\d{1,3})", test.dut.at1.last_response)
                if is_status_report:
                    test.expect(dstl_check_urc(test.dut, ".*CDS: .*", timeout=test.SMS_TIMEOUT))
                if test.expect(cmti is not None):
                    test.verify_sms(cmti[1], msg_content_pdu)
                else:
                    test.log.error("Fail to get value of CMTI")
            else:
                test.log.info("Message NOT delivered")
            test.expect(dstl_delete_all_sms_messages(test.dut))

    def verify_sms(test, index, regex_pdu):
        test.expect(dstl_read_sms_message(test.dut, index))
        test.log.info(f"Expected REGEX: .*{regex_pdu}.*")
        exp_regex = re.search(f".*{regex_pdu}.*", test.dut.at1.last_response)
        test.expect(exp_regex is not None)
        test.expect(dstl_select_sms_message_format(test.dut, sms_format='Text'))
        test.expect(dstl_read_sms_message(test.dut, index))
        test.expect(dstl_select_sms_message_format(test.dut, sms_format='PDU'))


if "__main__" == __name__:
    unicorn.main()
