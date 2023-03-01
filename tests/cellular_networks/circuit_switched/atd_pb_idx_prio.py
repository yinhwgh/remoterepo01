# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0093145.001,TC0093144.001,TC0093142.001

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
    ATD>"n"[;]  - MO Voice and Data, Fax Call if supported.
    Subscriber: 2
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(3)
        test.dut.dstl_register_to_network()
        test.r1.dstl_restart()
        test.sleep(3)
        test.r1.dstl_register_to_network()
        test.sleep(5)
        test.r1_nat_num = test.r1.sim.nat_voice_nr
        test.r1_int_num = test.r1.sim.int_voice_nr

    def run(test):
        type_mo = ['129', '145', '161']
        memlist = ['SM', 'ME', 'ON', 'FD']

        if 'ME'  not in test.dut.dstl_get_supported_pb_memory_list():
            memlist = ['SM', 'ON', 'FD']

        test.log.step('0. initialization DUT and AUX')
        test.expect(test.dut.at1.send_and_verify("AT^SLCC=1", "OK"))
        test.expect(test.dut.at1.send_and_verify(" AT+CLIP=1", "OK"))
        test.expect(test.r1.at1.send_and_verify("AT^SLCC=1", "OK"))
        test.expect(test.r1.at1.send_and_verify(" AT+CLIP=1", "OK"))
        for type_n in type_mo:
            test.atd_pb_index_check(type_n, memlist, 'GSM')
            test.atd_pb_index_check(type_n, memlist, 'UCS2')

    def cleanup(test):
        test.log.step('5. clearing all phone books')
        test.expect(test.dut.dstl_set_character_set('GSM'))
        test.expect(test.dut.dstl_clear_all_pb_storage())

    def convert_char_ucs2(test, text ,charset):
        if charset == 'GSM':
            return text
        elif charset =='UCS2':
            return test.dut.dstl_convert_to_ucs2(text)


    def atd_pb_index_check(test, type_n, mem_list, charset):
        if type_n == '145':
            write_number = test.r1_int_num
            read_number = '\\'+test.r1_int_num
        else:
            write_number = test.r1_nat_num
            read_number = test.r1_nat_num

        test.expect(test.dut.dstl_set_character_set(charset))
        test.log.step('1.1 DUT create the same entry in SM, ME, FD, ON memory with one exception "text" is different.')
        for mem in mem_list:
            test.expect(test.dut.dstl_set_pb_memory_storage(mem))
            test.expect(test.dut.dstl_write_pb_entries(1, write_number, type=type_n, text=test.convert_char_ucs2(mem,charset)))

        test.log.step('1.2 DUT performs a call from PB and check if PB entry is taken.')
        test.expect(test.dut.dstl_set_pb_memory_storage(test.pb_memory))
        test.dut.at1.send_and_verify('atd>1;')

        test.log.step('1.3 AUX detects an incoming call and terminate it.')
        test.r1.at1.wait_for('RING')
        test.dut.at1.send_and_verify('at+clcc',f'1,0,3,0,0,"{read_number}",.*')
        test.sleep(3)
        test.r1.dstl_release_call()

        test.expect(test.dut.dstl_set_pb_memory_storage('LD'))
        test.expect(test.dut.at1.send_and_verify('at+cpbr=1',f'CPBR: 1,"{read_number}",{type_n},"{test.convert_char_ucs2(test.pb_memory,charset)}".*'))

        test.log.step(
            '2.1 DUT create the same entry in SM, ME, FD, ON memory with one exception "number" is different.')
        for mem in mem_list:
            test.expect(test.dut.dstl_set_pb_memory_storage(mem))
            if mem == test.pb_memory:
                test.expect(test.dut.dstl_write_pb_entries(1, write_number, type=type_n, text=test.convert_char_ucs2('dummy',charset)))
            else:
                test.expect(test.dut.dstl_write_pb_entries(1, '1234567890', type=type_n, text=test.convert_char_ucs2('dummy',charset)))

        test.log.step('2.2 DUT performs a call from PB and check if PB entry is taken.')
        test.expect(test.dut.dstl_set_pb_memory_storage(test.pb_memory))
        test.dut.at1.send_and_verify('atd>1;')

        test.log.step('2.3 AUX detects an incoming call and terminate it.')
        test.r1.at1.wait_for('RING')
        test.dut.at1.send_and_verify('at+clcc',f'1,0,3,0,0,"{read_number}",.*')
        test.sleep(3)
        test.r1.dstl_release_call()

        test.expect(test.dut.dstl_set_pb_memory_storage('LD'))
        test.expect(test.dut.at1.send_and_verify('at+cpbr=1','CPBR: 1,\\"{}\\",{},"{}".*'.format(read_number,type_n,test.convert_char_ucs2('dummy',charset))))

        test.log.step(
            f'3.1 DUT creates double entry in {test.pb_memory} memory with one exception "location" is different.')
        test.expect(test.dut.dstl_set_pb_memory_storage(test.pb_memory))
        test.expect(test.dut.dstl_write_pb_entries(1, write_number, type=type_n, text=test.convert_char_ucs2('location1',charset)))
        test.expect(test.dut.dstl_write_pb_entries(2, write_number, type=type_n, text=test.convert_char_ucs2('location2',charset)))

        test.log.step('3.2 DUT performs a call from PB and check if correct entry is taken.')
        test.expect(test.dut.dstl_set_pb_memory_storage(test.pb_memory))
        test.dut.at1.send_and_verify('atd>2;')

        test.log.step('3.3 AUX detects an incoming call and terminate it.')
        test.r1.at1.wait_for('RING')
        test.dut.at1.send_and_verify('at+clcc',f'1,0,3,0,0,"{read_number}",.*')
        test.sleep(3)
        test.r1.dstl_release_call()

        test.expect(test.dut.dstl_set_pb_memory_storage('LD'))
        test.expect(test.dut.at1.send_and_verify('at+cpbr=1','CPBR: 1,"{}",{},"{}".*'.format(read_number,type_n,test.convert_char_ucs2('location2',charset))))

        test.log.step('4. Restore the DUT to the default settings by sending at&f.')
        test.expect(test.dut.at1.send_and_verify('at&f'))


if "__main__" == __name__:
    unicorn.main()
