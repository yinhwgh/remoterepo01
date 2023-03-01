#responsible: yandong.wu@thalesgroup.com;xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0093132.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.phonebook import phonebook_handle
from dstl.call import setup_voice_call
from dstl.configuration import character_set
from dstl.auxiliary.generate_data import dstl_generate_data


class Test(BaseTest):
    '''
           TC0093132.001 - AtdPbIdx_LD
           Intention: This test is provided to verify the functionality of Direct Dialling from Phone books with a concrete syntax (3GPP TS 27.007).
                      Storage set to LD. ATD>"n"[;]  - MO Voice and Data, Fax Call if supported.
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

    def run(test):
        types_mo = ['129', '145', '161']
        test.log.step('0. initialization')
        test.dut.dstl_clear_all_pb_storage()
        test.dut.at1.send_and_verify("AT^SLCC=1", "OK")
        test.log.step('1. Test different type with GSM charset')
        for types in types_mo:
            test.atd_pb_idx_ld(1, types, 'GSM')
        test.log.step('2. Test different type with UCS2 charset')
        for types in types_mo:
            test.atd_pb_idx_ld(2, types, 'UCS2')

    def cleanup(test):
        test.expect(test.dut.dstl_set_character_set('GSM'))
        test.dut.dstl_clear_all_pb_storage()
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK"))

    def convert_char_ucs2(test, text ,charset):
        if charset == 'GSM':
            return text
        elif charset =='UCS2':
            return test.dut.dstl_convert_to_ucs2(text)

    def atd_pb_idx_ld(test, i, type_n, charset):
        if type_n == '145':
            write_number = test.r1_int_num
            read_number = '\\' + test.r1_int_num
        else:
            write_number = test.r1_nat_num
            read_number = test.r1_nat_num
        test.expect(test.dut.dstl_set_character_set(charset))
        test.log.info(f'Set type as {type_n}')
        test.log.step(f'{i}.1 Write a record in SM pb.')
        mem_max_location = test.dut.dstl_get_pb_storage_max_location('SM')
        test_index = mem_max_location // 2
        test_text = dstl_generate_data(10)
        test.expect(test.dut.dstl_set_pb_memory_storage('SM'))
        test.expect(test.dut.dstl_write_pb_entries(test_index, write_number, type=129,
                            text=f'{test.convert_char_ucs2(test_text, charset)}'))

        test.log.step(f'{i}.2 Set up call to remote 1.')
        test.dut.at1.send_and_verify(f'atd{write_number};')
        test.expect(test.r1.at1.wait_for('RING'))
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify('at+clcc', f'1,0,3,0,0,"{read_number}",.*'))
        test.sleep(2)
        test.dut.dstl_release_call()
        test.r1.dstl_release_call()
        test.sleep(2)
        test.dut.dstl_delete_pb_entry(test_index)
        test.log.step(f'{i}.3 Set up call from LD by atd>1;.')
        test.expect(test.dut.dstl_set_pb_memory_storage('LD'))
        test.dut.at1.send_and_verify(f'atd>1;')
        test.expect(test.r1.at1.wait_for('RING'))
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify('at+clcc', f'1,0,3,0,0,"{read_number}",.*'))
        test.sleep(2)
        test.dut.dstl_release_call()


if '__main__' == __name__:
    unicorn.main()
