#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0000116.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.phonebook import phonebook_handle
from dstl.call import setup_voice_call

class Test(BaseTest):
    """
    TC0000116.001 - TpCAtdl
    Test atdl command.
    Only test voice call currently.
    """

    def setup(test):

        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.dut.dstl_register_to_network()
        test.r1.dstl_register_to_network()

        test.r2.dstl_detect()
        test.r2.dstl_register_to_network()

    def run(test):
        dut_phone_num = test.dut.sim.nat_voice_nr
        r1_phone_num = test.r1.sim.nat_voice_nr
        r2_phone_num = test.r2.sim.nat_voice_nr

        test.log.step('1.Clear entry in LD phonebook')
        max_ld = test.dut.dstl_get_pb_storage_max_location('LD')
        test.dut.dstl_clear_select_pb_storage('LD')

        test.log.step('2.voice call dut to r1 create first entry and test atdl')
        test.expect(test.dut.dstl_voice_call_by_number(test.r1,r1_phone_num))
        test.expect(test.dut.at1.send_and_verify('ath'))
        test.expect(test.r1.at1.wait_for('NO CARRIER'))
        test.expect(test.r1.at1.send_and_verify('ath'))
        test.expect(test.dut.at1.send_and_verify(f'at+cpbr=1,{max_ld}',r1_phone_num))

        test.dut.at1.send_and_verify('atdl;')
        test.expect(test.r1.at1.wait_for('RING', timeout=15))
        test.expect(test.r1.at1.send_and_verify('at+clcc',f'\+CLCC: 1,1,4,0,0,.*{dut_phone_num}.*'))
        test.expect(test.r1.at1.send_and_verify('ata'))
        test.sleep(2)
        test.expect(test.r1.at1.send_and_verify('at+clcc', f'\+CLCC: 1,1,0,0,0,.*{dut_phone_num}.*'))
        test.expect(test.dut.at1.send_and_verify('at+clcc', f'\+CLCC: 1,0,0,0,0,.*{r1_phone_num}.*'))
        test.expect(test.dut.at1.send_and_verify('ath'))
        test.expect(test.r1.at1.wait_for('NO CARRIER'))
        test.expect(test.r1.at1.send_and_verify('ath'))

        test.log.step('3.voice call dut to r2 create second entry and test atdl')
        test.expect(test.dut.dstl_voice_call_by_number(test.r2, r2_phone_num))
        test.expect(test.dut.at1.send_and_verify('ath'))
        test.expect(test.r2.at1.send_and_verify('ath'))
        test.expect(test.dut.at1.send_and_verify(f'at+cpbr=1,{max_ld}', r2_phone_num))

        test.dut.at1.send_and_verify('atdl;')
        test.expect(test.r2.at1.wait_for('RING', timeout=15))
        test.expect(test.r2.at1.send_and_verify('at+clcc', f'\+CLCC: 1,1,4,0,0,.*{dut_phone_num}.*'))
        test.expect(test.r2.at1.send_and_verify('ata'))
        test.sleep(2)
        test.expect(test.r2.at1.send_and_verify('at+clcc', f'\+CLCC: 1,1,0,0,0,.*{dut_phone_num}.*'))
        test.expect(test.dut.at1.send_and_verify('at+clcc', f'\+CLCC: 1,0,0,0,0,.*{r2_phone_num}.*'))
        test.expect(test.dut.at1.send_and_verify('ath'))
        test.expect(test.r2.at1.wait_for('NO CARRIER'))
        test.expect(test.r2.at1.send_and_verify('ath'))

        test.log.step('4.test ATDL; produce an ERROR with an empty LD phonebook')
        test.dut.dstl_clear_select_pb_storage('LD')
        test.expect(test.dut.at1.send_and_verify('atdl;','ERROR'))

        test.log.step('5.test ATDLI; skip')
        test.log.step('6.test ATDLi; skip')


    def cleanup(test):
       pass





if "__main__" == __name__:
    unicorn.main()
