#responsible: wen.liu@thalesgroup.com
#location: Dalian
#TC0094815.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module


class Test(BaseTest):
    '''
    TC0094815.001 - SindSimAndImsiStatusAfterSimLocked
    Intention: Intention of this test case is to check correctness of SIM status and IMSI value (in AT^SIND read command) in presence of locked SIM card.
    SIM PUK need logged in Webimacs
    '''


    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_restart())
        test.sleep(10)


    def run(test):
        simpuk = test.dut.sim.puk1
        simpin = test.dut.sim.pin1
        incorrect_simpin ='8362'
        new_simpin = '4321'
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='OK'))
        test.log.step("1. Enter SIM PIN and check status of SIM PIN")
        test.expect(test.dut.at1.send_and_verify('at+cpin?', expect='\+CPIN: SIM PIN\s+OK'))
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify('at+cpin?', expect='\+CPIN: READY\s+OK'))
        test.log.step("2. Change SIM PIN via AT+CPWD three times and enter wrong value of <old password> parameter for each time")
        test.expect(test.dut.at1.send_and_verify('at+cpwd=\"SC\",\"{}\",\"{}\"'.format(incorrect_simpin, new_simpin) , expect='\+CME ERROR: incorrect password'))
        test.expect(test.dut.at1.send_and_verify('at+cpwd=\"SC\",\"{}\",\"{}\"'.format(incorrect_simpin, new_simpin) , expect='\+CME ERROR: incorrect password'))
        test.expect(test.dut.at1.send_and_verify('at+cpwd=\"SC\",\"{}\",\"{}\"'.format(incorrect_simpin, new_simpin) , expect='\+CME ERROR: SIM PUK required'))
        test.log.step("3. Check status of SIM PIN")
        if simpuk:
            test.expect(test.dut.at1.send_and_verify('at+cpin?', expect='\+CPIN: SIM PUK\s+OK'))
            test.expect(test.dut.at1.send_and_verify('at^sind?', expect='\^SIND: simstatus,0,3'))
            test.log.step("4. Change SIM PIN by AT+CPIN")
            test.expect(test.dut.at1.send_and_verify('at+cpin=\"{}\",\"{}\"'.format(simpuk, new_simpin), expect='OK'))
            test.expect(test.dut.at1.send_and_verify('at+cpin?', expect='\+CPIN: READY\s+OK'))
            test.expect(test.dut.dstl_restart())
            test.sleep(10)
            test.expect(test.dut.at1.send_and_verify('at+cpin?', expect='\+CPIN: SIM PIN\s+OK'))
            test.expect(test.dut.at1.send_and_verify('at+cpin=\"{}\"'.format(new_simpin), expect='OK'))
            test.expect(test.dut.at1.send_and_verify('at+cpin?', expect='\+CPIN: READY\s+OK'))
            test.log.step("5. Change SIM PIN via AT+CPWD three times and enter wrong value of <old password> parameter for each time")
            test.expect(test.dut.at1.send_and_verify('at+cpwd=\"SC\",\"{}\",\"{}\"'.format(incorrect_simpin, new_simpin), expect='\+CME ERROR: incorrect password'))
            test.expect(test.dut.at1.send_and_verify('at+cpwd=\"SC\",\"{}\",\"{}\"'.format(incorrect_simpin, new_simpin), expect='\+CME ERROR: incorrect password'))
            test.expect(test.dut.at1.send_and_verify('at+cpwd=\"SC\",\"{}\",\"{}\"'.format(incorrect_simpin, new_simpin), expect='\+CME ERROR: SIM PUK required'))
            test.log.step("6. Check status of SIM PIN")
            test.expect(test.dut.at1.send_and_verify('at+cpin?', expect='\+CPIN: SIM PUK\s+OK'))
            test.expect(test.dut.at1.send_and_verify('at^sind?', expect='\^SIND: simstatus,0,3'))
            test.log.step("7. Change SIM PIN by AT+CPIN")
            test.expect(test.dut.at1.send_and_verify('at+cpin=\"{}\",\"{}\"'.format(simpuk, new_simpin), expect='OK'))
            test.expect(test.dut.at1.send_and_verify('at+cpin?', expect='\+CPIN: READY\s+OK'))
            test.expect(test.dut.dstl_restart())
            test.sleep(10)
            test.expect(test.dut.at1.send_and_verify('at+cpin?', expect='\+CPIN: SIM PIN\s+OK'))
            test.expect(test.dut.at1.send_and_verify('at+cpin=\"{}\"'.format(new_simpin), expect='OK'))
            test.expect(test.dut.at1.send_and_verify('at+cpin?', expect='\+CPIN: READY\s+OK'))
            test.log.step("8. Restore SIM PIN")
            test.expect(
                test.dut.at1.send_and_verify("at+cpwd=\"SC\",\"{}\",\"{}\"".format(new_simpin, simpin), expect='OK'))
        else:
            test.log.error('Error, SIM PUK not logged in webimacs')


    def cleanup(test):
        pass


if '__main__' == __name__:
    unicorn.main()
