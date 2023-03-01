#responsible: yi.guo@thalesgroup.com
#location: Beijing
#TC0091774.001 - TpAtAndFBasic

import unicorn
import random

from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network


class TpAtAndFBasic(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.log.info("1. Restore to default configurations ")
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*"))
        test.log.info("*******************************************************************\n\r")

        test.log.info("2. Enable SIM PIN lock before testing  ")

        test.expect(test.dut.at1.send_and_verify(r'AT+CLCK="SC",1,"{}"'.format(test.dut.sim.pin1),".*(OK|ERROR).*"))
        test.dut.dstl_restart()
        # test.device.dstl_restart()
        test.sleep(2)
        test.log.info("*******************************************************************\n\r")
        pass

    def run(test):

        test.log.info("1. test: Check AT&F Execute Command before input SIM PIN ")
        # test.expect(test.dut.at1.send_and_verify(r'AT^SCFG=?', '.*SCFG: \"MEopMode/PwrSave\".*'))
        test.expect(test.dut.at1.send_and_verify(r'AT&F', '.*OK.*'))
        test.log.info("*******************************************************************\n\r")



        test.log.info("2. test: Change ATV value to ATV0 with PIN ")
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify(r'AT&F', '.*OK.*'))
        test.log.info("*******************************************************************\n\r")

        test.log.info("3. Set incorret value  of AT&F")
        test.expect(test.dut.at1.send_and_verify(r'AT&F3', r'.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT&F12345', r'.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT&FB', r'.*ERROR.*'))
        test.log.info("*******************************************************************\n\r")

        test.log.info("4. Change some settings and restore the default settings via AT&F")
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify(r'AT+CMGF=1', r'.*OK.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT+CMEE=0', r'.*OK.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT^SSET=1', r'.*OK.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT+CREG=2', r'.*OK.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT^SLED=1', r'.*OK.*'))
        test.expect(
            test.dut.at1.send_and_verify(r'AT&V',
                                         r'.*CMGF: 1[\s\S]*CMEE: 0[\s\S]*SSET: 1[\s\S]*CREG: 2[\s\S]*SLED: 1[\s\S]*OK.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT&F', r'.*OK.*'))
        test.expect(
            test.dut.at1.send_and_verify(r'AT&V',
                                         r'.*CMGF: 0[\s\S]*CMEE: 2[\s\S]*SSET: 0[\s\S]*CREG: 0[\s\S]*SLED: 0[\s\S]*OK.*'))

    def cleanup(test):
        pass


if (__name__ == "__main__"):
    unicorn.main()
