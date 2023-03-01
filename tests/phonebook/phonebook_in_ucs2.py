# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0091692.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.call.setup_voice_call import dstl_release_call
from dstl.auxiliary import init
from dstl.network_service import register_to_network
from dstl.configuration.character_set import dstl_convert_to_ucs2
from dstl.phonebook.phonebook_handle import dstl_clear_all_pb_storage

class Test(BaseTest):
    '''
    TC0091692.001 - TpPhonebookInUCS2
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.dut.dstl_register_to_network()
        test.r1.dstl_detect()
        test.r1.dstl_register_to_network()
        test.sleep(10)

    def run(test):
        gsm_text = 'QAZXSW0123'
        ucs2_text = test.dut.dstl_convert_to_ucs2(gsm_text)

        test.log.step('0. clear all PB entry')
        test.dut.dstl_clear_all_pb_storage()
        test.log.step('1.set char set to UCS2')
        test.expect(test.dut.at1.send_and_verify('AT+CSCS="UCS2"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CPBS="SM"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CLIP=1', 'OK'))

        test.log.step('2.write pb entry with text in UCS2')
        test.expect(test.dut.at1.send_and_verify(f'AT+CPBW=1,"{test.r1.sim.nat_voice_nr}",129,"{ucs2_text}"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CPBR=1', f'\+CPBR: 1,.*\"{ucs2_text}\".*OK.*'))

        test.log.step('3.set up call, read clcc and clip')
        test.log.step('3.1 set up call with atd{number};')
        test.expect(test.dut.at1.send_and_verify(f'ATD{test.r1.sim.nat_voice_nr};', 'OK'))
        test.expect(test.r1.at1.wait_for('RING'))
        test.expect(test.dut.at1.send_and_verify('AT+CLCC', f'\+CLCC: .*,\"{ucs2_text}\".*OK.*'))
        test.dut.dstl_release_call()
        test.r1.dstl_release_call()
        test.sleep(5)

        test.log.step('3.2 set up call with atd>"str";')
        test.expect(test.dut.at1.send_and_verify(f'ATD>"{ucs2_text}";', 'OK'))
        test.expect(test.r1.at1.wait_for('RING'))
        test.expect(test.dut.at1.send_and_verify('AT+CLCC', f'\+CLCC: .*,\"{ucs2_text}\".*OK.*'))
        test.dut.dstl_release_call()
        test.r1.dstl_release_call()
        test.sleep(5)

        test.log.step('3.3 MT call')
        test.expect(test.r1.at1.send_and_verify(f'ATD{test.dut.sim.nat_voice_nr};', 'OK'))
        test.expect(test.dut.at1.wait_for('RING'))
        test.expect(test.dut.at1.wait_for(f'.*CLIP: .*"{ucs2_text}".*'))
        test.dut.dstl_release_call()
        test.r1.dstl_release_call()
        test.sleep(2)

        test.log.step('4.set char set to GSM and read')
        test.expect(test.dut.at1.send_and_verify('AT+CSCS="GSM"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CPBR=1', f'\+CPBR: 1,.*\"{gsm_text}\".*OK.*'))

        test.log.step('5.delete test entry')
        test.expect(test.dut.at1.send_and_verify('AT+CPBW=1','.*OK.*'))

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('AT+CLIP=0', 'OK'))


if "__main__" == __name__:
    unicorn.main()
