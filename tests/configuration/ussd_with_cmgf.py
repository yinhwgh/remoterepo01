#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0093708.002


import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.sms import select_sms_format
from dstl.configuration import character_set

import re

class Test(BaseTest):
    """TC0095954.002 - UssdwithCmgf

    Intention: This case is for customer IPIS100202836, when AT+CMGF=1, and AT+CUSD=1, diplayed information is in UCS2 mode, not in text mode.
    Description:
    1. Switch ON module
    2. Registered to the network
    3. Set text mode AT+CMGF=1 (Scripts extended this step to check both cmgf=0 and cmgf=1)
    4. Set AT+CSCS="GSM" (Scripts extended this step to check both "GSM" and "UCS2")
    5. Set AT+CUSD=1
    6. Send #code USSD ( it is differents depend on the network).
    7. Wait for URC response from the network side.
    """
    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        ussd_code = "*141#"
        test.log.step("1. Switch ON module")
        test.log.step("2. Registered to the network")
        test.expect(test.dut.dstl_register_to_network())
        loops = {"1": "AT+CMGF=1, AT+CSCS=GSM",
                 "2": "AT+CMGF=1, AT+CSCS=UCS2",
                 "3": "AT+CMGF=0, AT+CSCS=GSM",
                 "4": "AT+CMGF=0, AT+CSCS=UCS2"}
        for k, v in loops.items():
            test.log.info(f"Loop {k}: v")
        loop = 1
        for sms_format in ["Text", "PDU"]:
            for char_set in ['GSM', 'UCS2']:
                test.log.step(f"Loop {loop}/4 3. Set text mode AT+CMGF=\"{sms_format}\"")
                test.expect(test.dut.dstl_select_sms_message_format(sms_format))
            
                test.log.step(f"Loop {loop}/4 4. Set AT+CSCS=\"{char_set}\"")
                test.expect(test.dut.dstl_set_character_set(char_set))

                test.log.step(f"Loop {loop}/4 5. Set AT+CUSD=1")
                test.expect(test.dut.at1.send_and_verify("AT+CUSD=1"))

                test.log.step(f"Loop {loop}/4 6. Send #code USSD ( it is differents depend on the network).")
                test.expect(test.dut.at1.send_and_verify(f"ATD{ussd_code};", "OK"))
                test.expect(test.dut.at1.send_and_verify("AT+COPS?", "OK"))

                test.log.step(f"Loop {loop}/4 7. Wait for URC response from the network side.")
                display_cusd_urc = test.dut.at1.wait_for("\+CUSD: .*", timeout=60)
                if display_cusd_urc:
                    cusd_urc = test.dut.at1.last_response
                    ussd_data = re.findall("\+CUSD: [0-5],\"(.*)\",\d+", cusd_urc)
                    if ussd_data:
                        ussd_data = ussd_data[0]
                        test.expect(not test.dut.dstl_is_text_in_ucs2_mode(ussd_data), msg="USSD data is in UCS2 mode.")
                    else:
                        test.expect(ussd_data, msg="Unexpected format of CUSD URC.")
                
                else:
                    test.expect(display_cusd_urc, msg="Cannot find CUSD URC.")
                loop += 1
            loop += 1

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT&F"))

if "__main__" == __name__:
    unicorn.main()
