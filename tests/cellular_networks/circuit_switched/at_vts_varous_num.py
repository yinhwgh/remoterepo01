#author: haofeng.ding@thalesgroup.com
#location: Dalian
#TC0093115.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call.setup_voice_call import dstl_is_data_call_supported

class Test(BaseTest):
    '''
        TC0093115.001 - DtmfSequenceWithVariousNumberOfSignals
        To check if the duration of gaps between DTMF tones generate in sequence are no longer than
        300 ms.
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
        test.log.info('Enable error reporting')
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='OK'))

    def run(test):
        r1_phone_num = test.r1.sim.int_voice_nr
        test.log.info('Establish voice call between DUT and REMOTE')
        test.expect(test.dut.at1.send_and_verify('atd{};'.format(r1_phone_num), '', wait_for=''))
        test.r1.at1.wait_for('RING')
        test.sleep(2)
        test.expect(test.r1.at1.send_and_verify('ata'))
        test.sleep(2)
        test.log.info('A.5')
        test.expect(test.dut.at1.send_and_verify('AT+VTS="1";+VTS="2";+VTS="3";+VTS="3";+VTS="3";', expect='OK'))
        test.log.info('B.10')
        test.expect(test.dut.at1.send_and_verify('AT+VTS="1";+VTS="2";+VTS="3";+VTS="3";+VTS="3";+VTS="4";+VTS="5";+VTS="6";+VTS="7";+VTS="8";',expect='OK'))
        test.log.info('C.15')
        test.expect(test.dut.at1.send_and_verify('AT+VTS="1";+VTS="2";+VTS="3";+VTS="3";+VTS="3";+VTS="4";+VTS="5";+VTS="6";+VTS="7";+VTS="8";+VTS="9";+VTS="A";+VTS="B";+VTS="C";+VTS="D";',expect='OK'))
        test.log.info('D.25')
        test.expect(test.dut.at1.send_and_verify('AT+VTS="1";+VTS="2";+VTS="3";+VTS="3";+VTS="3";+VTS="4";+VTS="5";+VTS="6";+VTS="7";+VTS="8";+VTS="9";+VTS="A";+VTS="B";+VTS="C";+VTS="D";+VTS="*";+VTS="#";+VTS="2";+VTS="3";+VTS="3";+VTS="3";+VTS="4";+VTS="5";+VTS="6";+VTS="7";',expect='OK', timeout=30))
        test.log.info('E.40')
        test.expect(test.dut.at1.send_and_verify('AT+VTS="1";+VTS="2";+VTS="3";+VTS="3";+VTS="3";+VTS="4";+VTS="5";+VTS="6";+VTS="7";+VTS="8";+VTS="9";+VTS="A";+VTS="B";+VTS="C";+VTS="D";+VTS="*";+VTS="#";+VTS="2";+VTS="3";+VTS="3";+VTS="3";+VTS="4";+VTS="5";+VTS="6";+VTS="7";+VTS="1";+VTS="2";+VTS="3";+VTS="3";+VTS="3";+VTS="4";+VTS="5";+VTS="6";+VTS="7";+VTS="8";+VTS="9";+VTS="A";+VTS="B";+VTS="C";+VTS="D";+VTS="4";+VTS="5";+VTS="6";+VTS="7";+VTS="8";',expect='OK', timeout= 30))
        test.log.info('Analyze traces and check if duration between each of DTMF tones in sequence is no longer than 300 ms for each sequence of DTMF, also check duration of DTMF tones')
        test.expect(test.dut.at1.send_and_verify('at+vts="5"', expect='OK'))
        test.log.info('Terminate the call')
        test.expect(test.dut.at1.send_and_verify('ath', expect='OK'))
    def cleanup(test):
        test.log.info('***Test End***')


if '__main__' == __name__:
    unicorn.main()
