#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0093128.002,TC0093147.002,TC0093150.002

import unicorn
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

    Intention:
    This test is provided to verify the functionality of Direct Dialling from Phone books with a concrete syntax (3GPP TS 27.007).
    ATD>mem"n"[;]  - MO Voice and Data, Fax Call if supported.
    Subscriber: 2
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(3)
        test.dut.dstl_register_to_network()
        test.r1.dstl_register_to_network()
        test.sleep(2)
        test.r1_nat_num = test.r1.sim.nat_voice_nr
        test.r1_int_num = test.r1.sim.int_voice_nr
        test.dut.nat_num = test.dut.sim.nat_voice_nr

    def run(test):
        type_mo = ['129', '145', '161']

        test.log.step('0. initialization')
        test.expect(test.dut.at1.send_and_verify("AT^SLCC=1", "O"))
        test.expect(test.dut.at1.send_and_verify(" AT+CLIP=1", "O"))
        test.expect(test.dut.dstl_clear_select_pb_storage(test.pb_memory))

        for type_n in type_mo:
            test.atd_pb_mem_index_check(type_n, 'GSM')
        for type_n in type_mo:
            test.atd_pb_mem_index_check(type_n, 'UCS2')

        test.log.step('4.Restore the DUT to the default settings by sending at&f and '
                      'clearing all phone books.')
        test.expect(test.dut.at1.send_and_verify('at&f'))
        test.expect(test.dut.dstl_clear_all_pb_storage())

    def cleanup(test):
        test.expect(test.dut.dstl_set_character_set('GSM'))

    def convert_char_ucs2(test, text ,charset):
        if charset == 'GSM':
            return text
        elif charset =='UCS2':
            return test.dut.dstl_convert_to_ucs2(text)

    def atd_pb_mem_index_check(test, type_n, charset):

        if type_n == '145':
            write_number = test.r1_int_num
            read_number = '\\'+test.r1_int_num
        else:
            write_number = test.r1_nat_num
            read_number = test.r1_nat_num
        test.expect(test.dut.dstl_set_character_set(charset))
        sm_max = test.dut.dstl_get_pb_storage_max_location(test.pb_memory)
        test_index = sm_max//2
        test_text = test.convert_char_ucs2('Remote1',charset)

        test.log.step('1.a Dial and disconnect MO Call from SM storage when only one entry')
        test.expect(test.dut.dstl_set_pb_memory_storage(test.pb_memory))
        test.expect(test.dut.dstl_write_pb_entries(test_index,write_number,type_n,test_text))
        test.dut.dstl_mo_call_by_mem_index(test.pb_memory, test_index)
        test.expect(test.r1.at1.wait_for('RING'))
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify("AT+CLCC", f'CLCC: 1,0,3,0,0,"{read_number}"'))
        test.dut.dstl_release_call()
        test.r1.dstl_release_call()
        test.sleep(2)
        test.log.step('1.b Dial from AUX ATD"DUT number"[;] and disconnect from AUX')
        test.r1.dstl_voice_call_by_number(test.dut,test.dut.nat_num)
        test.r1.dstl_release_call()
        test.dut.dstl_release_call()
        test.sleep(2)

        test.log.step('2.a Dial and disconnect MO Call from SM storage when all other indexes '
                      'are filled with random content')
        test.expect(test.dut.dstl_fill_selected_pb_memory(test.pb_memory,text=test.convert_char_ucs2('Dummy data',charset)))
        test.expect(test.dut.dstl_write_pb_entries(test_index, write_number, type_n, test_text))
        test.dut.dstl_mo_call_by_mem_index(test.pb_memory, test_index)
        test.expect(test.r1.at1.wait_for('RING'))
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify("AT+CLCC", f'CLCC: 1,0,3,0,0,"{read_number}"'))
        test.dut.dstl_release_call()
        test.r1.dstl_release_call()
        test.sleep(2)

        test.log.step('2.b Dial from AUX ATD"DUT number"[;] and disconnect from AUX')
        test.r1.dstl_voice_call_by_number(test.dut, test.dut.nat_num)
        test.r1.dstl_release_call()
        test.dut.dstl_release_call()
        test.sleep(2)

        test.log.step('3.a Change to other storage and dial and disconnect MO Call from SM storage ')
        test.expect(test.dut.dstl_set_pb_memory_storage('LD'))
        test.dut.dstl_mo_call_by_mem_index(test.pb_memory, test_index)
        test.expect(test.r1.at1.wait_for('RING'))
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify("AT+CLCC", f'CLCC: 1,0,3,0,0,"{read_number}"'))
        test.dut.dstl_release_call()
        test.r1.dstl_release_call()
        test.sleep(2)

        test.log.step('3.b Dial from AUX ATD"DUT number"[;] and disconnect from AUX')
        test.r1.dstl_voice_call_by_number(test.dut, test.dut.nat_num)
        test.r1.dstl_release_call()
        test.dut.dstl_release_call()
        test.sleep(2)


if "__main__" == __name__:
    unicorn.main()
