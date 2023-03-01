# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0093177.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.phonebook import phonebook_handle
from dstl.call import setup_voice_call
import re


class Test(BaseTest):
    '''
    TC0093177.001 - AtdPbEmptyStorages
    Intention:
    This test is provided to verify the functionality of Direct Dialling from Phone books with a concrete syntax (3GPP TS 27.007).
    ATD>"mem""n"[;]  - MO Voice and Data, Fax Call if supported.
    Doesn't exist any entry in phone book and error is expected after attempt of call.
    Subscriber: 2
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(10)
        test.dut.dstl_register_to_network()
        test.r1.dstl_restart()
        test.sleep(10)
        test.r1.dstl_register_to_network()
        test.sleep(5)
        test.r1_phone_num = test.r1.sim.nat_voice_nr

    def run(test):

        test.log.info('0. Clear all PB storages')
        test.dut.dstl_clear_all_pb_storage()

        test.log.info('1.Try to call from empty storage. Do this step for all supported storages')

        support_list = test.dut.dstl_get_supported_pb_memory_list()
        test.log.info('Supported phonebook storage :'.format(support_list))
        for storage in support_list:
            if re.search('SN|LD|EC|SD|MC|DC|EN', str(storage)):
                continue
            else:
                test.func_test(storage, support_list.index(storage) + 1)

        test.log.info('2. Restore the DUT to the default settings by sending at&f and clearing all phone books')
        test.dut.at1.send_and_verify('AT&F', 'OK')
        test.dut.dstl_clear_all_pb_storage()

    def cleanup(test):
        test.log.info('***Test End, clean up***')
        test.expect(test.dut.dstl_set_pb_memory_storage('SM'))

    def func_test(test, pb_storage, index):
        test.log.info('2.{} Start test {} storage'.format(index, pb_storage))
        test.log.info('*** a.Test voice call ***')
        test.dut.at1.send_and_verify('at^sm20=0', 'O')
        test.expect(test.dut.dstl_mo_call_by_mem_index(pb_storage, 1, expect_result='ERROR|NO CARRIER|NO DIALTONE'))
        test.dut.at1.send_and_verify('ath', 'OK')
        test.r1.at1.send_and_verify('ath', 'OK')

        if test.dut.dstl_is_data_call_supported():
            test.log.info('*** b.Test data call ***')
            test.log.info('*** Deactivating CLIR service for DUT and AUX ***')
            test.expect(test.dut.dstl_mo_call_by_mem_index(pb_storage, 1, expect_result='ERROR|NO CARRIER', data=True))
            test.dut.at1.send('+++', end='')
            test.r1.at1.send('+++', end='')


if "__main__" == __name__:
    unicorn.main()
