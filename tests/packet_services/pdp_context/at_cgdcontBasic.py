#author: Thomas.Troeger@thalesgroup.com
#location: Berlin
#TC0091874.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode, dstl_set_airplane_mode

class Test(BaseTest):
    """Intention:
    Checks basic settings of AT+CGDCONT."""

    def setup(test):
        test.dut.dstl_detect()
        #test.dut.dstl_restart()
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='OK'))

    def run(test):
        test.log.step('1. Check command.')
        test.log.step('Step 1.0: check test and exec command without PIN')
        # ==============================================================
        test.dut.at1.send_and_verify("at+CPIN?", ".*O.*")
        if  ("READY" in test.dut.at1.last_response):
            # restart the module
            test.expect(test.dut.dstl_restart())


        # test.expect(test.dut.at1.send_and_verify('AT+CPIN?', expect='\+CPIN: SIM PIN'))
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=?', expect='.*[+]CGDCONT: (1-16),\"IP\",,,(0-2),(0-4).*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=?', expect='.*[+]CGDCONT: (1-16),\"PPP\",,,(0-2),(0-4).*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=?', expect='.*[+]CGDCONT: (1-16),\"IPV6\",,,(0-2),(0-4).*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=?', expect='.*[+]CGDCONT: (1-16),\"IP\",,,(0-2),(0-4).*\+CGDCONT: (1-16),\"PPP\",,,(0-2),(0-4).*\+CGDCONT: (1-16),\"IPV6\",,,(0-2),(0-4).*\+CGDCONT: (1-16),\"IPV4V6\",,,(0-2),(0-4).*'))


        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=16,\"IPV4V6\",\"TestAPN\",\"0.0.0.0\"', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=15,\"IPV4V6\",\"TestAPN\",\"0.0.0.0\"', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=14,\"IPV4V6\",\"TestAPN\",\"0.0.0.0\"', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=13,\"IPV4V6\",\"TestAPN\",\"0.0.0.0\"', expect='OK'))

        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=12,\"IPV6\",\"TestAPN\",\"0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0\"', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=11,\"IPV6\",\"TestAPN\",\"0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0\"', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=10,\"IPV6\",\"TestAPN\",\"0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0\"', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=9,\"IPV6\",\"TestAPN\",\"0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0\"',  expect='OK'))

        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=8,\"PPP\",\"TestAPNPPP\"', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=7,\"PPP\",\"TestAPNPPP\"', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=6,\"PPP\",\"TestAPNPPP\"', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=5,\"PPP\",\"TestAPNPPP\"', expect='OK'))

        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=4,\"IP\",\"TestAPNIP\"', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=3,\"IP\",\"TestAPNIP\"', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=2,\"IP\",\"TestAPNIP\"', expect='OK'))

       
        test.log.step('Step 2.0: check test and exec command with PIN')
        # ==============================================================
        test.expect(test.dut.dstl_register_to_network())
        test.sleep(40)
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=?', expect='.*[+]CGDCONT: (1-16),\"IP\",,,(0-2),(0-4).*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=?', expect='.*[+]CGDCONT: (1-16),\"PPP\",,,(0-2),(0-4).*'))
        test.expect(
            test.dut.at1.send_and_verify('AT+CGDCONT=?', expect='.*[+]CGDCONT: (1-16),\"IPV6\",,,(0-2),(0-4).*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=?',
                                                 expect='.*[+]CGDCONT: (1-16),\"IP\",,,(0-2),(0-4).*\+CGDCONT: (1-16),\"PPP\",,,(0-2),(0-4).*\+CGDCONT: (1-16),\"IPV6\",,,(0-2),(0-4).*\+CGDCONT: (1-16),\"IPV4V6\",,,(0-2),(0-4).*'))

        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=16,\"IPV4V6\",\"TestAPN\",\"0.0.0.0\"', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=15,\"IPV4V6\",\"TestAPN\",\"0.0.0.0\"', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=14,\"IPV4V6\",\"TestAPN\",\"0.0.0.0\"', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=13,\"IPV4V6\",\"TestAPN\",\"0.0.0.0\"', expect='OK'))

        test.expect(
            test.dut.at1.send_and_verify('AT+CGDCONT=12,\"IPV6\",\"TestAPN\",\"0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0\"',
                                         expect='OK'))
        test.expect(
            test.dut.at1.send_and_verify('AT+CGDCONT=11,\"IPV6\",\"TestAPN\",\"0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0\"',
                                         expect='OK'))
        test.expect(
            test.dut.at1.send_and_verify('AT+CGDCONT=10,\"IPV6\",\"TestAPN\",\"0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0\"',
                                         expect='OK'))
        test.expect(
            test.dut.at1.send_and_verify('AT+CGDCONT=9,\"IPV6\",\"TestAPN\",\"0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0\"',
                                         expect='OK'))

        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=8,\"PPP\",\"TestAPNPPP\"', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=7,\"PPP\",\"TestAPNPPP\"', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=6,\"PPP\",\"TestAPNPPP\"', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=5,\"PPP\",\"TestAPNPPP\"', expect='OK'))

        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=4,\"IP\",\"TestAPNIP\"', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=3,\"IP\",\"TestAPNIP\"', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=2,\"IP\",\"TestAPNIP\"', expect='OK'))

        ###testcases with PIN
        ### cleanup
        test.sleep(10)
        #test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=1', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=2', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=3', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=4', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=5', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=6', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=7', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=8', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=9', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=10', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=11', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=12', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=13', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=14', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=15', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=16', expect='OK'))


    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('AT&F', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT&W', expect='OK'))
        test.dut.dstl_set_full_functionality_mode()


if '__main__' == __name__:
    unicorn.main()
