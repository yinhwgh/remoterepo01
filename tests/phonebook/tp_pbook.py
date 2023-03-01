# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0091704.001

import unicorn
from core.basetest import BaseTest
from dstl.phonebook import phonebook_handle
from dstl.auxiliary import init
from dstl.network_service import register_to_network


class Test(BaseTest):
    '''
    TC0091704.001 - TpPbook
    Intention: Checks phonebook actions
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_enter_pin()
        test.sleep(10)
        test.check_memory= 'SM'

    def run(test):
        max_loc = test.dut.dstl_get_pb_storage_max_location(test.check_memory)
        max_num_len = test.dut.dstl_get_pb_storage_max_number_length(test.check_memory)
        max_text_len = test.dut.dstl_get_pb_storage_max_text_length(test.check_memory)

        test.log.info('1.Clear select memory')
        test.expect(test.dut.dstl_clear_select_pb_storage(test.check_memory))
        test.expect(test.dut.at1.send_and_verify('at+cpbw=0','ERROR'))
        test.expect(test.dut.at1.send_and_verify(f'at+cpbw={int(max_loc)+1}', 'ERROR'))

        test.log.info('2.1 check length of number')
        test.expect(test.dut.dstl_set_pb_memory_storage(test.check_memory))
        for i in range(0,max_num_len+1):
            test.expect(test.dut.at1.send_and_verify('at+cpbw=1,"{}",,"{}"'.format('1'*i,i), 'OK'))
            test.expect(test.dut.at1.send_and_verify('at+cpbr=1','CPBR: 1,"{}",.*"{}".*OK'.format('1'*i,i)))
        test.expect(test.dut.at1.send_and_verify('at+cpbw=1,"{}",,"aaa"'.format('a' * (max_num_len+1)), 'ERROR'))


        test.log.info('2.2 check length of text')
        for i in range(0,max_text_len+1):
            test.expect(test.dut.at1.send_and_verify('at+cpbw={},"{}",,"{}"'.format(i+1,i,'a'*i), 'OK'))
            test.expect(test.dut.at1.send_and_verify('at+cpbr={}'.format(i+1),'CPBR: {},"{}",.*"{}".*OK'.format(i+1,i,'a'*i)))
        test.expect(test.dut.at1.send_and_verify('at+cpbw=1,"1234",,"{}"'.format('a' * (max_text_len+1)), 'ERROR'))


        test.log.info('2.3 check length of memory')
        test.expect(test.dut.at1.send_and_verify('at+cpbw=0,"0",,"abc"', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify(f'at+cpbw={max_loc},"0",,"abcd"', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'at+cpbw={int(max_loc) + 1},"0",,"abcde"', 'ERROR'))

        test.log.info('3. Fill memory')
        test.expect(test.dut.dstl_fill_selected_pb_memory(test.check_memory))

        test.log.info('4. Clear memory')
        test.expect(test.dut.dstl_clear_select_pb_storage(test.check_memory))

        test.log.info('5. Run special PB commands')
        test.expect(test.dut.at1.send_and_verify('at+cnum', 'OK'))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
