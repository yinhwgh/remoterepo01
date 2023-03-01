# responsible: lei.chen@thalesgroup.com
# location: Dalian
# TC0093179.001, TC0093180.001, TC0093181.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.phonebook import phonebook_handle
from dstl.call import setup_voice_call
from dstl.call import extended_list_of_calls
from dstl.configuration import character_set
from dstl.supplementary_services import lock_unlock_facility

import random, re

class Test(BaseTest):
    '''
    TC0093279.001 - AtdPbDialSpecialChar_SM
    TC0093280.001 - AtdPbDialSpecialChar_FD
    TC0093281.001 - AtdPbDialSpecialChar_ON
    Intention:
    This test is provided to verify the functionality of Direct Dialling from Phone books with a concrete syntax (3GPP TS 27.007).
    ATD>SM"n"; ATD>"n"; and ATD>"str"; - MO Voice if supported. 
    Subscriber: 2
    Duration: about 15h30mins
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_register_to_network()
        test.r1.dstl_detect()
        test.r1.dstl_register_to_network()
        test.pb_memory = "SM"
    
    def run(test):
        test.log.info("****** Initialize modules  - START ******")
        test.expect(test.dut.dstl_lock_unlock_facility(facility="FD", lock=False))
        test.expect(test.dut.at1.send_and_verify("AT+CLIP=1"))
        test.expect(test.dut.at1.send_and_verify("AT+CLIR=2"))
        test.expect(test.dut.dstl_enable_slcc_urc())
        test.expect(test.r1.at1.send_and_verify("AT+CLIR=2"))
        test.expect(test.r1.dstl_enable_slcc_urc())
        char_sets = test.dut.dstl_get_supported_character_sets()
        mo_types = ['129', '145', '161']
        mt_types = ['129', '161']
        test.log.h3(f"Loop for types: {mo_types}")
        test.log.h3(f"Loop for character sets: {char_sets}")
        test.top_range_gsm = test.top_range_ucs2 = 255
        test.top_range_ira = 128
        test.log.info("****** Initialize modules  - END ******")

        test.log.info("****** Clear PB, set storage and get location - START ******")
        test.expect(test.dut.dstl_clear_all_pb_storage())
        test.expect(test.dut.dstl_clear_mc_rc_dc_ld_storage())
        test.pb_memory_list = test.dut.dstl_get_supported_pb_memory_list()
        test.log.info(f"Memory list: {test.pb_memory_list}.")
        test.expect(test.pb_memory_list and test.pb_memory in test.pb_memory_list,
                    msg=f"Module does not support test memory {test.pb_memory}.", critical=True)
        test.expect(test.dut.dstl_set_pb_memory_storage(test.pb_memory))
        test.max_loc = test.dut.dstl_get_pb_storage_max_location(test.pb_memory)
        half_idx = int(test.max_loc/2)
        half_idx = half_idx + 1 if half_idx in (0,1) else half_idx
        test.log.h3(f"Phonebook will be saved to index {half_idx}")
        test.log.info("****** Clear PB, set storage and get location - END ******")

        for char_set in char_sets:
            test.log.info("****** Loop for character set {char_set} ******")
            test.expect(test.dut.dstl_set_character_set(char_set))
            top_range = eval(f"test.top_range_{char_set.lower()}")
            for i in range(top_range + 1):
                for mo_type in mo_types:
                    r1_number = test.get_number(mo_type)
                    test.log.step(f"{i + 1}/{top_range}: character of {i}, character set {char_set},"
                                  f" number type {mo_type}.")
                    write_text = test.dut.dstl_get_write_character_by_decimal(i, char_set)
                    if not write_text:
                        test.log.info(f"No character found for {i}, continue to next character.")
                        continue
                    verify_text = test.dut.dstl_get_read_character_by_decimal(i, char_set)
                    test.expect(test.dut.dstl_set_pb_memory_storage(test.pb_memory))
                    test.expect(test.dut.dstl_write_pb_entries(half_idx, r1_number, mo_type,
                                                               write_text))

                    if not test.check_pb_in_mem(half_idx, r1_number, mo_type, verify_text):
                        test.expect(False, msg=f"Write entry with alpha text {write_text} failed. "
                                    f"Continue tests for next character.")
                        continue
                    else:
                        test.log.step(f"{i+1}.1 MO Call with memory + location.")
                        # read to clear buffer
                        test.r1.at1.read()
                        test.call_with_memory_location(half_idx)
                        test.check_slcc_and_clcc(expect_status=3, number=r1_number, alpha=verify_text)
                        test.expect(test.dut.dstl_release_call())
                        test.check_ld_dc_pb(r1_number, mo_type, verify_text)
                        test.expect(test.dut.dstl_clear_mc_rc_dc_ld_storage())
                        test.sleep(2)

                        test.log.step(f"{i+1}.2 MO Call with location only.")
                        clear_buffer = test.r1.at1.read()
                        test.expect(test.dut.dstl_set_pb_memory_storage(test.pb_memory))
                        test.call_with_location(half_idx)
                        test.check_slcc_and_clcc(expect_status=3, number=r1_number, alpha=verify_text)
                        test.expect(test.dut.dstl_release_call())
                        test.check_ld_dc_pb(r1_number, mo_type, verify_text)
                        test.expect(test.dut.dstl_clear_mc_rc_dc_ld_storage())
                        test.sleep(2)

                        test.log.step(f"{i+1}.3 MO Call with pb name only.")
                        clear_buffer = test.r1.at1.read()
                        test.expect(test.dut.dstl_set_pb_memory_storage(test.pb_memory))
                        test.call_with_alpha(verify_text)
                        test.check_slcc_and_clcc(expect_status=3, number=r1_number, alpha=verify_text)
                        test.expect(test.dut.dstl_release_call())
                        test.check_ld_dc_pb(r1_number, mo_type, verify_text)
                        test.expect(test.dut.dstl_clear_mc_rc_dc_ld_storage())
                        test.sleep(2)
                        
                        if mo_type in mt_types:
                            test.log.step(f"{i+1}.4 Test MT call for {mo_type}.")
                            test.expect(test.r1.at1.send_and_verify(f"ATD\"{test.dut.sim.nat_voice_nr}\";", "OK"))
                            test.expect(test.dut.at1.wait_for("RING"))
                            test.check_slcc_and_clcc(expect_status=4, number=r1_number, alpha=verify_text, is_mo=False)
                            test.expect(test.r1.dstl_release_call())
                            test.sleep(2)


    def cleanup(test):
        test.expect(test.dut.dstl_release_call())
        test.expect(test.r1.dstl_release_call())
        test.expect(test.dut.at1.send_and_verify("AT&F"))
        test.expect(test.dut.dstl_clear_all_pb_storage())

    def get_number(test, num_type):
        """ 
        Number will be read voice number of remote module from simdata according to num_type
        """
        if num_type == "145":
            prefix = "int"
        else:
            prefix = "nat"
        aux_number = eval(f"test.r1.sim.{prefix}_voice_nr")
        return aux_number
    
    def check_ld_dc_pb(test, number, type, text):
        cpbr_expect = f"+CPBR: 1,\"{number}\",{type},\"{text}\""
        pbs = ["LD", "DC"]
        for pb in pbs:
            if pb in test.pb_memory_list:
                test.expect(test.dut.dstl_set_pb_memory_storage("LD"))
                test.expect(test.dut.at1.send_and_verify("AT+CPBR=1"))
                last_response = test.dut.at1.last_response
                if text == '\x7f':
                    last_response = test.dut.at1.send_and_read_binary("AT+CPBR=1")
                    cpbr_expect = cpbr_expect.encode('utf-8')
                result = cpbr_expect in last_response
                if result == False:
                    test.log.error(f"{cpbr_expect} does not exist in response.")
                else:
                    test.log.info(f"{cpbr_expect} exists in response.")
            else:
                test.log.info(f"{pb} is not in module supported list.")
        
    def check_pb_in_mem(test, location, number, type, alpha):
        if alpha == '\x7f':
            last_response = test.dut.at1.send_and_read_binary(f"AT+CPBR=1,{test.max_loc}")
            read_item = True
        else:
            read_item = test.dut.at1.send_and_verify(f"AT+CPBR=1,{test.max_loc}", "\+CPBR:.*OK")
            last_response = test.dut.at1.last_response
        if read_item:
            expect_pb = f"+CPBR: {location},\"{number}\",{type},\"{alpha}\""
            if isinstance(last_response, (bytes, bytearray)):
                expect_pb = expect_pb.encode('utf-8')
            if expect_pb in last_response:
                test.log.info(f"Find {expect_pb} in response.")
                return True

            else:
                test.log.error(f"Expect {expect_pb} does not exist in response")
                return False
        else:
            test.log.error(f"No item is read from pb.")
            return False

    def check_slcc_and_clcc(test, expect_status, number, alpha, is_mo=True):
        test.expect(test.dut.dstl_check_slcc_binary(is_mo=is_mo, expect_status=expect_status, number=number, type="(129|145|161)", alpha=alpha))
        test.expect(test.dut.dstl_check_clcc_binary(is_mo=is_mo, expect_status=expect_status, number=number, type="(129|145|161)", alpha=alpha))

    def call_with_pb_entry(test, call_method, location=None, alpha=None):
        # call_method: 1->ATD>"mem+n";  2->ATD>n; 3->ATD>"alpha";
        if call_method == 1:
            atd_cmd = f"ATD>\"{test.pb_memory}{location}\";"
        elif call_method == 2:
            atd_cmd = f"ATD>{location};"
        elif call_method == 3:
            atd_cmd = f"ATD>\"{alpha}\";"
        else:
            test.log.error(f"Invalid parameter value {call_method} for call_method.") 
        test.expect(test.dut.at1.send_and_verify(atd_cmd))
        ring_urc = test.r1.at1.wait_for("RING")
        if not ring_urc:
            i = 1
            while not ring_urc and i < 5:
                test.log.warning(f"No RING URC received from remote module, maybe network issue, try the {i+1}th time.")
                test.expect(test.dut.at1.send_and_verify(atd_cmd))
                ring_urc = test.r1.at1.wait_for("RING")
                i += 1
        test.expect(ring_urc, msg="No RING URC received from R1.")

    def call_with_memory_location(test, location):
        test.call_with_pb_entry(1, location)
    
    def call_with_location(test, location):
        test.call_with_pb_entry(2, location)
    
    def call_with_alpha(test, alpha):
        test.call_with_pb_entry(3, alpha=alpha)


if "__main__" == __name__:
    unicorn.main()