#author: lei.chen@thalesgroup.com
#location: Dalian
#TC0088283.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module
from dstl.security import lock_unlock_sim
from dstl.auxiliary.devboard import devboard
from dstl.call import extended_list_of_calls
from dstl.call import setup_voice_call
import re

class Test(BaseTest):
    """
    TC0088283.001 - TpEmCallBasic 
    Check emergency-calls with SIM and without PIN and without SIM
    """
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.at1.send_and_verify('AT+cmee=2', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at^scfg="Call/ECC",0', expect='OK'))

    def run(test):
        test.log.step("1. check, if SIM has ECC field")
        ecc_status_map = {
            0: "2G/3G no ECC field",
            1: "2G SIM ECC field exist, but empty",
            2: "2G ECC filed exists with values",
            3: "3G SIM ECC field exist, but empty",
            4: "3G ECC filed exists with values"
        }
        numbers = []
        uicc_type = test.detect_uicc_type()
        ecc_status, numbers = test.detect_ecc_file_status(uicc_type)
        test.log.info(f"Detected ecc status is {ecc_status} - {ecc_status_map[ecc_status]}")
        ecc_with_record_status = [2, 4]

        test.log.step("2.Make EM-calls - with SIM PIN locked")
        test.expect(test.dut.dstl_lock_sim())
        test.expect(test.dut.dstl_restart())
        test.attempt(test.dut.at1.send_and_verify, "AT+CPIN?", "SIM PIN", retry=3, sleep=1)
        if ecc_status in ecc_with_record_status:
            if not numbers:
                test.log.error("ECC field exists with records, but read numbers failed. Will used default numbers to continue tests")

        numbers = ['911', '112'] if numbers == [] else numbers
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Call/ECC",0', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG?', expect='\^SCFG: "Call/ECC","0"'))
        for number in numbers:
            test.expect(test.dut.at1.send_and_verify(f'ATD{number};', expect='OK'))
            test.expect(test.dut.at1.send_and_verify('AT^SLCC', expect=f'SLCC: 1,0,(2|3),0,0,0,"{number}",161'))
            test.expect(test.dut.dstl_release_call())
            test.sleep(1)

        test.log.step("3.Make EM-calls - with SIM PIN ready")
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify('AT+CMEE=2', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CREG=2', expect='OK'))
        for number in numbers:
            test.expect(test.dut.at1.send_and_verify(f'ATD{number};', expect='OK'))
            test.expect(test.dut.at1.send_and_verify('AT^SLCC', expect=f'SLCC: 1,0,(2|3),0,0,0,"{number}",161'))
            test.expect(test.dut.dstl_release_call())
            test.sleep(1)

        test.log.step("4.Make EM-calls - without SIM")
        call_numbers = ['112','911','08','000','110','999','118','119']
        test.expect(test.dut.at1.send_and_verify('AT^SCKS=1'))
        test.expect(test.dut.dstl_remove_sim())
        test.attempt(test.dut.at1.send_and_verify,"AT+CPIN?", "SIM not inserted", retry=5, sleep=1)
        for number in call_numbers:
            test.expect(test.dut.at1.send_and_verify(f'ATD{number};', expect='OK'))
            # if number == "000" and test.dut.project.upper() == "VIPER":
            #     test.log.warning("Due to IPIS100333557 not to fix for Viper, verify type 145 for 000.")
            #     type = "145"
            # else:
            type = "161"
            test.expect(test.dut.at1.send_and_verify('AT^SLCC',
                                                     expect=f'SLCC: 1,0,(2|3),0,0,0,"{number}",{type}'))
            test.expect(test.dut.dstl_release_call())
            test.sleep(1)

    def cleanup(test):
        test.expect(test.dut.dstl_insert_sim())
        test.expect(test.dut.at1.send_and_verify('at^scks=0'))
        test.attempt(test.dut.at1.send_and_verify,"ATH", expect="OK", retry=3, sleep=1)
    
    def detect_uicc_type(test):
        uicc_type = ""
        test.dut.at1.send_and_verify('AT+CRSM=242')
        if "144,0,00" in test.dut.at1.last_response or "144,0,\"00" in test.dut.at1.last_response:
            test.log.info("Detecting SIM Card is 2G, uicc type is set to 0x01")
            uicc_type = "0x01"
        elif "144,0,62" in test.dut.at1.last_response or "144,0,\"62" in test.dut.at1.last_response:
            test.log.info("Detecting SIM Card is 3G, uicc type is set to 0x03")
            uicc_type = "0x03"
        elif "145,11," in test.dut.at1.last_response:
            test.log.error("SIM don't answer correct the request, maybe SIM busy? Quit test.")
            exit()
        else:
            test.log.error("Cannot detect SIM status, quit test.")
            exit()
        return uicc_type

    def detect_ecc_file_status(test, uicc_type):
        # check if ECC file exist
        ecc_status = 0
        numbers = []
        test.dut.at1.send_and_verify("AT+CRSM=192,28599")
        if "144,0" in test.dut.at1.last_response:
            test.log.info("Found ECC file")
            if "0x01" in uicc_type:
                ecc_status = 1
                i = 0
                while i < 15:
                    test.dut.at1.send_and_verify(f"AT+CRSM=176,28599,0,{i},{i+3}")
                    if "144,0," in test.dut.at1.last_response and "FFFFFF" not in test.dut.at1.last_response:
                        test.log.info("ECC file is not empty, read number")
                        number = test.detect_ecc_file_number(test.dut.at1.last_response)
                        if number != "":
                            numbers.append(number)
                        ecc_status = 2
                    elif "107,0" in test.dut.at1.last_response or "103,0" in test.dut.at1.last_response:
                        test.log.info("Error: parameter wrong, abort loop")
                        break
                    i += 3
            elif "0x03" in uicc_type:
                ecc_status = 3
                test.log.info("Reading record length for 3G UICC")
                test.dut.at1.send_and_verify("AT+CRSM=178,28599,1,4,255")
                res_format = re.compile('CRSM: 103,"?(\d+)"?')
                match_format =  res_format.findall(test.dut.at1.last_response)
                if match_format:
                    record_len = match_format[0]
                    for i in range(1,10):
                        test.dut.at1.send_and_verify(f"AT+CRSM=178,28599,{i},4,{record_len}")
                        if "106,131" in test.dut.at1.last_response:
                            test.log.info("Error response, exit loop")
                            break
                        else:
                            if "144,0,\"F" not in test.dut.at1.last_response and "103,16" not in test.dut.at1.last_response:
                                test.log.info("ECC file is not empty, read number")
                                number = test.detect_ecc_file_number(test.dut.at1.last_response)
                                if number != "":
                                    numbers.append(number)
                                ecc_status = 4
                else:
                    # No record found
                    pass
        return ecc_status, numbers

    def detect_ecc_file_number(test, response):
        number = ""
        match_format = re.search(f"\+CRSM: 144,0,\"(.+)\"", test.dut.at1.last_response)
        if match_format:
            value = match_format.group(1)
            test.log.info("Trying to find number in response.")
            exit_loop = False
            i = 0
            while i < len(value):
                if i+1 < len(value) and value[i+1]!='F':
                    number += value[i+1]
                elif i+1 < len(value) and value[i+1]=='F':
                    exit_loop = True
                if value[i] != 'F': 
                    number += value[i]
                else:
                    exit_loop = True
                if exit_loop:
                    break
                i += 2
            test.log.info(f"Detected number {number} in response.")
        else:
            test.log.error(f"Invalid response, cannot detect emergency numbers: {response}")
        return number

if '__main__' == __name__:
    unicorn.main()
