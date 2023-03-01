#responsible agata.mastalska@globallogic.com
#Wroclaw

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service import register_to_network

class Test(BaseTest):
    """
    Init test
    Prepares a module for testing
    author: agata.mastalska@globallogic.com
    """

    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        test.log.step("Init test")
        test.dut.dstl_restart(test.dut.at1)
        test.dut.dstl_enter_pin()

        supported_products = ["MIAMI", "JAKARTA", "BOXWOOD", "GINGER"] 

        if test.dut.project in supported_products:
            test.log.step("Commands supported by MIAMI, JAKARTA, BOXWOOD and GINGER")
            test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*|.*ERROR.*"))

            test.expect(test.dut.at1.send_and_verify("ATZ", ".*OK.*|.*ERROR.*"))
            test.sleep(0.4)
            test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT&V", ".*OK.*|.*ERROR.*"))

            test.expect(test.dut.at1.send_and_verify("AT^SCFG?", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CFUN?", ".*OK.*|.*ERROR.*"))

            test.expect(test.dut.at1.send_and_verify("AT^CICRET=SWN", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SIEKRET=0", ".*OK.*|.*ERROR.*"))

            test.expect(test.dut.at1.send_and_verify("ATI", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("ATI1", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("ATI8", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("ATI51", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("ATI61", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("ATI176", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("ATI255", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("ATI281", ".*OK.*|.*ERROR.*"))

            test.expect(test.dut.at1.send_and_verify("AT+CGMM", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT+GMM", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CGMR", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT+GMR", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CGMI", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT+GMI", ".*OK.*|.*ERROR.*"))

            test.expect(test.dut.at1.send_and_verify("AT^SOS=bootloader/info", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SOS=ver", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SOS=adc/hwid", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SINFO?", ".*OK.*|.*ERROR.*"))

            test.expect(test.dut.at1.send_and_verify("AT+CGSN", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT+GSN", ".*OK.*|.*ERROR.*"))

        if test.dut.project is "MIAMI":
            test.log.step("Commands supported by Qualcomm")
            test.expect(test.dut.at1.send_and_verify("ATI2", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("ATI3", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SGSN", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SGSN?", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SSVN", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SSRVSET=\"actsrvset\"", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SSRVSET=\"current\"", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"URC/DstIfc\"", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SINFO=ProvCfg/Ident", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SABR=\"coredump\"", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"MEopMode/CoreDump\"", ".*OK.*|.*ERROR.*"))
        
        else:
            test.log.step("Commands supported by Intel")
            test.expect(test.dut.at1.send_and_verify("ATI384", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT+FMR", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT+XLOG", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT+XLOG=2", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT+XATTMODE?", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT+XATTMODE=0", ".*OK.*|.*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT+XSIO?", ".*OK.*|.*ERROR.*"))

    def cleanup(test):
        test.dut.at1.close()

if "__main__" == __name__:
    unicorn.main()
