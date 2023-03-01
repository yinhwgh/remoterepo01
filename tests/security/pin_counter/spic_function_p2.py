# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0092778.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.security import unlock_sim_pin2


class Test(BaseTest):
    '''
    TC0092778.001 - TPAtSpicFunctionP2
    Intention:
    This test case is to check PIN counter function while in SPIC command is set to “P2”, means SIM PIN2.
    Subscriber: 1
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(10)
        test.simpin2 = test.dut.sim.pin2
        test.simpuk2 = test.dut.sim.puk2
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))

    def run(test):
        if test.simpin2 !='None' and test.simpuk2 !='None':
            test.log.info(f'Sim card PIN2:{test.simpin2}, PUK2:{test.simpuk2}')
        else:
            test.expect(False, critical=True,msg='Sim card info missing, please check!')

        test.log.step('1.Insert SIM card and enter SIM PIN using.')
        test.dut.dstl_enter_pin()
        test.sleep(3)

        test.log.step('2.Query current PIN counter using.')
        test.expect(test.dut.at1.send_and_verify("AT^SPIC", ".*\^SPIC: 3.*OK.*"))

        test.log.step('3.Query current the required password.')
        test.expect(test.dut.at1.send_and_verify("AT^SPIC?", ".*\^SPIC: SIM PIN2.*OK.*"))

        test.log.step('4.Enter wrong PIN2 using AT+CPBS="FD","wrong PIN2", at the same time check the PIN counter.')
        test.expect(test.dut.at1.send_and_verify("AT+CPBS=\"FD\",\"6789\"", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SPIC", ".*\^SPIC: 2.*OK.*"))

        test.log.step('5.After 3 times attempts, PIN2 is locked, query the required password.')
        test.expect(test.dut.at1.send_and_verify("AT+CPBS=\"FD\",\"6789\"", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SPIC", ".*\^SPIC: 1.*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBS=\"FD\",\"6789\"", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SPIC", ".*\^SPIC: 10.*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SPIC?", ".*\^SPIC: SIM PUK2.*OK.*"))

        test.log.step('6.Enter wrong PUK2 and check the PIN counter.')
        test.expect(test.dut.at1.send_and_verify("AT^SPIC?", ".*\^SPIC: SIM PUK2.*OK.*"))
        if test.dut.dstl_support_at_cpin2():
            test.expect(test.dut.at1.send_and_verify(f"AT+CPIN2=\"04540000\",\"{test.simpin2}\"", ".*\+CME ERROR: incorrect password.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SPIC", ".*\^SPIC: 9.*OK.*"))
            test.log.step('7.Enter correct PUK and then check the PIN counter.')
            test.expect(test.dut.at1.send_and_verify(f"AT+CPIN2=\"{test.simpuk2}\",\"{test.simpin2}\"",'OK'))
        else:
            test.expect(test.dut.at1.send_and_verify(f"AT+CPIN=\"04540000\",\"{test.simpin2}\"",".*\+CME ERROR: incorrect password.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SPIC", ".*\^SPIC: 9.*OK.*"))
            test.log.step('7.Enter correct PUK and then check the PIN counter.')
            test.expect(test.dut.at1.send_and_verify(f"AT+CPIN=\"{test.simpuk2}\",\"{test.simpin2}\"", "OK"))


    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
