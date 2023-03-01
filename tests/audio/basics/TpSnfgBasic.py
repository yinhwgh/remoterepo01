#author: Thomas.Troeger@thalesgroup.com
#location: Berlin
#TC0093085.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode, dstl_set_airplane_mode

class Test(BaseTest):
    """Intention:
    Checks basic settings of SNFG local tone """

    def setup(test):
        test.dut.dstl_detect()
        #test.dut.dstl_restart()
        test.expect(test.dut.at1.send_and_verify('at+cfun=1,1', expect='OK'))
        test.sleep(60)
        test.expect(test.dut.at1.send_and_verify('ate1', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='OK'))

    def run(test):
        test.log.step('1. Check command.')
        test.log.step('Step 1.0: check test and exec command without PIN')
        # ==============================================================
        test.dut.at1.send_and_verify("at+CPIN?", ".*O.*")
        if  ("READY" in test.dut.at1.last_response):
            # restart the module
            #test.expect(test.dut.dstl_restart()) waiting for proper working restart 
            test.expect(test.dut.at1.send_and_verify('at+cfun=1,1', expect='OK'))
            test.sleep(60)
            test.expect(test.dut.at1.send_and_verify('ate1', expect='OK'))
            test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='OK'))

        # test.expect(test.dut.at1.send_and_verify('AT+CPIN?', expect='\+CPIN: SIM PIN'))
        test.sleep(10)
        ## test if command exists and parameters are ok
        test.expect(test.dut.at1.send_and_verify('AT^SNFG=?', expect='OK'))
        ### aktivate Indicator , audio for test
        test.dut.at1.send_and_verify("AT^SIND=sounder,1", ".*O.*")
        test.dut.at1.send_and_verify("AT^SIND=audio,1", ".*O.*")
        ### check command with parameter boundaries
        test.dut.at1.send_and_verify("AT^SNFG=10,43,200,200", "OK")
        # test.expect(test.dut.dstl_check_urc('.*[+]CIEV: sounder.*', 4))
        test.sleep(2)
        test.dut.at1.send_and_verify("AT^SNFG=1000,1,3400,3399", "OK")
        test.sleep(5)
        test.dut.at1.send_and_verify("AT^SNFG=65536,44,3410,4000", ".*ERROR.*")
        test.sleep(5)

        test.dut.at1.send_and_verify("AT^SNFG=1000,1,3400,3399", "OK")
        test.sleep(5)
        test.log.step('Step 2.0: check test and exec command with PIN')
        # ==============================================================
        test.expect(test.dut.dstl_register_to_network())

        test.dut.at1.send_and_verify("AT^SNFG=0,43,200,200", "OK")
        # test.expect(test.dut.dstl_check_urc('.*[+]CIEV: sounder.*', 4))
        test.sleep(2)
        test.dut.at1.send_and_verify("AT^SNFG=1000,1,3400,3399", "OK")
        test.sleep(5)
        test.dut.at1.send_and_verify("AT^SNFG=65536,44,3410,4000", ".*ERROR.*")
        test.sleep(5)

        test.dut.at1.send_and_verify("AT^SNFG=1000,43,1800,3399", "OK")
        test.sleep(5)
        test.dut.at1.send_and_verify("AT^SNFG=10000,43,1800,3399", "OK")
        test.sleep(10)


        test.sleep(10)





    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('AT&F', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT&W', expect='OK'))
        #test.dut.dstl_set_full_functionality_mode()
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=1,1', expect='OK'))
        test.sleep(60)
        test.expect(test.dut.at1.send_and_verify('ATE1', expect='OK'))

if '__main__' == __name__:
    unicorn.main()
