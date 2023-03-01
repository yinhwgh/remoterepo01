# author: haofeng.ding@thalesgroup.com
# location: Dalian
# TC0071774.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call.setup_voice_call import dstl_is_data_call_supported


class Test(BaseTest):
    '''
    TC0071774.001 - TpCSendDtmfTonesStringQct
    DTMF tone generation with a large string during voice call.
    Subscriber: 2
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.dut.dstl_restart()
        test.r1.dstl_restart()
        test.sleep(3)
        test.r1.dstl_register_to_network()
        test.dut.dstl_register_to_network()

    def run(test):
        r1_phone_num = test.r1.sim.int_voice_nr
        test.log.info('***Test Start***')
        test.log.info('1. Test of the command: DTMF and tone generation')
        test.expect(test.dut.at1.send_and_verify('at+vts=?', '.*\+VTS: \(0-9,#,\*,A-D\),\(1-255\).*'))

        test.log.info('2. Establish call between DUT and 2nd subscriber')
        test.expect(test.dut.at1.send_and_verify('atd{};'.format(r1_phone_num), '', wait_for=''))
        test.r1.at1.wait_for('RING')
        test.sleep(2)
        test.expect(test.r1.at1.send_and_verify('ata'))
        test.sleep(2)
        test.log.info('Verify that you hear dtmf tones on the remote party (subscriber 2) during the voice call')
        test.sleep(10)
        test_vts_string = 'AT+VTS="1",1;+VTS="2",1;+VTS="3",1;+VTS="4",1;+VTS="5",1;+VTS="1",1;+VTS="2",1;+VTS="3",1;+VTS="4",1;+VTS="5",1;+VTS="1",1;+VTS="2",1;+VTS="3",1;+VTS="4",1;+VTS="5",1;+VTS="1",1;+VTS="2",1;+VTS="3",1;+VTS="4",1;+VTS="5",1;+VTS="1",1;+VTS="2",1;+VTS="3",1;+VTS="4",1;+VTS="5",1;'
        test.expect(test.dut.at1.send_and_verify(test_vts_string, '.*OK.*', timeout=60))
        test.sleep(10)
        test_vts_string = 'AT+VTS="5",1;+VTS="6",1;+VTS="7",1;+VTS="8",1;+VTS="9",1;+VTS="5",1;+VTS="6",1;+VTS="7",1;+VTS="8",1;+VTS="9",1;+VTS="5",1;+VTS="6",1;+VTS="7",1;+VTS="8",1;+VTS="9",1;+VTS="5",1;+VTS="6",1;+VTS="7",1;+VTS="8",1;+VTS="9",1;+VTS="5",1;+VTS="6",1;+VTS="7",1;+VTS="8",1;+VTS="9",1;'
        test.expect(test.dut.at1.send_and_verify(test_vts_string, '.*OK.*', timeout=60))
        test.expect(test.dut.at1.send_and_verify('ath'))
        test.expect(test.r1.at1.wait_for('.*NO CARRIER.*'))

    def cleanup(test):
        test.log.info('***Test End***')


if "__main__" == __name__:
    unicorn.main()
