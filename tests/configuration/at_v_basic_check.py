#responsible: yi.guo@thalesgroup.com
#location: Beijing
#TC0091776.001 - TpAtAndVBasic

import unicorn

from core.basetest import BaseTest

from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.security import lock_unlock_sim


class tpAtAndVBasic(BaseTest):
    def setup(test):
        test.dut.detect()
        test.log.info("1. Restore to default configurations ")
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.log.info("2. Enable SIM PIN lock before testing  ")
        test.dut.dstl_lock_sim()
        # restart(test.dut)
        test.dut.dstl_restart()
        test.sleep(2)


    def run(test):
        test.log.info("1. test: check exec command before input SIM PIN")
        test.expect(test.dut.at1.send_and_verify("AT&v", ".*OK.*"))

        test.log.info("2. test: check test and exec command after input SIM PIN")
        test.expect(test.dut.dstl_enter_pin())
        if (test.dut.project == 'VIPER'):
            test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
        else:
            test.expect(test.dut.at1.send_and_verify("AT+CMEE=1", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+Creg=2", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&v", ".*OK.*"))

        test.log.info("3. test: check at command with invalid paramter ")
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at&v=?", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at&v?", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at&v=0", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at&v9876", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at&v=-1", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at&v?", ".*ERROR.*"))

        test.log.info("4. test: functional test of at command ")
        if test.dut.project.lower() == "serval":
            test.expect(test.dut.at1.send_and_verify("AT+CMEE=0", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("at+cmee?", ".*CMEE: 0.*"))
            test.expect(test.dut.at1.send_and_verify("AT+Creg=1", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+creg?", ".*CREG: 1*"))
            test.expect(test.dut.at1.send_and_verify("AT&v", ".*CMEE: 0.*",".*CREG: 1.*"))
            test.expect(test.dut.at1.send_and_verify("AT&f", ".*OK*"))
            test.expect(test.dut.at1.send_and_verify("AT&v", ".*CMEE: 2.*", ".*CREG: 0.*"))
        else:
            test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("at+cmee?", ".*CMEE: 2.*"))
            test.expect(test.dut.at1.send_and_verify("AT+Creg=1", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+creg?", ".*CREG: 1*"))
            test.expect(test.dut.at1.send_and_verify("AT&v", ".*CMEE: 2.*",".*CREG: 1.*"))
            test.expect(test.dut.at1.send_and_verify("AT&f", ".*OK*"))
            if (test.dut.project == 'VIPER'):
                test.expect(test.dut.at1.send_and_verify("AT&V", ".*E1 Q0 V1 X0 &C1 &D2 &S0 .*Q3.*S0:000.*[+]CRC: 0.*"
                                                             "[+]CMGF: 0.*[+]CSDH: 0.*[+]CNMI: 0,0,0,0,1.*[+]CMEE: 2.*"
                                                             "[+]CSMS: 0.*SLCC: 0.*SCKS: 0.*SSET: 0.*[+]CREG: 0.*"
                                                             "[+]CLIP: 0.*[+]COPS: 0,0.*", timeout=10))
            else:
                test.expect(test.dut.at1.send_and_verify("AT&v", ".*CMEE: 0.*", ".*CREG: 0.*"))

    def cleanup(test):
        pass

if (__name__ == "__main__"):
    unicorn.main()
