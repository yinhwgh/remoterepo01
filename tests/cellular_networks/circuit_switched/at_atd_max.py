# author: xiaolin.liu@thalesgroup.com
# location: Dalian
# TC0071332.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module
from dstl.phonebook import phonebook_handle
import re


class Test(BaseTest):
    """
    TC0071332.001 - TpCAtdMax
    Intention: Checked length for phone number: during dialing the number for data and voice.
    for Viper:
    restricted number of phonebook items up to 40 digits
    restricted text of phonebook items up to 14 digits
    restricted text of atd items up to 80 digits
        """

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.dut.at1.send_and_verify('AT+CSCS="GSM"', expect='OK'))
        pass

    def run(test):
        num_39 = "123456789012345678901234567890123456789"
        text_13 = "ASDFGHJKLOIUY"
        n_79 = "1234567890123456789012345678901234567890123456789012345678901234567890123456789"
        num_array = [num_39, num_39 + '0', num_39 + '01', num_39 * 2]
        text_array = [text_13, text_13 + 'A', text_13 + 'AB', text_13 * 2]
        n_array = [n_79, n_79 + '0', n_79 + '01', n_79 * 2]

        test.log.step('1. Check the number length for dial number')
        lengh = ['79', '80', '81', '158']
        for i in range(len(lengh)):
            test.log.step('1.'+str(i+1)+'. The number length is: ' + (lengh[i]))
            if len(n_array[i]) <= 80:
                test.expect(test.dut.at1.send_and_verify(f"ATD{n_array[i]};"))
                test.dut.at1.send_and_verify('AT+CHUP', expect='.*OK.*')
                test.sleep(2)
            else:
                test.expect(test.dut.at1.send_and_verify(f"ATD{n_array[i]};", expect='ERROR'))
                test.dut.at1.send_and_verify('AT+CHUP', expect='.*OK.*')

        test.log.step('2. Check the number length for Phone book number')
        num_lengh = ['39', '40', '41', '78']
        text_lengh = ['13', '14', '15', '26']

        for i in range(len(lengh)):
            test.log.step('2.'+str(i+1)+'. The number length is: ' + (num_lengh[i])+', and the text length is: '
                          + (text_lengh[i]))
            test.expect(test.dut.at1.send_and_verify('AT+CPBS=?', expect='.*OK.*'))
            find_storage = re.findall("SM|ME|FD", test.dut.at1.last_response)
            for storage in find_storage:
                if storage != "FD":
                    if len(num_array[i]) <= 40 and len(text_array[i]) <= 14:
                        test.expect(test.dut.at1.send_and_verify(f"AT+CPBS=\"{storage}\""), "OK")
                        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW=1,\"{num_array[i]}\",129,"
                                                                 f"\"{text_array[i]}\""))
                        test.expect(test.dut.at1.send_and_verify("at^sblk", "OK"))
                        test.expect(test.dut.at1.send_and_verify(f"ATD{num_array[i]};"))
                        test.dut.at1.send_and_verify('AT+CHUP', expect='.*OK.*')
                        test.expect(test.dut.at1.send_and_verify(f"ATD>{text_array[i]};"))
                        test.dut.at1.send_and_verify('AT+CHUP', expect='.*OK.*')
                        test.sleep(2)
                    else:
                        test.expect(test.dut.at1.send_and_verify(f"AT+CPBS=\"{storage}\"", "OK"))
                        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW=1,\"{num_array[i]}\",129,"
                                                                 f"\"{text_array[i]}\"",
                                                                 expect='\+CME ERROR: dial string too long'))

                else:
                    if len(num_array[i]) <= 40 and len(text_array[i]) <= 14:
                        test.expect(test.dut.at1.send_and_verify(f"AT+CPBS=\"{storage}\",{test.dut.sim.pin2}", "OK"))
                        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW=1,\"{num_array[i]}\",129,"
                                                                 f"\"{text_array[i]}\""))
                        test.expect(test.dut.at1.send_and_verify("at^sblk", "OK"))
                        test.expect(test.dut.at1.send_and_verify(f"ATD{num_array[i]};"))
                        test.dut.at1.send_and_verify('AT+CHUP', expect='.*OK.*')

                        ret = test.expect(test.dut.at1.send_and_verify(f"ATD>{text_array[i]};"))
                        test.dut.at1.send_and_verify('AT+CHUP', expect='.*OK.*')
                        if not ret:     # to analyze VPR02-990
                            test.dut.at1.send_and_verify('at+CPBS?')
                            test.dut.at1.send_and_verify('at+CPBR=1,10')
                            test.dut.at1.send_and_verify('at+CPBS="FD"')
                            test.dut.at1.send_and_verify('at+CPBR=1,10')
                            test.dut.at1.send_and_verify('at+CPBS="SM"')
                            test.dut.at1.send_and_verify('at+CPBR=1,10')

                    else:
                        test.expect(test.dut.at1.send_and_verify(f"AT+CPBS=\"{storage}\"", "OK"))
                        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW=1,\"{num_array[i]}\",129,"
                                                                 f"\"{text_array[i]}\"",
                                                                 expect='\+CME ERROR: dial string too long'))

            # Data Call: Not implemented since Viper does not support.

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('AT&F', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT&W', expect='.*OK.*'))
        pass


if '__main__' == __name__:
    unicorn.main()
