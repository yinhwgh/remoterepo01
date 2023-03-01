#author: xiaolin.liu@thalesgroup.com
#location: Dalian
#TC0092775.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.security.lock_unlock_sim import dstl_lock_sim


class Test(BaseTest):
    '''
    TC0092775.001 - TPAtSpicFunctionSC
    Intention: This test case is to check PIN counter function while in SPIC command is set to “SC”, means SIM PIN.
        '''
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_lock_sim()
        test.dut.dstl_restart()
        test.sleep(10)
        test.simpin1 = test.dut.sim.pin1
        test.simpuk1 = test.dut.sim.puk1
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))

    def run(test):
        if test.simpin1 != 'None' and test.simpuk1 != 'None':
            test.log.info(f'Sim card PIN1:{test.simpin1}, PUK1:{test.simpuk1}')
        else:
            test.expect(False, critical=True, msg='Sim card info missing, please check!')

        test.log.step('1.Insert SIM card and enter wrong SIM PIN.')
        test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"5678\"", ".*ERROR.*"))

        test.log.step('2.Query current the required password.')
        test.expect(test.dut.at1.send_and_verify("AT^SPIC?", ".*\^SPIC: SIM PIN.*OK.*"))

        test.log.step('3.Query current PIN counter using.')
        test.expect(test.dut.at1.send_and_verify("AT^SPIC", ".*\^SPIC: 2.*OK.*"))

        test.log.step('4.Enter wrong PIN1 twice, at the same time check the PIN counter.')
        test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"5678\"", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SPIC", ".*\^SPIC: 1.*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"5678\"", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SPIC", ".*\^SPIC: 10.*OK.*"))

        test.log.step('5.After 2 times attempts, PIN1 is locked, query the required password.')
        test.expect(test.dut.at1.send_and_verify("AT^SPIC?", ".*\^SPIC: SIM PUK.*OK.*"))

        test.log.step('6.Enter wrong PUK1 and check the PIN counter.')
        test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"11111111\",\"1234\"", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SPIC", ".*\^SPIC: 9.*OK.*"))

        test.log.step('7.Enter correct PUK1 and check the PIN counter.')
        test.expect(test.dut.at1.send_and_verify(f"AT+CPIN=\"{test.simpuk1}\",\"1234\"", ".*OK.*"))
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "+CPIN: READY"))
        test.expect(test.dut.at1.send_and_verify("AT^SPIC", ".*\^SPIC: 3.*OK.*"))


    def cleanup(test):
        pass


if '__main__' == __name__:
    unicorn.main()
