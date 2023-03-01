# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0087932.001,TC0087932.002


import unicorn
from core.basetest import BaseTest
from dstl.phonebook import phonebook_handle
from dstl.auxiliary import init
from dstl.network_service import register_to_network
import re


class Test(BaseTest):
    '''
    TC0087932.001 - IntelLengthMax
    Intention: Check the possibility to use maximal length for all parameter of AT+CPBW command.
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_enter_pin()
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify('AT+CMEE=2', 'OK'))

    def run(test):
        test.log.step('0.delete all entries from all phonebook')
        test.dut.dstl_clear_all_pb_storage()
        test_pb = ['SM', 'ON', 'ME', 'FD']
        support_list = test.dut.dstl_get_supported_pb_memory_list()
        for i in range(4):
            if test_pb[i] in support_list:
                test.check_max_length(i+1,test_pb[i])
            else:
                test.log.info('3.{} The product not support {} storage, skipped'.format(i, test_pb[i]))

    def cleanup(test):
        test.expect(test.dut.dstl_set_pb_memory_storage('SM'))

    def check_max_length(test, index, memory):
        test.log.step(f'Start test phonebook memory : {memory}')
        test.expect(test.dut.dstl_set_pb_memory_storage(memory))
        test.log.step(f'{index}.1 check the maximal length for all parameters')
        max_text_len= test.dut.dstl_get_pb_storage_max_text_length(memory)
        max_num_len = test.dut.dstl_get_pb_storage_max_number_length(memory)
        num_1 = '1' * (max_num_len-1)
        num_2 = '1' * max_num_len
        num_3 = '1' * (max_num_len + 1)
        str_1 = 's' * (max_text_len - 1)
        str_2 = 's' * max_text_len
        str_3 = 's' * (max_text_len + 1)

        test.log.step(f'{index}.2 try to write an entry with all parameters one less then maximal length of each parameter')
        test.expect(test.dut.at1.send_and_verify(f'AT+CPBW=1,"{num_1}",129,"{str_1}"','OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CPBR=1', f'CPBR: 1,"{num_1}",129,"{str_1}"'))

        test.log.step(f'{index}.3 try to write an entry with text parameter with maximal length')
        test.expect(test.dut.at1.send_and_verify(f'AT+CPBW=1,"{num_2}",129,"{str_2}"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CPBR=1', f'CPBR: 1,"{num_2}",129,"{str_2}"'))

        test.log.step(f'{index}.4 try to write an entry with number parameter with maximal+1 length')
        test.expect(test.dut.at1.send_and_verify(f'AT+CPBW=1,"{num_3}",129,"{str_2}"', 'CME ERROR: dial string too long'))
        test.expect(test.dut.at1.send_and_verify(f'AT+CPBW=1,"{num_2}",129,"{str_3}"', 'CME ERROR: text string too long'))
        test.expect(test.dut.at1.send_and_verify('AT+CPBR=1', f'.*CPBR: 1,"{num_2}",129,"{str_2}".*OK'))

        test.log.step(f'{index}.5 purge all entries')
        test.expect(test.dut.at1.send_and_verify('AT+CPBW=1', 'OK'))


if "__main__" == __name__:
    unicorn.main()


