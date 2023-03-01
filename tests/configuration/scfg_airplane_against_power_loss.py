#author: cong.hu@thalesgroup.com
#location: Dalian
#TC0103778.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import restart_module
from dstl.auxiliary.devboard import devboard
from dstl.auxiliary import check_urc

class Test(BaseTest):
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.at1.send_and_verify('AT+CMEE=2', expect='OK'))

    def run(test):
        test.log.info('1. Set at^scfg="MEopMode/CFUN","0".')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/CFUN","0"', expect='.*OK.*'))
        test.log.info('2. Set cfun as airplane mode.')
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=4', expect='.*OK.*'))
        test.log.info('3. Shut down module with at^smso and then power on to check the state of Cfun.')
        for i in range(10):
            print(f'#########################SMSO LOOP {i} #########################')
            test.expect(test.dut.at1.send_and_verify('AT^SMSO', expect='.*OK.*', wait_for='SHUTDOWN'))
            test.sleep(2)
            test.expect(test.dut.dstl_turn_on_igt_via_dev_board(1000))
            test.expect(test.dut.at1.wait_for('\^SYSSTART'))
            test.expect(test.dut.at1.send_and_verify('AT+CFUN?', expect='\+CFUN: 4'))
        test.log.info('4. Power off module with Mc test or manually and then power on to check the state of Cfun')
        for i in range(10):
            print(f'#########################SMSO LOOP {i} #########################')
            test.expect(test.dut.devboard.send_and_verify("MC:EMERG=1000", "OK"))
            test.expect(test.dut.dstl_check_urc('\^SYSSTART'))
            test.expect(test.dut.at1.send_and_verify('AT+CFUN?', expect='\+CFUN: 4'))

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=1', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/CFUN","1"', expect='.*OK.*'))
        test.expect(test.dut.dstl_restart())


if '__main__' == __name__:
    unicorn.main()
