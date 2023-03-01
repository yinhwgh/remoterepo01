# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0000512.001

import unicorn
from core.basetest import BaseTest
from dstl.phonebook import phonebook_handle
from dstl.auxiliary import init
from dstl.network_service import register_to_network


class Test(BaseTest):
    '''
    TC0000512.001 - Cnum500
    Intention: Read the own number(s) of the subscribers from the SIM with "CNUM" command.
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_enter_pin()
        test.sleep(10)

    def run(test):
        test.log.info('1.set values for own number')
        test.expect(test.dut.dstl_set_pb_memory_storage('ON'))
        text = 'own number'
        test.expect(test.dut.dstl_write_pb_entries(1, test.dut.sim.int_voice_nr, 145, text))

        test.log.info('2.repeat reading out the own number(s) 500 times')
        for i in range(500):
            test.log.info('Test loop {}'.format(i))
            test.expect(test.dut.at1.send_and_verify('at+cnum',
                                                     r'+CNUM: "{}","{}",145'.format(text, test.dut.sim.int_voice_nr)))

        test.log.info('3.reset values')
        test.dut.dstl_clear_select_pb_storage('ON')
        test.expect(test.dut.at1.send_and_verify('at+cnum', 'OK'))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
