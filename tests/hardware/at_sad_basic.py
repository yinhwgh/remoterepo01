#author: liu.xiaolin@thalesgroup.com
#location: Dalian
#TC0092803.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect

class Test(BaseTest):
    '''
    TC0092803.001 - BasicSADcommand
    Intention: Check functionality of command AT^SAD
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='.*OK.*'))

    def run(test):
        test.log.step("1. Check test command.")
        test.expect(test.dut.at1.send_and_verify('AT^SAD=?', expect='\^SAD: \(10-13\).*OK.*'))
        test.log.step("2. Check SAD for all supported parameters.")
        all_modes= [10,11,13]
        query_setting = 12
        for i in all_modes:
            test.expect(test.dut.at1.send_and_verify(f'AT^SAD={i}', expect=f'\^SAD: {i}.*OK.*'))
            test.expect(test.dut.at1.send_and_verify(f'AT^SAD={query_setting}', expect=f'\^SAD: {i}.*OK.*'))


    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('AT&F', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT&W', expect='.*OK.*'))


if '__main__' == __name__:
    unicorn.main()
