# responsible: lei.chen@thalesgroup.com
# location: Dalian
# TC0087924.001

import unicorn
from core.basetest import BaseTest
from dstl.phonebook import phonebook_handle
from dstl.auxiliary import init
from dstl.network_service import register_to_network
import re
from dstl.call import setup_voice_call
import random


class Test(BaseTest):
    '''
    TC0087924.001 - IntelPhonebookEC
    Intention: Check functions with EC phonebook.
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_enter_pin()
        test.sleep(2)

    def run(test):

        test.log.info("******* Detecting module is in UICC SIM mode or UICC USIM mode. *******")
        test.expect(test.dut.at1.send_and_verify("AT+CRSM=242"))
        if re.search("\+CRSM: \d+,\d+,\"62", test.dut.at1.last_response):
            test.log.info("Detected module is in UICC USIM mode.")
        elif re.search("\+CRSM: \d+,\d+,\"00", test.dut.at1.last_response):
            test.log.info("Detected module is in UICC SIM mode.")
        else:
            test.log.error("Module is neither in UICC SIM mode or UICC USIM mode.")
        
        test.log.info("******* Detecting EC/EN storage *******")
        test.attempt(test.dut.at1.send_and_verify, "AT+CPBS?", "OK", retry=5, sleep=5)
        test.dut.at1.send_and_verify("AT+CPBS=?")
        ec = "EC"
        if "EC" in test.dut.at1.last_response:
            test.log.info("Detected EC in response")
        elif "EN" in test.dut.at1.last_response:
            ec = "EN"
            test.log.info("Detected EN in response")
        else:
            raise Exception("Module does not support EC or EN storage, cannot continue tests.")

        test.log.step('1.delete all entries from all phonebook')
        test.dut.dstl_clear_all_pb_storage()

        test.log.step('2.set phonebook memory to EC')
        test.expect(test.dut.dstl_set_pb_memory_storage(ec))
        ec_response = test.dut.at1.last_response

        test.log.step('3.check how many entries are supported')
        max_loc = test.dut.dstl_get_pb_storage_max_location(ec)
        max_loc = int(max_loc)

        test.log.step('4.try to select a not existing phonebook (AT+CPBS="AA"), the appropriate error message will be output')
        test.expect(test.dut.at1.send_and_verify("AT+CPBS=\"AA\"", "ERROR"))

        test.log.step('5.check if EC entry still exists (AT+CPBS?)')
        test.expect(test.dut.at1.send_and_verify("AT+CPBS?", ec_response))

        test.log.step('6.try to use AT+CPBW command to write entry into phonebook and erase entry from phonebook, appropriate error message will be displayed')
        un_allow_error = "\+CME ERROR: operation not allowed"
        test.expect(test.dut.at1.send_and_verify("AT+CPBW=1", un_allow_error))
        test.expect(test.dut.at1.send_and_verify("AT+CPBW=1,\"999\"", un_allow_error))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW=1,\"{test.dut.sim.nat_voice_nr}\"", un_allow_error))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW=1,\"{test.dut.sim.nat_voice_nr}\",129", un_allow_error))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW=1,\"{test.dut.sim.nat_voice_nr}\",,\"EC1\"", un_allow_error))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW={max_loc}", un_allow_error))

        test.log.step('7. check how many phonebook entries are supported (AT+CPBR=?)')
        test.expect(test.dut.at1.send_and_verify("AT+CPBR=?", f"\+CPBR: \(1-{max_loc}\).*OK"))

        test.log.step('8. read EC phonebook (AT+CPBR=1, x x=Maximum location number)')
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBR=1,{max_loc}", "\+CPBR: \d+,\"\d{1,3}\",129,\".*\""))

        test.log.step('9. try to read EC phonebook with maximum location number +1 more as allowed, the appropriate error message will be output')
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBR=1,{max_loc + 1}", "\+CME ERROR: invalid index"))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBR={max_loc + 1}", "\+CME ERROR: invalid index"))

        test.log.step('10. - try to read entries from the phonebook with the first value greater than the second (AT+CPBR=x, 1 x=Maximum location number),\
             the appropriate error message will be output')
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBR={max_loc},{max_loc-1}", "\+CME ERROR: invalid index"))
            
    def cleanup(test):
        test.expect(test.dut.dstl_set_pb_memory_storage('SM'))


if "__main__" == __name__:
    unicorn.main()
