# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0091790.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.security import lock_unlock_sim


class Test(BaseTest):
    '''
    TC0091790.001 - TpAtCpwdBasic
    Intention:
    This procedure provides the possibility of basic tests for the read and write command of at+cpwd.
    Subscriber: 1
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_lock_sim()
        test.dut.dstl_restart()
        test.sleep(10)

    def run(test):
        simpin = test.dut.sim.pin1
        new_pin = '04540000'
        #max length 8
        new_pin_long='123456789'
        test.log.info('1. test without pin')
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CPIN=?", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*CPIN: SIM PIN.*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at+cpwd=?","CME ERROR: SIM PIN required"))
        test.log.info('2. test with pin')
        test.dut.dstl_enter_pin()
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify("at+cpwd=?", ".*CPWD: .*OK.*"))

        test.log.info('3. check all parameters and also with invalid values')
        test.expect(test.dut.at1.send_and_verify("at+cpwd?", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+cpwd", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+cpwd=\"SS\",\"{}\",\"{}\"".format(simpin,new_pin), ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+cpwd=1", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+cpwd=\"SC\",\"{}\",\"{}\"".format(simpin, new_pin_long), ".*ERROR.*"))


        test.log.info('4. check functionality by changing PIN, entering new PIN and setting it back to original PIN')
        test.log.info('4.1 Change PIN')
        test.expect(test.dut.at1.send_and_verify("at+cpwd=\"SC\",\"{}\",\"{}\"".format(simpin, new_pin), "OK"))
        test.dut.dstl_restart()
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*CPIN: SIM PIN.*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"{}\"".format(new_pin), ".*OK.*"))
        test.sleep(3)
        test.log.info('4.2 Change it back to original PIN')
        test.expect(test.dut.at1.send_and_verify("at+cpwd=\"SC\",\"{}\",\"{}\"".format(new_pin, simpin), "OK"))
        test.dut.dstl_restart()
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*CPIN: SIM PIN.*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"{}\"".format(simpin), ".*OK.*"))



    def cleanup(test):
        test.log.info('***Test End, clean up***')



if "__main__" == __name__:
    unicorn.main()
