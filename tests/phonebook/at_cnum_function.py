#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0095751.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.configuration import character_set
from dstl.auxiliary import init


class AtCnumFunc(BaseTest):
    """
    TC0095751.001 - AtCnumFunc
    Subscriber number: 2
    Only automated for Dingo, should manually test for Cougar
    """

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.r1.dstl_register_to_network())

    def run(test):
        # Initiate variables
        code_international = test.dut.sim.int_voice_nr
        code_national = test.dut.sim.nat_voice_nr
        params = {
            "set_alpha_gsm_1": "int GSM",
            "set_alpha_gsm_2": "nat GSM",
            "alpha_converted_from_gsm_1": "0069006E0074002000470053004D",
            "alpha_converted_from_gsm_2": "006E00610074002000470053004D",
            "set_alpha_ucs2_1": "0069006E00740055004300530032",
            "set_alpha_ucs2_2": "006E006100740055004300530032",
            "alpha_converted_from_ucs2_1": "intUCS2",
            "alpha_converted_from_ucs2_2": "natUCS2"
        }
        character_set_loop = ("GSM", "UCS2")
        code_type = (145, 161, 129, 128)
        # Loop for character sets
        for i in range(0, len(character_set_loop)):
            char_set = character_set_loop[i]
            if i > 0:
                code_international = code_international.replace("+86", "")
            alpha_1 = params["set_alpha_{}_1".format(char_set.lower())]
            alpha_2 = params["set_alpha_{}_2".format(char_set.lower())]
            test.log.info('******************Loop {}/{}********************'.format(i+1, len(character_set_loop)))
            test.log.info('{}.1. Save phone book to "ON" storage with character set: {}'.format(i+1, char_set))
            test.expect(test.dut.dstl_set_character_set(char_set))
            test.expect(test.dut.at1.send_and_verify("AT+CPBS=\"ON\""), "OK")
            test.expect(test.dut.at1.send_and_verify("AT+CPBW=1,\"{}\",{},\"{}\"".
                        format(code_international, code_type[i*2], alpha_1)))
            test.expect(test.dut.at1.send_and_verify("AT+CPBW=2,\"{}\",{},\"{}\"".
                        format(code_national, code_type[i*2+1], alpha_2)))
            expected_cnum_result_in_gsm = "\+CNUM: \"{}\",\"{}\",{}\s+" \
                                          "\+CNUM: \"{}\",\"{}\",{}".\
                format(alpha_1, code_international.replace("+", "[+]"), code_type[i*2],
                       alpha_2, code_national, code_type[i*2+1])

            test.expect(test.dut.at1.send_and_verify("AT+CNUM", expect=expected_cnum_result_in_gsm))
            # Check CNUM with another character set
            another_char_set = "UCS2" if char_set is "GSM" else "GSM"
            test.log.info('{}.2. Check phonebook in "ON" storage with character set {}'.format(i+1, another_char_set))
            test.expect(test.dut.dstl_set_character_set(another_char_set))
            alpha_1_in_another_char_set = params["alpha_converted_from_{}_1".format(char_set.lower())]
            alpha_2_in_another_char_set = params["alpha_converted_from_{}_2".format(char_set.lower())]
            expected_cnum_result_in_ucs2 = "\+CNUM: \"{}\",\"{}\",{}\s+" \
                                          "\+CNUM: \"{}\",\"{}\",{}".\
                format(alpha_1_in_another_char_set, code_international.replace("+", "[+]"), code_type[i*2],
                       alpha_2_in_another_char_set, code_national, code_type[i*2+1])
            test.expect(test.dut.at1.send_and_verify("AT+CNUM", expect=expected_cnum_result_in_ucs2))
            # Call with another character set
            test.log.info('{}.3. Number in "ON" storage can be successfully called with character set'.format(i+1, another_char_set))
            test.r1.at1.send("ATD{};".format(code_international))
            test.expect(test.dut.at1.wait_for("RING", timeout=10))
            test.dut.at1.send("ATA")
            test.expect(test.dut.at1.wait_for("OK", timeout=10))
            test.r1.at1.send("ATH")
            test.expect(test.dut.at1.wait_for("NO CARRIER", timeout=10))
            test.r1.at1.send("ATD{};".format(code_national))
            test.expect(test.dut.at1.wait_for("RING", timeout=10))
            test.dut.at1.send("ATA")
            test.expect(test.dut.at1.wait_for("OK", timeout=10))
            test.r1.at1.send("ATH")
            test.expect(test.dut.at1.wait_for("NO CARRIER", timeout=10))

    def cleanup(test):
        test.expect(test.dut.dstl_set_character_set("GSM"))


if __name__ == "__main__":
        unicorn.main()
