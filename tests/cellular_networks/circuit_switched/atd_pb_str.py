# responsible: xiaolin.liu@thalesgroup.com
# location: Dalian
# TC0093165.001,TC0093167.001,TC0093164.001

import unicorn
from core import dstl
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.phonebook import phonebook_handle
from dstl.call import setup_voice_call
import re
from dstl.configuration import character_set


class Test(BaseTest):
    '''
    TC0093165.001
    TC0093167.001
    TC0093164.001

    Intention:
    This test is provided to verify the functionality of Direct Dialling from Phone books with a concrete syntax (3GPP TS 27.007).
Storage set to ON,SM,ME. ATD>"str"[;]  - MO Voice and Data, Fax Call if supported.
    Subscriber: 2
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.dut.dstl_restart()
        test.dut.dstl_register_to_network()
        test.r1.dstl_restart()
        test.r1.dstl_register_to_network()
        test.sleep(5)
        test.r1_nat_num = test.r1.sim.nat_voice_nr
        test.r1_int_num = test.r1.sim.int_voice_nr


    def run(test):
        types_mo = ['129', '145', '161']
        call_types = ["Voice", "Data", "Fax"]
        dut_data_call = test.dut.dstl_is_data_call_supported()
        dut_fax_call = test.dut.dstl_is_fax_call_supported()
        r1_data_call = test.r1.dstl_is_data_call_supported()
        r1_fax_call = test.r1.dstl_is_fax_call_supported()
        test.log.step('0. initialization and set memory storage')
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
        test.expect(test.dut.at1.send_and_verify("AT^SLCC=1", "OK"))
        test.expect(test.dut.at1.send_and_verify(" AT+CLIP=1", "OK"))
        test.r1.at1.send_and_verify("AT^SLCC=1", "O")
        test.r1.at1.send_and_verify(" AT+CLIP=1", "O")
        test.expect(test.dut.dstl_set_pb_memory_storage(test.pb_memory))

        test.log.step('1. Verify only one entry exist, calling success.')
        for type_n in types_mo:
            test.atd_pb_str_check(1,type_n, 'GSM')
            test.atd_pb_str_check(1,type_n, 'UCS2')

        mem_max_location = test.dut.dstl_get_pb_storage_max_location(test.pb_memory)
        test.log.step(f'2. Writting {mem_max_location} times,verify fill all PB SM entries, calling success.')
        test.log.step( f'2.0 Writting {mem_max_location} times, fill all PB entries.')
        test.dut.dstl_restart()
        test.dut.dstl_register_to_network()
        test.attempt(test.dut.at1.send_and_verify, "AT+CPBS?", timeout=90, retry=30)
        test.expect(test.dut.dstl_set_pb_memory_storage(test.pb_memory))
        charset = 'GSM'
        for idx in range(1,mem_max_location+1):
            test.expect(test.dut.dstl_write_pb_entries(idx,idx,type=129,text=f'{test.convert_char_ucs2(f"{test.pb_memory}.{idx}",charset)}'))
        for type_n in types_mo:
            test.atd_pb_str_check(2,type_n, 'GSM')
            test.atd_pb_str_check(2,type_n, 'UCS2')

    def cleanup(test):
        test.log.step('3. clearing all entries')
        test.expect(test.dut.dstl_set_character_set('GSM'))
        test.expect(test.dut.dstl_clear_select_pb_storage(test.pb_memory))

    def convert_char_ucs2(test, text ,charset):
        if charset == 'GSM':
            return text
        elif charset =='UCS2':
            return test.dut.dstl_convert_to_ucs2(text)


    def atd_pb_str_check(test, i,type_n, charset):
        if type_n == '145':
            write_number = test.r1_int_num
            read_number = '\\'+test.r1_int_num
        else:
            write_number = test.r1_nat_num
            read_number = test.r1_nat_num
        test.expect(test.dut.dstl_set_character_set(charset))

        test.log.step(f'{i}.1 DUT create an entry in {test.pb_memory}.')
        test.expect(test.dut.dstl_write_pb_entries(i, write_number, type=type_n, text=test.convert_char_ucs2(f"{test.pb_memory}.{i}",charset)))

        test.log.step(f'{i}.2 DUT performs a call from PB and check if PB entry is taken.')
        test.dut.at1.send_and_verify(f'atd>"{test.convert_char_ucs2(f"{test.pb_memory}.{i}",charset)}";')

        test.log.step(f'{i}.3 AUX detects an incoming call and terminate it.')
        test.r1.at1.wait_for('RING')
        test.dut.at1.send_and_verify('at+clcc',f'1,0,3,0,0,"{read_number}",.*')
        test.sleep(3)
        test.r1.dstl_release_call()

        test.expect(test.dut.dstl_set_pb_memory_storage('LD'))
        test.expect(test.dut.at1.send_and_verify('at+cpbr=1',f'CPBR: 1,"{read_number}",{type_n},"{test.convert_char_ucs2(f"{test.pb_memory}.{i}",charset)}".*'))
        test.expect(test.dut.dstl_set_pb_memory_storage(test.pb_memory))



if "__main__" == __name__:
    unicorn.main()
