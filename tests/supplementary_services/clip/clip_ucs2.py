#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0082193.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.phonebook import phonebook_handle
from dstl.configuration import character_set
from dstl.call import setup_voice_call
from random import randint

class Test(BaseTest):
    """
    TC0082193.001 - TpCClipUcs2
    Intention:
        Check call status using CLIP (Calling Line Identification Presentation) command with UCS2 mode enabled in folowing situations:
        - a voice call
        - a data call
        - a fax call

        Test case created due to IPIS100040113 requiments.
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_register_to_network()
        test.r1.dstl_detect()
        test.r1.dstl_register_to_network()

    def run(test):
        support_data_call = test.dut.dstl_is_data_call_supported()
        support_fax_call = test.dut.dstl_is_fax_call_supported()
        # Need some time after enter pin to load SM
        test.attempt(test.dut.at1.send_and_verify, "AT+CPBS=?", expect="SM", retry=5, sleep=5)
        test.expect(test.dut.dstl_clear_all_pb_storage())
        test.expect(test.dut.dstl_clear_mc_rc_dc_ld_storage())
        mo_number = test.r1.sim.nat_voice_nr
        max_pb_text_len = test.dut.dstl_get_pb_storage_max_text_length("SM")
        unprintable_list = [127]
        pb_text_gsm, pb_text_ucs2 = test.dut.dstl_generate_random_text(max_pb_text_len, except_char_indexes=unprintable_list)

        call_types = ["Voice", "Data", "Fax"]
        steps = ["1. A voice call in GSM/UCS2 mode",
                 "2. A data call in GSM/UCS2 mode",
                 "3. A fax call in GSM/UCS2 mode",
                 "4. A voice call in GSM/UCS2 mode (entry created in SM phonebook)",
                 "5. A data call in GSM/UCS2 mode (entry created in SM phonebook)",
                 "6. A fax call in GSM/UCS2 mode (entry created in SM phonebook)"]
        index = -1
        clip_gsm = f"\+CLIP: \"{mo_number}\",129,,,,0"
        clip_ucs2 = f"\+CLIP: \"{mo_number}\",129,,,,0"

        
        test.expect(test.dut.at1.send_and_verify("AT+CLIP=1"))
        test.dut.at1.send_and_verify("AT+CLIP?", "\+CLIP: 1,[012]")
        for step in steps:
            index += 1
            test.log.step(step)
            test.sleep(3)

            call_type = call_types[index%3]
            if call_type == "Data":
                if support_data_call == True:
                    test.expect(False, msg="Data call part is not implemented.")
                else:
                    test.log.info("Module dose not support data call, skip step.")
                continue
            elif call_type == "Fax":
                if support_fax_call == True:
                    test.expect(False, msg="Fax call part is not implemented.")
                else:
                    test.log.info("Module dose not support fax call, skip step.")
                continue
            check_clip_urc_on_call = eval(f'test.check_clip_urc_on_{call_type.lower()}_call')
        
            test.log.info("***** Set to GSM mode ********")
            test.dut.dstl_set_character_set("GSM")
            if index == 3:
                test.log.info("***** Save number to SM  ********")
                test.expect(test.dut.dstl_set_pb_memory_storage("SM"))
                test.expect(test.dut.dstl_write_pb_entries("1", mo_number,"129",pb_text_gsm))
                test.expect(test.dut.at1.send_and_verify("AT+CPBR=1", mo_number))
                pb_text_gsm_re = test.parse_text_to_regular_expression(pb_text_gsm)
                clip_gsm = f"\+CLIP: \"{mo_number}\",129,,,\"{pb_text_gsm_re}\",0"
                clip_ucs2 = f"\+CLIP: \"{mo_number}\",129,,,\"{pb_text_ucs2}\",0"
            elif index > 3:
                test.expect(test.dut.at1.send_and_verify("AT+CPBS?", "SM"))
                test.expect(test.dut.at1.send_and_verify("AT+CPBR=1", mo_number))
            check_clip_urc_on_call(clip_gsm)

            test.log.info("***** Set to UCS2 mode ********")
            test.dut.dstl_set_character_set("UCS2")
            check_clip_urc_on_call(clip_ucs2)

    def cleanup(test):
        test.dut.dstl_set_character_set("GSM")
        test.expect(test.dut.at1.send_and_verify("AT+CLIP=0"))
        test.dut.at1.send_and_verify("AT+CLIP?", "\+CLIP: 0,[012]")

    def check_clip_urc_on_voice_call(test, clip_urc):
        """
        For voice call, clip urc appears after every RING.
        For data call and fax call, clip URC only appears once
        """
        test.sleep(5)
        mt_number = test.dut.sim.nat_voice_nr
        test.attempt(test.r1.at1.send_and_verify, f"ATD{mt_number};", "OK", retry=3, sleep=5)
        no_carrier = False
        while not no_carrier:
            if test.expect(test.dut.at1.wait_for("RING", timeout=60)):
                if test.dut.at1.wait_for(clip_urc, timeout=6, append=True):
                    test.log.info(f"Found URC {clip_urc} in response.")
                    test.dut.dstl_check_voice_call_status_by_clcc(is_mo=False, expect_status='4')
                    test.sleep(0.2)
                    test.dut.at1.read(append=True)
                    no_carrier = "NO CARRIER" in test.dut.at1.last_response
                elif "NO CARRIER" in test.dut.at1.last_response or "NO ANSWER" in test.r1.at1.last_response:
                        test.log.info("Call is ended after multiple RINGs.")
                        no_carrier = True
                else:
                    test.expect(False, msg=f'Cannot find URC {clip_urc} in response')
            elif "NO CARRIER" in test.dut.at1.last_response:
                no_carrier = True
            else:
                test.log.error("Module is not Rung.")
                break
        test.expect(test.dut.dstl_release_call())
        test.expect(test.r1.dstl_release_call())
        test.sleep(2)
    
    def check_clip_urc_on_data_call(test, clip_urc):
        raise Exception("Checking CLIP on Data Call is not implemented.")

    def check_clip_urc_on_fax_call(test, clip_urc):
        raise Exception("Checking CLIP on Fax Call is not implemented.")
    def parse_text_to_regular_expression(test,text, exceptance=[]):
        special_chars = ['\\','.','+','*','(',')','?','^', ']', '[', '{', '}', '|', '"']
        for char in special_chars:
            if char in text and char not in exceptance:
                text = text.replace(char,'\\' + char)
        return text
    

if '__main__' == __name__:
    unicorn.main()


