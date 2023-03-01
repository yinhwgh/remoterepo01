#author: Thomas.Troeger@thalesgroup.com
#location: Berlin
#TC0088319.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode, dstl_set_airplane_mode

class Test(BaseTest):
    """Intention:
    Checks persistance of Contexts."""

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


                
        # Define parameters of +CGDCONT, +CGDSCONT, +CGEQOS, +CGAUTH, +CGTFT
        
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=1,\"IP\",\"TestAPNIP\"', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDSCONT=2,1,1,2', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGEQOS=1,2,512,256,256,128', expect='OK'))
        # test.expect(test.dut.at1.send_and_verify('AT+CGAUTH=4,\"IP\",\"TestAPNIP\"', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGTFT=1,1,1,\"255.255.255.255.127.64.0.0\"', expect='OK'))
        
        # - restart module and check values
        test.dut.dstl_restart()

        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT?', expect='.*[+]CGDCONT: 1,\"IP\",\"TestAPNIP\".*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDSCONT?', expect='.*[+]CGDSCONT: 2,1,1,2.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGEQOS?', expect='.*[+]CGEQOS: 1,2,512,256,256,128.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGTFT?', expect='.*[+]CGTFT: 1,1,1,\"255.255.255.255.127.64.0.0\".*'))
        
        
        
        # set to factory default and check values
        test.expect(test.dut.at1.send_and_verify('AT+CGTFT=1', expect='[+]CGTFT:'))
        test.expect(test.dut.at1.send_and_verify('AT+CGEQOS=1', expect='[+]CGEQOS:'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDSCONT=2', expect='[+]CGDSCONT:'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=1', expect='OK'))



    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('AT&F', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT&W', expect='OK'))
        test.dut.dstl_set_full_functionality_mode()


if '__main__' == __name__:
    unicorn.main()
