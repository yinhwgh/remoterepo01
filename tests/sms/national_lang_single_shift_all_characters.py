#responsible: dariusz.drozdek@globallogic.com
#location: Wroclaw
#TC0104302.001

import re
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory


class Test(BaseTest):
    """responsible: Dariusz Drozdek, dariusz.drozdek@globallogic.com location: Wroclaw

    TC0104302.001    NationalLangSingleShiftAllCharacters

    Check support of PDU messages using National Single Shift Tables and all defined characters as defined by 3GPP
    TS 23.038 V8.2.0 (3GPP Release 8 - Turkish, Spanish and Portuguese).

    "1. Save with at+cmgw PDU message configured for using Single Shift Character Set for Turkish
        language and containing all defined characters from 7-bit GSM Single Shift Character Set
    2. Read it and send it from memory with at+cmss to itself,
    3. Send message directly with at+cmgs to itself,
    4. Read incoming messages and verify correct content in PDU mode,
    5. Read messages in text mode,
    6. Repeat steps 1-5 also for Spanish and Portuguese Single Shift Character Sets"
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        test.log.info("Prepare module for sending SMS")
        test.expect(dstl_register_to_network(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT+CSCS=\"GSM\"", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSMS=1", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSCA=\"{}\"".format(test.dut.sim.sca_int), ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSDH=1", ".*OK.*"))
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
        test.expect(dstl_delete_all_sms_messages(test.dut))

    def run(test):
        language = ["Turkish", "Spanish", "Portuguese"]
        national_lang_characters = ["0000A72503250101D80037D3CD7833DF5036E5CD7173DEA036A94D7293DEF036BD8D6FF302",
                                    "0000A72903250102D80037C14D7843D95437E54D7D83DA2436A94D7293DEF036BD8D6FF3DA3C376F",
                                    "0000A74D03250103D80037C14D7823D94C36944D6153D95437E54D7D63D95C36980D6A93D86436A94D"
                                    "7293DE2C36DBCD7EC3D8F036DC0D7FD3DB3836BECD63F3D9BC36CFCD7BF307"]
        regex_content = [r"1B@.1BS.1Bc.1Bs.1B.14.1Be.1BG.1Bg.1B\(.1B\).1BI.1Bi.1B<.1B=.1B>.1B/",
                         r"1B@.1BA.1Ba.1B.14.1BU.1Be.1Bu.1B\(.1B.09.1B\).1BI.1Bi.1B<.1B=.1B>.1B/.1BO.1Bo",
                         r"1B@.1BA.1Ba.1B.12.1B.13.1B.14.1B.05.1B.15.1BU.1Be.1Bu.1B.16.1B.17.1B.18.1B\(.1B.09.1B."
                         r"19.1B\).1BI.1Bi.1B.0B.1B\[.1B\{.1B.0C.1B\<.1B.5C.1B\|.1B=.1B.0E.1B\>.1B.0F.1B.1F.1B/."
                         r"1BO.1Bo.1B"]

        for i, lang in enumerate(national_lang_characters, 0):
            test.log.step("1. Save with at+cmgw PDU message configured for using Single Shift Character Set for {} "
                          "language and containing all defined characters from 7-bit GSM Single Shift Character"
                          " Set".format(language[i]))
            test.expect(dstl_select_sms_message_format(test.dut, "PDU"))
            message_pdu = "{}5100{}{}".format(test.dut.sim.sca_pdu, test.dut.sim.pdu, lang)
            test.sms_command("write", test.pdu_length(message_pdu), message_pdu)

            test.log.step("2. Read it and send it from memory with at+cmss to itself")
            sms_index = re.findall(r" \d{1,3}", test.dut.at1.last_response)
            test.expect(test.dut.at1.send_and_verify("AT+CMGR={}".format(sms_index[0].strip()), ".*OK.*"))
            test.expect(re.search(".*{}.*{}.*".format(test.dut.sim.sca_pdu[:4], lang[52:]), test.dut.at1.last_response))
            test.sleep(1)
            test.expect(test.dut.at1.send_and_verify("AT+CMSS={}".format(sms_index[0].strip()), ".*CMSS.*OK.*"))
            test.expect(test.dut.at1.wait_for(".*CMTI.*"))
            sms_index = re.findall(r"\d{1,3}", test.dut.at1.last_response)

            test.log.step("3. Send message directly with at+cmgs to itself,")
            test.sms_command("send", test.pdu_length(message_pdu), message_pdu)
            test.expect(test.dut.at1.wait_for(".*CMTI.*"))

            test.log.step("4. Read incoming messages and verify correct content in PDU mode,")
            test.expect(test.dut.at1.send_and_verify("AT+CMGR={}".format(sms_index[0]), ".*OK.*"))
            test.expect(re.search(".*{}.*{}.*".format(test.dut.sim.sca_pdu[:4], lang[52:]), test.dut.at1.last_response))
            test.expect(test.dut.at1.send_and_verify("AT+CMGR={}".format(str(int(sms_index[0])+1)), ".*OK.*"))
            test.expect(re.search(".*{}.*{}.*".format(test.dut.sim.sca_pdu[:4], lang[52:]), test.dut.at1.last_response))

            test.log.step("5. Read messages in text mode,")
            test.expect(dstl_select_sms_message_format(test.dut, "TEXT"))
            test.expect(test.dut.at1.send_and_verify("AT+CMGR={}".format(sms_index[0]), ".*OK.*"))
            test.expect(re.search(".*{}.*".format(regex_content[i]), test.dut.at1.last_response))
            test.log.info(".*{}.*".format(regex_content[i]))
            test.expect(test.dut.at1.send_and_verify("AT+CMGR={}".format(str(int(sms_index[0]) + 1)), ".*OK.*"))
            test.expect(re.search(".*{}.*".format(regex_content[i]), test.dut.at1.last_response))
            test.log.info(".*{}.*".format(regex_content[i]))
            if i < 2:
                test.log.step("6. Repeat steps 1-5 also for Spanish and Portuguese Single Shift Character Sets")

    def cleanup(test):
        dstl_delete_all_sms_messages(test.dut)
        test.dut.at1.send_and_verify("AT&F", ".*OK.*")
        test.dut.at1.send_and_verify("AT&W", ".*OK.*")

    def sms_command(test, command, length, message):
        test.expect(test.dut.at1.send_and_verify("AT+CMG{}={}".format(command.upper()[:1], length), ">"))
        test.expect(test.dut.at1.send_and_verify(message, end="\u001A", expect=r"\+CMG{}: \d{}.*OK.*".
                                                 format(command.upper()[:1], "{1,3}"), timeout=20))

    def pdu_length(test, pdu):
        return str(int((len(pdu) - (int(ord(bytes.fromhex(pdu[0:2]))) + 1) * 2) / 2))


if "__main__" == __name__:
    unicorn.main()
