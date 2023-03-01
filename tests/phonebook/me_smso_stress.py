#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0009963.001

import unicorn
from core.basetest import BaseTest
from dstl.phonebook import phonebook_handle
from dstl.auxiliary import init
from dstl.network_service import register_to_network
from dstl.auxiliary.devboard import devboard


class Test(BaseTest):
    '''
    TC0009963.001 - MeStressSmso
    Equipment: MCtest3
    Execution effort average : 449min
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_enter_pin()
        test.sleep(5)

    def run(test):
        if 'ME' in test.dut.dstl_get_supported_pb_memory_list():
            for i in range(1000):
                test.log.info('************** Loop {} Start ************'.format(i + 1))
                max = test.dut.dstl_get_pb_storage_max_location('ME')
                test.log.step('1.Fill out the whole phonebook with "AT+CPBW" command.')
                test.expect(test.dut.dstl_fill_selected_pb_memory('ME'))

                test.log.step('2.Write max+1 entries in the phonebook ')
                test.expect(test.dut.dstl_write_pb_entries(max + 1, '12345678') == False)

                test.log.step('3.Read out the entries of the phonebook with "AT+CPBR" command.')
                test.expect(test.dut.at1.send_and_verify('at+cpbr=1,{}'.format(max)))

                test.log.step('4.Switch off the module with "SMSO" command.')
                test.expect(test.dut.devboard.send_and_verify('mc:ver','OK'))
                test.expect(test.dut.at1.send_and_verify('at^smso', 'OK'))
                test.sleep(5)
                test.expect(test.dut.dstl_check_if_module_is_on_via_dev_board() == False)

                test.log.step('5.Switch on the module.')
                test.expect(test.dut.dstl_turn_on_igt_via_dev_board(igt_time=4000))
                test.sleep(5)

                test.log.step('6.Insert PIN.')
                test.dut.dstl_enter_pin()
                test.sleep(10)

                test.log.step('7.Read out the entries of the phonebook with "AT+CPBR" command.')
                test.expect(test.dut.dstl_set_pb_memory_storage('ME'))
                test.expect(test.dut.at1.send_and_verify('at+cpbr=1,{}'.format(max)))
                test.sleep(3)

                test.log.info('************** Loop {} End *************'.format(i + 1))

        else:
            test.log.info('The project not support ME phonebook, test finish')

    def cleanup(test):
        test.log.step('9.Delete all entries with "AT+CPBW".')
        test.dut.dstl_clear_select_pb_storage('ME')
        pass


if "__main__" == __name__:
    unicorn.main()
