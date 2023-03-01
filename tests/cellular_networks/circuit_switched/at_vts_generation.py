#responsible: haofeng.ding@thalesgroup.com
#location: Dalian
#TC0071755.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call.setup_voice_call import dstl_is_data_call_supported

class Test(BaseTest):
    '''
    TC0071755.001 - TpCDtmfToneGenerationCommandsQct
    Test of the command: DTMF and tone generation (VTS).
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
        test.expect(test.dut.at1.send_and_verify('at+vts=?','.*\+VTS: \(0-9,#,\*,A-D\),\(1-255\).*'))
		
        test.log.info('2. Establish call between DUT and 2nd subscriber')
        test.expect(test.dut.at1.send_and_verify('atd{};'.format(r1_phone_num),'',wait_for=''))
        test.r1.at1.wait_for('RING')
        test.sleep(2)
        test.expect(test.r1.at1.send_and_verify('ata'))
        test.sleep(2)
        test_correct_chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', '*', '#']
        for i in test_correct_chars:
            test_vts='at+vts="'+str(i)+'"'
            test.expect(test.dut.at1.send_and_verify(test_vts, '.*OK.*'))
        test_incorrect_chars = [' ', '!', '$', '%', '&', '\'', '(', ')', '+', ',', '-', '.', '/', ':', ';', '<', '=', '>', '@', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X','Y', 'Z', '[', ']', '^', '_', '`', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~']
        for i in test_incorrect_chars:
            test_vts = 'at+vts="' + str(i) + '"'
            test.expect(test.dut.at1.send_and_verify(test_vts, '.*\+CME ERROR:.*'))
        test.expect(test.dut.at1.send_and_verify('ath'))
        test.expect(test.r1.at1.wait_for('.*NO CARRIER.*'))


    def cleanup(test):
       test.log.info('***Test End***')



if "__main__" == __name__:
    unicorn.main()

