# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0091846.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.phonebook import phonebook_handle


class Test(BaseTest):
    """
    TC0091846.001 - TpAtDStrAndAtChupBasic
    Intention: This procedure provides basic tests for the test and write command of ATD<str>.
    Subscriber: 2
    """

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(10)
        test.r1.dstl_restart()
        test.sleep(10)
        test.r1.dstl_register_to_network()
        test.r1_phone_num = test.r1.sim.nat_voice_nr
        test.r1_phone_num_regexpr = test.r1_phone_num
        if test.r1_phone_num_regexpr.startswith('0'):
            test.r1_phone_num_regexpr = '.*' + test.r1_phone_num_regexpr[1:]
        pass

    def run(test):
        test.log.info('***Test Start***')

        test.log.info('1. test without pin ')
        test.expect(test.dut.at1.send_and_verify('at+cpin?', 'SIM PIN'))
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+cmee?', 'CMEE: 2'))
        test.expect(test.dut.at1.send_and_verify('atd>"abc";', 'ERROR|NO DIALTONE|NO CARRIER',
                                                 wait_for='ERROR|NO DIALTONE|NO CARRIER'))

        test.log.info('2. test with pin')
        test.dut.dstl_register_to_network()
        test.sleep(5)
        test.attempt(test.dut.at1.send_and_verify, "at+cpbw=?", retry=5, sleep=5)

        test.log.info('3. Function check start')
        test.log.info('*** Delete all pb entries ***')
        test.dut.dstl_clear_all_pb_storage()
        test_pb = ['SM', 'ON', 'ME', 'FD']
        support_list = test.dut.dstl_get_supported_pb_memory_list()
        for i in range(4):
            if test_pb[i] in support_list:
                test.func_test(test_pb[i], i + 1)
                test.clear_pb(test_pb[i], i + 1)
            else:
                test.log.info('3.{} The product not support {} storage, skipped'.format(i, test_pb[i]))

        test.log.info('4. invalid parameter test')
        test.expect(test.dut.at1.send_and_verify('atd>\"ddd ddd\";', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('atd>\"ddd d-d-d\";', 'ERROR'))
        pass

    def cleanup(test):
        test.log.info('***Test End, clean up***')
        test.expect(test.dut.dstl_set_pb_memory_storage('SM'))
        pass

    def func_test(test, pb_storage, index):
        test.log.info('3.{} Start test {} storage'.format(index, pb_storage))
        test.expect(test.dut.dstl_set_pb_memory_storage(pb_storage))
        if pb_storage != 'LD':
            test.expect(test.dut.dstl_write_pb_entries(index, test.r1_phone_num, 129, pb_storage))
        test.expect(test.dut.at1.send_and_verify('atd>\"{}\";'.format(pb_storage), '', wait_for=''))
        test.r1.at1.wait_for('RING')
        test.sleep(2)
        test.expect(test.r1.at1.send_and_verify('ata'))
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify('at+cimi', '.*\d{15}.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+clcc', f'.*CLCC: 1,0,0,0,0,\"{test.r1_phone_num_regexpr}\".*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+chup'))
        pass

    def clear_pb(test, pb_storage, index):
        test.expect(test.dut.dstl_set_pb_memory_storage(pb_storage))
        test.expect(test.dut.dstl_delete_pb_entry(index))
        pass


if "__main__" == __name__:
    unicorn.main()
