#author: Thomas.Troeger@thalesgroup.com
#location: Berlin
#TC0085121.001
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

        ###1. delete all PDP context and all QoS parameters of all PDP context profiles
        for i in range(1,16):
            test.expect(test.dut.at1.send_and_verify('AT+CGTFT=(i)', expect='[+]CGTFT:'))
            test.expect(test.dut.at1.send_and_verify('AT+CGEQOS=(i)', expect='[+]CGEQOS:'))
            test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=(i)', expect='OK'))
        
        for i in range(2,16):
            test.expect(test.dut.at1.send_and_verify('AT+CGDSCONT=(i)', expect='[+]CGDSCONT:'))
            
        ###2. set all PDP context and all QoS parameters to values other than the defaults

        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=1,\"IP\",\"TestAPNIP\"', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDSCONT=2,1,1,2', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGEQOS=1,2,512,256,256,128', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGTFT=1,1,1,\"255.255.255.255.127.64.0.0\"', expect='OK'))
                            
        ###3. read all PDP context and QoS parameters after setting
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT?', expect='.*1,\"IP\",\"TestAPNIP\".*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDSCONT?', expect='.*2,1,1,2.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGEQOS?', expect='.*1,2,512,256,256,128.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGTFT?', expect='.*1,1,1,\"255.255.255.255.127.64.0.0\".*'))
        
        
        
        
        ###4. reset all device parameters to the default values (ATZ)
        test.expect(test.dut.at1.send_and_verify('ATZ', expect='OK'))

        ###5. read all PDP context and QoS parameters after ATZ

        ###6. load the manufacturer defaults (AT&F)
        test.expect(test.dut.at1.send_and_verify('AT&F', expect='OK'))

        ###7. read all PDP context and QoS parameters after AT&F

        ###8. reboot the DUT (AT+CFUN=1,1)
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=1,1', expect='OK'))
        test.sleep(60)
        ###9. read all PDP context and QoS parameters after CFUN
        
        ###13. restart the DUT
        test.dut.dstl_restart()
        ###14. read all PDP context and QoS parameters after restart
        ###15. delete all PDP context and all QoS parameters of all PDP context profiles
        for i in range(1, 16):
            test.expect(test.dut.at1.send_and_verify('AT+CGTFT=(i)', expect='[+]CGTFT:'))
            test.expect(test.dut.at1.send_and_verify('AT+CGEQOS=(i)', expect='[+]CGEQOS:'))
            test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=(i)', expect='OK'))

        for i in range(2, 16):
            test.expect(test.dut.at1.send_and_verify('AT+CGDSCONT=(i)', expect='[+]CGDSCONT:'))

        test.sleep(10)



                
        ######################################################################################################
        



    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('AT&F', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT&W', expect='OK'))
        test.dut.dstl_set_full_functionality_mode()


if '__main__' == __name__:
    unicorn.main()
