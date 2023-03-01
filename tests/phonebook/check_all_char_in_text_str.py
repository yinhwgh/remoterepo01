# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0091707.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.call.setup_voice_call import dstl_release_call
from dstl.auxiliary import init
from dstl.network_service import register_to_network
from dstl.configuration.character_set import dstl_convert_to_ucs2, dstl_set_character_set
from dstl.phonebook.phonebook_handle import dstl_clear_all_pb_storage
import random


class Test(BaseTest):
    '''
    TC0091707.001 - TpCheckAllCharactersInTextStr
    Intention: test all chars in <text> of phonebook entry, and convert between GSM and UCS2 charset.
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.dut.dstl_register_to_network()
        test.r1.dstl_detect()
        test.r1.dstl_register_to_network()
        test.sleep(10)
        test.memory = 'SM'
        test.r1_number = test.r1.sim.nat_voice_nr

    def run(test):

        test.log.step('0. clear all PB entry')
        test.dut.dstl_clear_all_pb_storage()
        test.r1.dstl_clear_all_pb_storage()

        test.expect(test.dut.at1.send_and_verify('at^slcc=1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+clip=0', 'OK'))
        max_entry = test.dut.dstl_get_pb_storage_max_location(test.memory)
        gsm_char_set = test.dut.dstl_get_all_gsm_characters()

        for i in range(1, 257):
            test_char = gsm_char_set[i - 1]
            if test_char != "" and test_char != 255:
                test.log.info(f'Loop: {i} of 256 - Start')
                test.check_single_char_in_text(i - 1, max_entry)
                test.log.info(f'Loop: {i} of 256 - End')
            else:
                test.log.info('Loop cancelled, because of unsupported character in UCS-table')

    def cleanup(test):
        test.expect(test.dut.dstl_set_character_set('GSM'))

    def check_single_char_in_text(test, c_index, max):
        test.log.step('1)set to GSM')
        test.expect(test.dut.dstl_set_character_set('GSM'))
        index = random.randint(1, max)

        test.log.step('2)write entry and read')
        write_char = test.dut.dstl_get_character_by_decimal(c_index, 'GSM')
        read_char = write_char
        read_char_ucs2 = test.dut.dstl_get_character_by_decimal(c_index, 'UCS2')

        test.expect(test.dut.dstl_write_pb_entries(index, test.r1_number, '129', write_char))
        if str(read_char).find('\\') >= 0:
            read_char = read_char.replace('\\', '\\\\')
        if str(read_char).find(')') >= 0:
            read_char = read_char.replace(')', '\\)')
        if str(read_char).find('(') >= 0:
            read_char = read_char.replace('(', '\\(')
        if c_index in [36, 43, 91, 94]:
            read_char = '\\' + read_char

        # 127 can't be displayed in Unicorn
        if c_index != 127:
            test.expect(test.dut.at1.send_and_verify(f'at+cpbr={index}',
                                                 f'.*\+CPBR:\s*{index},"{test.r1_number}",129,"{read_char}".*'))
        test.log.step('3)set up voice call by atd>"str";')
        test.dut.at1.send_and_verify(f'atd>"{write_char}";', expect='', wait_for='')
        # 127 can't be displayed in Unicorn
        if c_index != 127:
            test.expect(test.dut.at1.wait_for(f'.*\^SLCC: 1,0,3,0,0,0,"{test.r1_number}",(129|145|128|161),"{read_char}".*'))
            test.expect(test.dut.at1.send_and_verify('at+clcc',
                                                     f'.*\+CLCC: 1,0,3,0,0,"{test.r1_number}",(129|145|128|161),"{read_char}".*'))
        test.expect(test.r1.at1.wait_for('RING'))


        test.log.step('4)release call')
        test.dut.dstl_release_call()
        test.r1.dstl_release_call()

        test.log.step('5)set to UCS2')
        test.expect(test.dut.dstl_set_character_set('UCS2'))
        test.log.step('6)read entry')
        test.expect(test.dut.at1.send_and_verify(f'at+cpbr={index}',
                                                 f'.*\+CPBR:\s*{index},"{test.r1_number}",129,"{read_char_ucs2}".*'))
        test.log.step('7)delete entry')
        test.expect(test.dut.dstl_delete_pb_entry(index))


if "__main__" == __name__:
    unicorn.main()
