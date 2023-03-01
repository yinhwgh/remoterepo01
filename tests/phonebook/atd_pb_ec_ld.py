#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0103988.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.security import lock_unlock_sim
from dstl.phonebook import phonebook_handle
from dstl.call import setup_voice_call
import random
import re


class Test(BaseTest):
    """
    TC0103988.001 - AtdPb_EC_LD  
    """

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.expect(test.r1.dstl_register_to_network())
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2"))
        
    def run(test):
        test.log.info("******** Checking if module supports storage LD an EC ********")
        test_mems = []
        test.attempt(test.dut.at1.send_and_verify, "AT+CPBS?", "OK", retry=3, sleep=2)
        test.expect(test.dut.at1.send_and_verify("AT+CPBS=?"))
        if "LD" in test.dut.at1.last_response:
            test_mems.append("LD")
        if "EC" in test.dut.at1.last_response:
            test_mems.append("EC")
        elif "EN" in test.dut.at1.last_response:
            test_mems.append("EN")
        if len(test_mems) < 2:
            test.log.error("Cannot find both LD and EC(EN) storages in response.")

        test.log.info("******** Writing an entry to SM for testing LD ********")
        test.expect(test.dut.at1.send_and_verify("AT+CPBS=SM"))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW=1,\"{test.r1.sim.nat_voice_nr}\",,\"R1 VOICE NR\""))
        
        for mem in test_mems:
            test.log.step(f"{mem} 1. Set phonebook memory storage to {mem}")
            max_loc = test.dut.dstl_get_pb_storage_max_location(mem)

            test.log.step(f"{mem} 2. Fail to write entry to {mem}")
            test.expect(test.dut.at1.send_and_verify("AT+CPBR=1,\"123456\",,\"name\"", "ERROR"))
            
            test.log.step(f"{mem} 3. Call a random entry in {mem} with command ATD>\"{mem}n\"")
            record_num, pb_num, pb_text = test.get_record_for_mem(mem)
            test.log.info(f"Random entry is {record_num}, {pb_num}, {pb_text}")
            if record_num < 0:
                test.expect(record_num > 0,
                            msg=f"Cannot get valid record number in storage {mem}. Tests for {mem} have to be stopped.")
                test.expect(test.dut.at1.send_and_verify(f"AT+CPBR=1,{max_loc}"))
                continue
            test.call_with_type(type=1, mem=mem, location=record_num, alpha=pb_text)

            test.log.step(f"{mem} 4. Call a random entry in {mem} with command ATD>\"n\"")
            if pb_num == "":
                test.log.error("Cannot get valid phone number in storage {mem}, index {record_num}.")
                test.expect(test.dut.at1.send_and_verify(f"AT+CPBR=1,{max_loc}"))
                continue
            test.call_with_type(type=2, mem=mem, location=record_num, alpha=pb_text)

            test.log.step(f"{mem} 5. Call a random entry in {mem} with command ATD>\"str\"")
            if pb_text == "":
                test.expect(False, f"Cannot get valid text in storage {mem}, index {record_num}.")
                test.expect(test.dut.at1.send_and_verify(f"AT+CPBR=1,{max_loc}"))
                continue
            test.call_with_type(type=3, mem=mem, location=record_num, alpha=pb_text)

    def cleanup(test):
        test.expect(test.dut.dstl_release_call())
        test.expect(test.dut.at1.send_and_verify("AT+CPBS=SM"))

    def prepare_records_for_ld(test, location):
        test.log.info("******** Preparing records in LD ********")
        test.log.info(f"Make calls to generate record in location {location}")
        for i in range(1, location + 1):
            if i == location:
                num = test.r1.sim.nat_voice_nr
            else:
                num = i
            test.expect(test.dut.at1.send_and_verify(f"ATD{num};"))
            test.sleep(1)
        test.expect(test.dut.dstl_release_call())
        test.expect(
            test.dut.at1.send_and_verify(f"AT+CPBR={location}", f"{location},\"{test.r1.sim.nat_voice_nr}\""))

    def get_record_for_mem(test, mem):
        record_num = '\d+'
        pb_number = ""
        pb_text = ""
        max_loc = test.dut.dstl_get_pb_storage_max_location(mem)
        if mem == "LD":
            record_num = random.randint(1, int(max_loc))
            record_num = 1
            test.prepare_records_for_ld(record_num)
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBR=1,{max_loc}"))
        # Find items with values: number, alpha
        record_info = re.findall(f"CPBR: ({record_num}),\"(\d+)\",\d+,\"(.+?)\"", test.dut.at1.last_response)
        if not record_info and mem != 'LD':
            # Find items at least with number
            record_info = re.findall(f"CPBR: ({record_num}),\"(\d+)\",\d+,\"(.*?)\"", test.dut.at1.last_response)
        if record_info:
            record_num = int(record_info[0][0])
            pb_number = record_info[0][1]
            pb_text = record_info[0][2]
        else:
            record_num = -1
        return record_num, pb_number, pb_text

    def call_with_type(test, type, mem, location, alpha):
        if type == 1:
            call_cmd = f"ATD>\"{mem}{location}\";"
        elif type == 2:
            call_cmd = f"ATD>{location};"
        elif type == 3:
            call_cmd = f"ATD>\"{alpha}\";"
        else:
            test.expect(isinstance(type, int) and type in [1, 2, 3], msg="Only 1, 2, 3 are valid types.")
        test.expect(test.dut.at1.send_and_verify(call_cmd, "OK"))
        if mem == "LD":
            test.expect(test.r1.at1.wait_for("RING"))
        else:
            test.expect(test.dut.at1.wait_for("NO CARRIER"))
        test.expect(test.dut.dstl_release_call())
        test.sleep(2)

if __name__ == "__main__":
        unicorn.main()
