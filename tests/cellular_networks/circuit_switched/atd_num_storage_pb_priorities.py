# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0093176.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.phonebook import phonebook_handle
from dstl.call import setup_voice_call
from dstl.auxiliary.generate_data import dstl_generate_data


class Test(BaseTest):
    '''
    TC0093176.001 - AtdNumStoragePbPriorities
    Intention:
    This test is provided to verify the functionality of Direct Dialling with ATD"AUX number" which exists in Phone Book storage.
    Test checked storages priorities according to order SM, ME, FD, ON.
    Subscriber: 2
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()

        test.log.info('0. Initialisation')
        test.expect(test.dut.at1.send_and_verify('AT+CSCS=\"GSM\"'))
        test.expect(test.dut.at1.send_and_verify('AT+CMEE=2'))
        test.dut.dstl_register_to_network()
        test.r1.dstl_register_to_network()
        test.sleep(10)
        test.r1_nat_num = test.r1.sim.nat_voice_nr

    def run(test):
        test_memory = ['SM', 'ME', 'FD', 'ON']
        support_list = test.dut.dstl_get_supported_pb_memory_list()
        test.log.info('0.1 Clear All PB storage')
        test.dut.dstl_clear_all_pb_storage()
        test.log.info('Test following memory :{}'.format(test_memory))
        test.step1to4(test_memory, support_list)

    def cleanup(test):
        test.log.info('***Test End, clean up***')
        test.expect(test.dut.at1.send_and_verify('at&f'))
        test.dut.dstl_clear_all_pb_storage()
        test.expect(test.dut.dstl_set_pb_memory_storage('SM'))

    def step1to4(test, list_t, list_s):
        test.log.info('1.1 Create same entry in SM,ME,FD,ON PB with different text')
        text_list = []
        for item in list_t:
            test.expect(test.dut.dstl_set_pb_memory_storage(item))
            random_text = dstl_generate_data(10)
            test.expect(test.dut.dstl_write_pb_entries(1, test.r1_nat_num, 129, random_text))
            text_list.append(random_text)

        test.log.info('1.2 DUT MO Call by dialing ATD<Aux num>; Check LD,DC')
        test.expect(test.dut.at1.send_and_verify('atd{};'.format(test.r1_nat_num), '', ''))
        test.expect(test.r1.at1.wait_for('RING'))
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('at+clcc',
                                                 '.*CLCC: 1,0,0,0,0,\"{}\".*"{}".*OK.*'.format(test.r1_nat_num,
                                                                                               text_list[0])))
        test.expect(test.dut.at1.send_and_verify('ath'))
        test.expect(test.r1.at1.send_and_verify('ath'))

        test.log.info('1.3 Check LD,DC , delete SM entry')
        if 'LD' in list_s:
            test.expect(test.check_ld_dc('LD', 1, test.r1_nat_num, text_list[0]))
        else:
            test.log.info('Not support LD ,skip')
        if 'DC' in list_s:
            test.expect(test.check_ld_dc('DC', 1, test.r1_nat_num, text_list[0]))
        else:
            test.log.info('Not support DC ,skip')

        test.expect(test.dut.dstl_clear_select_pb_storage('SM'))

        test.log.info('2.1 Create same entry in ME,FD,ON PB with different text')
        test.log.info('2.2 DUT MO Call by dialing ATD<Aux num>; Check LD,DC')
        test.expect(test.dut.at1.send_and_verify('atd{};'.format(test.r1_nat_num), '', ''))
        test.expect(test.r1.at1.wait_for('RING'))
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('at+clcc',
                                                 '.*CLCC: 1,0,0,0,0,\"{}\".*"{}".*OK.*'.format(test.r1_nat_num,
                                                                                               text_list[1])))
        test.expect(test.dut.at1.send_and_verify('ath'))
        test.expect(test.r1.at1.send_and_verify('ath'))
        test.log.info('2.3 Check LD,DC, delete ME entry')
        if 'LD' in list_s:
            test.expect(test.check_ld_dc('LD', 1, test.r1_nat_num, text_list[1]))
        else:
            test.log.info('Not support LD ,skip')
        if 'DC' in list_s:
            test.expect(test.check_ld_dc('DC', 1, test.r1_nat_num, text_list[1]))
        else:
            test.log.info('Not support DC ,skip')
        test.expect(test.dut.dstl_clear_select_pb_storage('ME'))

        test.log.info('3.1 Create same entry in FD,ON PB with different text')
        test.log.info('3.2 DUT MO Call by dialing ATD<Aux num>; Check LD,DC')
        test.expect(test.dut.at1.send_and_verify('atd{};'.format(test.r1_nat_num), '', ''))
        test.expect(test.r1.at1.wait_for('RING'))
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('at+clcc',
                                                 '.*CLCC: 1,0,0,0,0,\"{}\".*"{}".*OK.*'.format(test.r1_nat_num,
                                                                                               text_list[2])))
        test.expect(test.dut.at1.send_and_verify('ath'))
        test.expect(test.r1.at1.send_and_verify('ath'))
        test.log.info('3.3 Check LD,DC, delete ME entry')
        if 'LD' in list_s:
            test.expect(test.check_ld_dc('LD', 1, test.r1_nat_num, text_list[2]))
        else:
            test.log.info('Not support LD ,skip')
        if 'DC' in list_s:
            test.expect(test.check_ld_dc('DC', 1, test.r1_nat_num, text_list[2]))
        else:
            test.log.info('Not support DC ,skip')
        test.expect(test.dut.dstl_clear_select_pb_storage('FD'))

        test.log.info('4.1 Create same entry in ON PB with different text')
        test.log.info('4.2 DUT MO Call by dialing ATD<Aux num>; Check LD,DC')
        test.expect(test.dut.at1.send_and_verify('atd{};'.format(test.r1_nat_num), '', ''))
        test.expect(test.r1.at1.wait_for('RING'))
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('at+clcc',
                                                 '.*CLCC: 1,0,0,0,0,\"{}\".*"{}".*OK.*'.format(test.r1_nat_num,
                                                                                               text_list[3])))
        test.expect(test.dut.at1.send_and_verify('ath'))
        test.expect(test.r1.at1.send_and_verify('ath'))
        test.log.info('4.3 Check LD,DC, delete ME entry')
        if 'LD' in list_s:
            test.expect(test.check_ld_dc('LD', 1, test.r1_nat_num, text_list[3]))
        else:
            test.log.info('Not support LD ,skip')
        if 'DC' in list_s:
            test.expect(test.check_ld_dc('DC', 1, test.r1_nat_num, text_list[3]))
        else:
            test.log.info('Not support DC ,skip')
        test.expect(test.dut.dstl_clear_select_pb_storage('ON'))

    def check_ld_dc(test, storage, index, num, text):
        maxloc = test.dut.dstl_get_pb_storage_max_location(storage)
        return test.dut.at1.send_and_verify('at+cpbr=1,{}'.format(maxloc),
                                            'CPBR: {},\"{}\".*{}.*OK'.format(index, num, text))


if "__main__" == __name__:
    unicorn.main()
