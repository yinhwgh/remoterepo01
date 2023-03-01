#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0105229.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.security import lock_unlock_sim
from dstl.auxiliary import restart_module

class Test(BaseTest):
    '''
    TC0105229.002 - TpAtScslFunc
    At^scsl write command enable/disable the PN lock.
    while enable:
    SIM with MCCMNC not in the <data> list with be blocked
    SIM with MCCMNC in the <data> list with not be blocked
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.password = '00000000'

    def run(test):
        test.log.step("1. Check the module can register on network with the (U)SIM card.")
        test.expect(test.dut.dstl_register_to_network())

        test.log.step('2. Enable the PN lock with at^scsl="PN",1,<password>,<data>; '
                      '(U)SIM\'s MCCMNC should in the data field')
        test.expect(test.dut.dstl_lock_network_personalization(test.password))

        test.log.step('3. Check the module still register on network.')
        test.expect(test.dut.at1.send_and_verify("AT+COPS?", '\d,\d,".+?",\d'))

        test.log.step('4. Restart the module, check module register status.')
        test.dut.dstl_restart()
        test.sleep(2)
        test.dut.at1.send_and_verify(f'AT+CPIN="{test.dut.sim.pin1}"')
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('AT+CPIN?', 'READY'))
        test.sleep(5)
        test.attempt(test.dut.at1.send_and_verify, 'AT+COPS?', '\d,\d,".+?",\d', retry=5, sleep=5)

        test.log.step('5. Disable the PN lock with at^scsl="PN",0,<password>.')
        test.expect(test.dut.dstl_unlock_network_personalization(test.password))

        test.log.step('6. Restart module, module can register to network after entering pin.')
        test.dut.dstl_restart()
        test.sleep(2)
        test.dut.at1.send_and_verify(f'AT+CPIN="{test.dut.sim.pin1}"')
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('AT+CPIN?', 'READY'))
        test.sleep(5)
        test.attempt(test.dut.at1.send_and_verify, 'AT+COPS?', '\d,\d,".+?",\d', retry=5, sleep=5)

        test.log.step('7. Enable the PN lock with at^scsl="PN",1,<password>,<data>; '
                      '(U)SIM\'s MCCMNC should not in the data field')
        test.expect(test.dut.dstl_lock_network_personalization(test.password, "999.99"))

        test.log.step('8. Check the module behavior.')
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "PH\-NET PIN"))

        test.log.step('9. restart module and check the module require PN password'
                      '("at+cpin?" return "PH-SIM PIN")')
        test.dut.dstl_restart()
        test.sleep(2)
        test.dut.at1.send_and_verify(f'AT+CPIN="{test.dut.sim.pin1}"')
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "PH\-NET PIN"))

        test.log.step('10. Try to unlock the PN lock with at^scsl and incorrect password 3 times '
                      '(10 times will block device and can\'t be unblocked)')
        for i in range(3):
            test.expect(test.dut.dstl_unlock_network_personalization("12345678",
                                                                 expect_response="\+CME ERROR: operation failed"))

        test.log.step('11. Check the PN lock status with at+cpin? ("at+cpin?" return "PH-SIM PIN")')
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "PH\-NET PIN"))

        test.log.step('12. Try to unlock the PN lock with at^scsl and correct password')
        test.expect(test.dut.dstl_unlock_network_personalization(test.password))

        test.log.step('13. Check the PN lock status with at+cpin? ("at+cpin?" return READY)')
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "READY"))

        test.log.step('14. Check the module register on network')
        test.attempt(test.dut.at1.send_and_verify, 'AT+COPS?', '\d,\d,".+?",\d', retry=5, sleep=5)

    def cleanup(test):
        test.expect(test.dut.dstl_unlock_network_personalization(test.password))


if '__main__' == __name__:
    unicorn.main()