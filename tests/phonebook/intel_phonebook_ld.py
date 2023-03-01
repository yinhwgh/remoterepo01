# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0087922.001

import unicorn
from core.basetest import BaseTest
from dstl.phonebook import phonebook_handle
from dstl.auxiliary import init
from dstl.network_service import register_to_network
import re
from dstl.call import setup_voice_call
import random


class Test(BaseTest):
    '''
    TC0087922.001 - IntelPhonebookLd
    Intention: Check functions with LD phonebook.
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_enter_pin()
        test.sleep(10)

    def run(test):

        test.log.step('1.delete all entries from all phonebook')
        test.dut.dstl_clear_all_pb_storage()

        test.log.step('2.set phonebook memory to LD')
        test.expect(test.dut.dstl_set_pb_memory_storage('LD'))

        test.log.step('3.check how many entries are supported,x')
        max_loc = test.dut.dstl_get_pb_storage_max_location('LD')
        max_loc_1 = max_loc+1

        test.log.step('4.set phonebook memory to SM')
        test.expect(test.dut.dstl_set_pb_memory_storage('SM'))

        test.log.step('5. make x+1 entries into SM phonebook filling all supported parameters of AT+CPBW write command')
        for i in range(1, max_loc_1+1):
            test.expect(test.dut.dstl_write_pb_entries(i,i,129,f'testtext{i}'))

        test.log.step('6.set phonebook memory to LD')
        test.expect(test.dut.dstl_set_pb_memory_storage('LD'))

        test.log.step('7.try to select a not existing phonebook')
        test.expect(test.dut.at1.send_and_verify('AT+CPBS=\"AA\"', 'ERROR'))

        test.log.step('8.check if LD entry still exist')
        test.expect(test.dut.at1.send_and_verify('AT+CPBS?', 'CPBS:.*LD.*'))

        test.log.step('9. set up the call to a number from SM phonebook and go on hook,(ATD>SMy;)')
        test.dut.dstl_mo_call_by_mem_index('SM',1)
        test.dut.dstl_release_call()

        test.log.step('10. read each written entry (AT+CPBR=1)')
        test.expect(test.dut.at1.send_and_verify('at+cpbr=1','\+CPBR: 1,\"1\",.*,\"testtext1\".*OK.*'))

        test.log.step('11.repeat this step until fill up all entries (x times)')

        for i in range(2, max_loc_1+1):
            test.log.step('12. set up the call to a number from SM phonebook and go on hook')
            test.dut.dstl_mo_call_by_mem_index('SM', i)
            test.dut.dstl_release_call()

            test.log.step('13. read each written entry (AT+CPBR=1) and the last entry is always the first number in the LD phonebook')
            test.expect(test.dut.at1.send_and_verify('at+cpbr=1', f'CPBR: 1,\"{i}\",.*,\"testtext{i}\".*OK.*'))

        test.log.step('14. set up the call to the number from random chosen entry and goes on hook(e.g. ATD>LD6; entry from LD phonebook)')
        x= random.randint(1, 10)
        test.log.info(f'Random chosen location : LD {x}')
        test.expect(test.dut.at1.send_and_verify(f'at+cpbr={x}', '.*OK.*'))
        resp = test.dut.at1.last_response
        read_number = re.search('CPBR: \d+,"(.*)",129,"(.*)"', resp).group(1)
        read_text = re.search('CPBR: \d+,"(.*)",129,"(.*)"', resp).group(2)
        test.dut.dstl_mo_call_by_mem_index('LD', x)
        test.dut.dstl_release_call()

        test.log.step('15. read each written entry (AT+CPBR=1) and the last entry is always the first number in the LD phonebook;')
        test.expect(test.dut.at1.send_and_verify('at+cpbr=1', f'CPBR: 1,\"{read_number}\",.*,\"{read_text}\".*OK.*'))

        test.log.step('16. check how many phonebook entries are supported (AT+CPBR=?)')
        test.expect(test.dut.at1.send_and_verify('at+cpbr=?', f'CPBR: \\(1-{max_loc}\\).*OK.*'))

        test.log.step('17. read all entries from LD phonebook (AT+CPBR=1,x)')
        test.expect(test.dut.at1.send_and_verify(f'at+cpbr=1,{max_loc}', 'OK', timeout=20))

        test.log.step('18. try to read LD phonebook with maximum location number +1 more than allowed')
        test.expect(test.dut.at1.send_and_verify(f'at+cpbr={max_loc_1}', 'ERROR'))

        test.log.step('19. try to read entries from the phonebook with the first value greater than the second (AT+CPBR=x,1)')
        test.expect(test.dut.at1.send_and_verify(f'at+cpbr={max_loc_1},1', 'ERROR'))

        test.log.step('20. try to delete phonebook entry with AT+CPBW=y')
        for i in range(1,max_loc_1):
            test.expect(test.dut.at1.send_and_verify(f'at+cpbw={max_loc_1}', 'ERROR'))

        test.log.step('21. check if last called number is still on first entry of phonebook with AT+CPBR=1 command')
        test.expect(test.dut.at1.send_and_verify('at+cpbr=1', f'CPBR: 1,\"{read_number}\",.*,\"{read_text}\".*OK.*'))

        test.log.step('22. set phonebook memory to SM (AT+CPBS="SM");delete the entries one by one with AT+CPBW=index command')
        test.expect(test.dut.dstl_clear_select_pb_storage('SM'))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
