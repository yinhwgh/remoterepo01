# responsible: lei.chen@thalesgroup.com
# location: Dalian
# TC0093172.001, TC0093174.001, TC0093175.001, TC0093156.001, TC0093158.001, TC0093159.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.phonebook import phonebook_handle
from dstl.call import setup_voice_call
from dstl.call import extended_list_of_calls
from dstl.configuration import character_set
from dstl.phonebook import phonebook_priority
from dstl.supplementary_services import lock_unlock_facility

import random, re

class Test(BaseTest):
    '''
    TC0093172.001 - AtdPbStrPrio_FD
    TC0093174.001 - AtdPbStrPrio_ON
    TC0093175.001 - AtdPbStrPrio_SM

    TC0093156.001 - AtdPbMemIdxPrio_FD
    TC0093158.001, TC0093158.002 - AtdPbMemIdxPrio_ON
    TC0093159.001 - AtdPbMemIdxPrio_SM

    Intention:
    This test is provided to verify the functionality of Direct Dialling from Phone books with a concrete syntax (3GPP TS 27.007).
    Storage set to ON/FD/SM. ATD>"str"[;]/ATD>"mem+index"[;]  - MO and MT Voice and Data, Fax Call if supported.
    Subscriber: 2
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_register_to_network()
        test.r1.dstl_detect()
        test.r1.dstl_register_to_network()
    
    def run(test):
        test_mem = test.pb_mem
        test.log.info("****** Initialize modules  - START ******")
        if test.dut.dstl_is_facility_locked(facility="FD"):
            test.expect(test.dut.dstl_lock_unlock_facility(facility="FD", lock=False))
        test.expect(test.dut.at1.send_and_verify("AT+CLIP=1"))
        test.expect(test.dut.at1.send_and_verify("AT+CLIR=2"))
        test.expect(test.dut.dstl_enable_slcc_urc())
        test.expect(test.r1.at1.send_and_verify("AT+CLIR=2"))
        test.expect(test.r1.dstl_enable_slcc_urc())
        dut_data_call = test.dut.dstl_is_data_call_supported()
        dut_fax_call = test.dut.dstl_is_fax_call_supported()
        r1_data_call = test.r1.dstl_is_data_call_supported()
        r1_fax_call = test.r1.dstl_is_fax_call_supported()
        char_sets = test.dut.dstl_get_supported_character_sets()
        call_types = ["Voice", "Data", "Fax"]
        mo_types = ['129', '145', '161']
        aux_mems = ['SM', 'ME', 'FD', 'ON']
        alpha_except_chars = [0,127]
        test.pb_mem_list = test.dut.dstl_get_supported_pb_memory_list()
        max_locs = []
        temp_mems = []
        for mem in aux_mems:
            if mem not in test.pb_mem_list:
                test.log.info(f"DUT does not support {mem}, remove from auxiliary memories {aux_mems}")
            elif mem == "FD" and not test.dut.sim.pin2:
                test.log.info(f"DUT SIM PIN2 is not set, remove FD from auxiliary memories {aux_mems}")
            else:
                temp_mems.append(mem)
                max_loc = test.dut.dstl_get_pb_storage_max_location(mem)
                if isinstance(max_loc, int):
                    max_locs.append(max_loc)
        aux_mems = temp_mems
        # Generate random index based on the minimum max location index of all aux memories. 
        max_loc = min(max_locs)
        random_idx = str(random.randint(1, max_loc))
        
        test.log.h3(f"DUT supports memories {test.pb_mem_list}")
        test.log.h3(f"Final auxilliary memories are {aux_mems}")
        test.log.h3(f"Random index is {random_idx}")
        test.log.h3(f"Loop for types: {mo_types}")
        test.log.h3(f"Loop for call: Voice: True, Data: {dut_data_call}, Fax: {dut_fax_call}")
        test.log.h3(f"Loop for character sets: {char_sets}")
        test.log.info("****** Initialize modules  - END ******")
         
        test.log.info("****** Test Steps  - START ******")
        for mo_type in mo_types:
            test.log.info(f"****** Loop for MO Type {mo_type} ******")
            for call in call_types:
                if call == "Data":
                    if dut_data_call == True:
                        if r1_data_call == True:
                            test.log.error("Data call is not implemented")
                        else:
                            test.log.error(f"Remote module should support data call for tests.")
                    else:
                        test.log.info("DUT does not support Data call, skip step.")
                    continue
                elif call == "Fax":
                    if dut_fax_call == True:
                        if r1_fax_call == True:
                            test.log.error("Fax call is not implemented")
                        else:
                            test.log.error(f"Remote module should support fax call for tests.")
                    else:
                        test.log.info("DUT does not support Fax call, skip step.")
                    continue
                test.log.info(f"****** Tests for {call} call ******")
                for char_set in char_sets:
                    if char_set not in ['GSM','UCS2']:
                        test.log.error(f"Steps are not implemented for {char_set}")
                        continue
                    test.log.step(f"1.1 Number type {mo_type}, {call} call, character set {char_set}: Writing items to {aux_mems} with only verify_text different")
                    test.expect(test.dut.dstl_clear_all_pb_storage())
                    test.log.info(f"****** Character set {char_set} ******")
                    test.expect(test.dut.dstl_set_character_set(char_set))
                    r1_number = test.get_number(call, mo_type, is_dut=False)
                    dut_number = test.get_number(call, "129", is_dut=True)
                    prioritized_mem = test.dut.dstl_get_prioritized_pb_memory(aux_mems, test_mem)
                    test.log.info(f"Tested memory is {test_mem}, prioritized memory is {prioritized_mem}")
                    for mem in aux_mems:
                        max_text_length = test.dut.dstl_get_pb_storage_max_text_length(mem)
                        max_loc = test.dut.dstl_get_pb_storage_max_location(mem)
                        gsm_text, gsm_verify_text, ucs2_text = test.dut.dstl_generate_random_text(max_text_length/2, alpha_except_chars)
                        verify_text = gsm_verify_text if char_set == "GSM" else ucs2_text
                        test.expect(test.dut.dstl_set_pb_memory_storage(mem))
                        test.expect(test.dut.dstl_write_pb_entries(random_idx, r1_number, mo_type, verify_text))
                        if mem == prioritized_mem:
                            clcc_text = verify_text
                        if mem == test_mem:
                            test_mem_text = verify_text
                    test.expect(test.dut.dstl_clear_mc_rc_dc_ld_storage())

                    test.log.step(f"1.2 Number type {mo_type}, {call} call, character set {char_set}: DUT performs a call from PB and check if PB entry is taken. AUX detects an incoming call and terminate it.")
                    test.log.info(f"Current call-from memory is {test_mem}, according to priority list, the number stored in {prioritized_mem} will be used.")
                    test.expect(test.dut.dstl_set_pb_memory_storage(test_mem))
                    test.call_alpha_or_mem_idx(test_mem_text, test_mem, random_idx)
                    test.expect(test.dut.dstl_check_slcc_urc(is_mo=True, expect_status=3, number=r1_number, alpha=clcc_text))
                    test.expect(test.r1.at1.wait_for("RING"))
                    test.expect(test.check_clcc(is_mo=True, expect_status=3, number=r1_number, alpha=clcc_text))
                    test.expect(test.r1.dstl_release_call())
                    test.expect(test.dut.dstl_release_call())
                    test.check_ld_dc_pb(r1_number, mo_type, clcc_text)
                    test.expect(test.dut.dstl_clear_all_pb_storage())
                    test.expect(test.dut.dstl_clear_mc_rc_dc_ld_storage())

                    test.log.step(f"2.1. Number type {mo_type}, {call} call, character set {char_set}: Writing items to {aux_mems} with only number different")
                    max_text_length = test.dut.dstl_get_pb_storage_max_text_length(test_mem)
                    max_number_length = test.dut.dstl_get_pb_storage_max_number_length(test_mem)
                    test.log.info(f"Max number length is {max_number_length}")
                    gsm_text, gsm_verify_text, ucs2_text = test.dut.dstl_generate_random_text(max_text_length/2, alpha_except_chars)
                    verify_text = gsm_text if char_set == "GSM" else ucs2_text
                    text_to_verify = gsm_verify_text if char_set == "GSM" else ucs2_text
                    for mem in aux_mems:
                        if mem == test_mem:
                            number = r1_number
                        else:
                            number = test.get_random_number(max_number_length, mo_type)
                        test.expect(test.dut.dstl_set_pb_memory_storage(mem))
                        test.expect(test.dut.dstl_write_pb_entries(random_idx, number, mo_type, verify_text))

                    test.log.step(f"2.2. Number type {mo_type}, {call} call, character set {char_set}: DUT performs a call from PB and check if PB entry is taken. AUX detects an incoming call and terminate it.")  
                    test.expect(test.dut.dstl_set_pb_memory_storage(test_mem))
                    test.call_alpha_or_mem_idx(text_to_verify, test_mem, random_idx)
                    test.expect(test.dut.dstl_check_slcc_urc(is_mo=True, expect_status=3, number=r1_number, alpha=text_to_verify))
                    test.expect(test.r1.at1.wait_for("RING"))
                    test.expect(test.check_clcc(is_mo=True, expect_status=3, number=r1_number, alpha=text_to_verify))
                    test.expect(test.r1.dstl_release_call())
                    test.expect(test.dut.dstl_release_call())
                    test.check_ld_dc_pb(r1_number, mo_type, text_to_verify)
                    test.expect(test.dut.dstl_clear_all_pb_storage())
                    test.expect(test.dut.dstl_clear_mc_rc_dc_ld_storage())

                    test.log.step(f"3.1. Number type {mo_type}, {call} call, character set {char_set}: A DUT creates double entry in FD memory with one exception \"location\" is different")
                    test.expect(test.dut.dstl_set_pb_memory_storage(test_mem))
                    gsm_text, gsm_verify_text, ucs2_text = test.dut.dstl_generate_random_text(max_text_length/2, alpha_except_chars)
                    verify_text = gsm_text if char_set == "GSM" else ucs2_text
                    text_to_verify = gsm_verify_text if char_set == "GSM" else ucs2_text
                    test.expect(test.dut.dstl_write_pb_entries(random_idx, r1_number, mo_type, verify_text))
                    if int(random_idx) + 1 > max_loc:
                        random_idx_2 = str(int(random_idx) - 1)
                    else:
                        random_idx_2 = str(int(random_idx) + 1)
                    test.expect(test.dut.dstl_write_pb_entries(random_idx_2, r1_number, mo_type, verify_text))

                    test.log.step(f"3.2. Number type {mo_type}, {call} call, character set {char_set}: DUT performs a call from PB and check if correct entry is taken. AUX detects an incoming call and terminate it.")  
                    test.expect(test.dut.dstl_set_pb_memory_storage(test_mem))
                    test.call_alpha_or_mem_idx(text_to_verify, test_mem, random_idx)
                    test.expect(test.dut.dstl_check_slcc_urc(is_mo=True, expect_status=3, number=r1_number, alpha=text_to_verify))
                    test.expect(test.r1.at1.wait_for("RING"))
                    test.expect(test.check_clcc(is_mo=True, expect_status=3, number=r1_number, alpha=text_to_verify))
                    test.expect(test.r1.dstl_release_call())
                    test.expect(test.dut.dstl_release_call())
                    test.check_ld_dc_pb(r1_number, mo_type, text_to_verify)
                    test.expect(test.dut.dstl_clear_mc_rc_dc_ld_storage())
                    
                    # As follow pegasus, skip the following tests for 145, as cannot make MO number display as 145
                    if mo_type != '145':
                        test.log.step(f"3.3. Number type {mo_type}, {call} call, character set {char_set}: Makes DUT MT Call from AUX ATD\"DUT number\"[;] and disconnect from AUX.")  
                        r1_number = "(\+\d{2,3})?" + test.r1.sim.nat_voice_nr
                        test.expect(test.dut.dstl_set_pb_memory_storage(test_mem))
                        test.expect(test.r1.at1.send_and_verify(f"ATD{dut_number};", "OK"))
                        test.expect(test.dut.dstl_check_slcc_urc(is_mo=False, expect_status=4, number=r1_number, alpha=text_to_verify))
                        test.expect(test.dut.at1.wait_for("RING"))
                        test.expect(test.check_clip(number=r1_number, alpha=text_to_verify))
                        test.expect(test.check_clcc(is_mo=False, expect_status=4, number=r1_number, alpha=text_to_verify))
                        test.expect(test.r1.dstl_release_call())
        test.log.info("****** Test Steps  - END ******")

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT&F"))
        test.expect(test.dut.dstl_clear_all_pb_storage())

    def get_number(test, call_type, num_type, is_dut=True):
        """ 
        Number will be read from simdata according to <call_type> (voice, data, fax) and num_type
        """
        if is_dut == True:
            module = "dut"
        else:
            module = "r1"
        if num_type == "145":
            prefix = "int"
        else:
            prefix = "nat"
        aux_number = eval(f"test.{module}.sim.{prefix}_{call_type.lower()}_nr")
        return aux_number
    
    def check_ld_dc_pb(test, number, type, text):
        cpbr_expect = f"+CPBR: 1,\"{number}\",{type},\"{text}\""
        pbs = ["LD", "DC"]
        for pb in pbs:
            if pb in test.pb_mem_list:
                test.expect(test.dut.dstl_set_pb_memory_storage("LD"))
                test.expect(test.dut.at1.send_and_verify("AT+CPBR=1"))
                result = cpbr_expect in test.dut.at1.last_response
                if result == False:
                    test.log.error(f"{cpbr_expect} does not exist in response.")
                else:
                    test.log.info(f"{cpbr_expect} exists in response.")
            else:
                test.log.info(f"{pb} is not in module supported list.")
   
    def get_random_number(test, length, num_type):
        number = ""
        for i in range(0, length-1):
            number += str(random.randint(0,9))
        if num_type == "145":
            number = "+" + number
        else:
            number += str(random.randint(0,9))
        return number

    def check_clcc(test, is_mo, expect_status, number, alpha):
        """
        Because the character in alpha may be key character of regular expressions, verify CLCC in two parts.
        """
        if is_mo == True:
            mode = '0'
        else:
            mode = '1'
        num_type = "(129|161|145)"
        if number.startswith('+'):
            number = number.replace('+','\+')
        clcc_status = test.dut.at1.send_and_verify('at+clcc', f'\+CLCC: 1,{mode},{expect_status},0,0,\"{number}\",{num_type}')
        response = test.dut.at1.last_response
        test.log.info(f"Got last response if {response}")
        if clcc_status == True:
            clcc_part_1 = re.search(f'\+CLCC: 1,{mode},{expect_status},0,0,\"{number}\",{num_type}', response).group(0)
            clcc_part_2 = f',"{alpha}"'
            expect_clcc = clcc_part_1 + clcc_part_2
            result = expect_clcc in response
            if result == True:
                test.log.info(f"Found {expect_clcc} in response.")
                return True
            else:
                test.log.error(f"{expect_clcc} is not in response {response}.")
                return False
        else:
            test.log.error(f"Cannot find +CLCC: 1,{mode},{expect_status},0,0,\"{number}\",{num_type},{alpha} in response.")
            return False

    def check_clip(test, number, alpha):
        """
        Because the character in alpha may be key character of regular expressions, verify CLIP in two parts.
        """
        num_type = '(128|129|145|161|255)'
        if not number.startswith('+'):
            number = "(\+\d{2,3})?" + number
        else:
            number = number.replace('+','\+')
        clip_status = test.dut.at1.wait_for(f"\+CLIP: \"{number}\",{num_type},,,", timeout=15)
        if clip_status:
            response = test.dut.at1.last_response
            clip_part_1 = re.search(f"\+CLIP: \"{number}\",{num_type},,,", response).group(0)
            clip_part_2 = f'"{alpha}",'
            clip_expect = clip_part_1 + clip_part_2
            if clip_expect in response:
                test.log.info(f"Found {clip_expect} in response.")
                return True
            else:
                test.log.error(f"Fail to find {clip_expect} in response.")
                return False
        else:
            test.log.error(f"Fail to find CLIP URC with number {number}, type {num_type} in response.")
            return False
    
    def call_alpha_or_mem_idx(test, alpha, mem, idx):
        if test.call_method == "alpha":
            test.log.info("Calling with ATD>\"alpha\"")
            test.expect(test.dut.at1.send_and_verify(f"ATD>\"{alpha}\";", "OK"))
        elif test.call_method == "mem_idx":
            test.log.info("Calling with ATD>\"memory+index\"")
            test.expect(test.dut.at1.send_and_verify(f"ATD>\"{mem}{idx}\";", "OK"))
        else:
            test.log.error(f"Unsupported call method: \"{test.call_method}\"")
            

            
if "__main__" == __name__:
    unicorn.main()