# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0087920.001,TC0087921.001,TC0087923.001

import unicorn
from core.basetest import BaseTest
from dstl.phonebook import phonebook_handle
from dstl.auxiliary import init
from dstl.network_service import register_to_network
import re


class Test(BaseTest):
    '''
    TC0087920.001,TC0087921.001,TC0087923.001
    Intention: Checks phonebook actions
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_enter_pin()
        test.sleep(10)

    def run(test):

        test.log.step('1.delete all entries from all phonebook')
        test.dut.dstl_clear_all_pb_storage()

        test.log.step(f'2.set phonebook memory to {test.pb_storage}')
        test.expect(test.dut.dstl_set_pb_memory_storage(test.pb_storage))

        test.log.step('3.check how many entries are supported')
        max_loc = test.dut.dstl_get_pb_storage_max_location(test.pb_storage)

        test.log.step('4.try to select a not existing phonebook')
        test.expect(test.dut.at1.send_and_verify('AT+CPBS=\"AA\"', 'ERROR'))

        test.log.step(f'5.check if {test.pb_storage} entry still exist')
        test.expect(test.dut.at1.send_and_verify('AT+CPBS?', f'CPBS:.*{test.pb_storage}.*'))

        test.log.step('6.check if syntax of test command (AT+CPBW=?) is in accordance with the specification')
        test.expect(test.dut.at1.send_and_verify('AT+CPBW=?', 'CPBW: \\(1-\\d+\\),\\d+,\\(.*\\),\\d+.*OK.*'))

        test.log.step(f'7.write one entry into the {test.pb_storage} phonebook with location number 0')
        test.expect(test.dut.at1.send_and_verify('AT+CPBW=0,\"123456\",129,\"aaaa\"', 'ERROR'))

        test.log.step(f'8.write all entries into the {test.pb_storage} phonebook')
        test.expect(test.dut.dstl_fill_selected_pb_memory(test.pb_storage))

        test.log.step(f'9.try to write one more entry into the {test.pb_storage} phonebook as allowed')
        test.expect(test.dut.at1.send_and_verify(f'at+cpbw={int(max_loc) + 1},"0",,"abcde"', 'ERROR'))

        test.log.step('10. check how many phonebook entries are supported')
        test.expect(test.dut.at1.send_and_verify('at+cpbr=?', f'CPBR: \\(1-{max_loc}\\).*OK.*'))

        test.log.step(f'11. read {test.pb_storage} phonebook (AT+CPBR=1, x x=Maximum location number)')
        test.expect(test.dut.at1.send_and_verify(f'at+cpbr=1,{max_loc}', 'OK',timeout=60))
        resp = test.dut.at1.last_response
        none_empty_list =re.findall('CPBR: (\d+),',resp)
        if len(none_empty_list) == int(max_loc):
            test.log.info('Pass,entry count match')
            test.expect(True)
        else:
            test.log.error('Error,entry count not match')
            test.expect(False)

        test.log.step(f'12. try to read {test.pb_storage} phonebook with maximum location number +1 more as allowed')
        test.expect(test.dut.at1.send_and_verify(f'at+cpbr={int(max_loc) + 1}', 'ERROR'))

        test.log.step('13.try to read entries from the phonebook with the first value greater than the second')
        test.expect(test.dut.at1.send_and_verify(f'at+cpbr={int(max_loc) + 1},1', 'ERROR'))

        test.log.step('14.delete the entries one by one with AT+CPBW=index command')
        test.expect(test.dut.dstl_clear_select_pb_storage(test.pb_storage))


    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
