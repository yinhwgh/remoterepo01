#responsible: feng.han@thalesgroup.com
#location: Dalian
#TC0095534.003

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.network_service import register_to_network


class Test(BaseTest):
    """
    TC0095534.003 - FactoryTestModeMultipleEnteringLeaving
    Check if module is able to multiple operation of entering/leaving Factory Test Mode (FTM)
    This version of TC has been created for modules where entering to FTM is executed by commands for generating and measuring CW signal
    Author: Fhan
    """

    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        for i in range(50):
            test.log.info('1.Check current functionality level (AT+CFUN?).')
            test.expect(test.dut.at1.send_and_verify('at+cfun?', '+CFUN: 1'))
            test.log.info('2.Enter FTM mode and send few AT commands')
            test.expect(test.dut.at1.send_and_verify('at+cfun=5', 'OK'))
            test.expect(test.dut.at1.send_and_verify('at+cfun?', '+CFUN: 5'))
            test.log.info('3. Send command for generating Continuous Wave signal')
            test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/CT","1","0","50","19575"', 'OK'))
            test.sleep(5)
            test.log.info('4. Check current functionality level')
            test.expect(test.dut.at1.send_and_verify('at+cfun?', '+CFUN: 5'))
            test.log.info('5. Leave FTM using command AT+CFUN=1,1')
            test.dut.dstl_restart()
            test.log.info('6. Check functionality level after restart and Enter FTM mode')
            test.expect(test.dut.at1.send_and_verify('at+cfun?', '+CFUN: 1'))
            test.expect(test.dut.at1.send_and_verify('at+cfun=5', 'OK'))
            test.log.info('7. Send command for measuring Continuous Wave signal')
            test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/CR","0","190","4","1","0"', 'OK'))
            test.sleep(5)
            test.log.info('8. Check current functionality level')
            test.expect(test.dut.at1.send_and_verify('at+cfun?', '+CFUN: 5'))
            test.log.info('9. Leave FTM using command AT+CFUN=1,1')
            test.dut.dstl_restart()
            test.log.info('10.Check functionality level after restart')
            test.expect(test.dut.at1.send_and_verify('at+cfun?', '+CFUN: 1'))

    def cleanup(test):
        pass

if "__main__" == __name__:
        unicorn.main()
