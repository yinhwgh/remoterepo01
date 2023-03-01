#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0093324.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call import setup_voice_call

class Test(BaseTest):
    '''
    TC0093324.001 - CallHoldJustAfterTerminatingParty
    Test case covers scenario reported in IPIS100133783.
    Subscriber: 2
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(3)
        test.dut.dstl_register_to_network()
        test.r1.dstl_register_to_network()

    def run(test):
        nat_dut_phone_num = test.dut.sim.nat_voice_nr

        test.log.step('1. Check command (AT+CHLD=?)')
        test.expect(test.dut.at1.send_and_verify('AT+CHLD=?', '.*\+CHLD:.*'))
        test.expect(test.r1.at1.send_and_verify('AT^SM20=0', 'O'))
        for i in range(1,6):
            test.log.info(f'*** Start Test LOOP {i}/5 ***')

            test.log.step('2. Establish incoming call connection to the DUT')
            test.expect(test.r1.at1.send_and_verify(f'ATD{nat_dut_phone_num};', '.*'))

            test.log.step('3. Wait for "RING"')
            test.expect(test.dut.at1.wait_for('RING', timeout=60))

            test.log.step('4. Connect to incoming call (ATA)')
            test.expect(test.dut.at1.send_and_verify('ATA', 'OK'))

            test.log.step('5. Check connection status using AT^SLCC or AT+CLCC')
            test.sleep(2)
            test.expect(test.dut.at1.send_and_verify("AT+CLCC", "\+CLCC: 1,1,0,0,0.*"))
            test.expect(test.r1.at1.send_and_verify("AT+CLCC", "\+CLCC: 1,0,0,0,0.*"))

            test.log.step('6. Place active connection on hold (AT+CHLD=2)')
            test.expect(test.dut.at1.send_and_verify('AT+CHLD=2', 'OK'))
            test.sleep(2)
            test.log.step('7. Check connection status using AT^SLCC or AT+CLCC')
            test.expect(test.dut.at1.send_and_verify("AT+CLCC", "\+CLCC: 1,1,1,0,0.*"))

            test.log.step('8. Terminate all active connections on remote (AT+CHUP) and as quickly as possible (<0.5 s.) terminate the connection on DUT using AT+CHLD=1.')
            test.expect(test.r1.dstl_release_call())
            test.expect(test.dut.at1.send_and_verify("AT+CHLD=1", "O"))

            test.log.step('9. All active calls should be terminated (AT^SLCC or AT+CLCC).')
            test.expect(test.dut.at1.send_and_verify("AT+CLCC", "^(?!.*\+CLCC:).*$"))

            test.log.step('10. Check if DUT is responsive (enter AT into terminal).')
            test.expect(test.dut.at1.send_and_verify("AT", "OK"))
            test.expect(test.r1.dstl_release_call())
            test.expect(test.dut.dstl_release_call())

            test.log.step('11. If DUT is responsive, try to establish an incoming call to the DUT again.')
            test.expect(test.r1.at1.send_and_verify(f'ATD{nat_dut_phone_num};', '.*'))

            test.log.step('12. Wait for "RING" on DUT')
            test.expect(test.dut.at1.wait_for('RING', timeout=60))

            test.log.step('13. Connect to incoming call (ATA).')
            test.expect(test.dut.at1.send_and_verify('ATA', 'OK'))

            test.log.step('14.Check if DUT is responsive, if yes, this test should be repeated several times.')
            test.expect(test.dut.at1.send_and_verify("AT", "OK"))
            test.expect(test.r1.dstl_release_call())
            test.expect(test.dut.dstl_release_call())



    def cleanup(test):

        pass



if "__main__" == __name__:
    unicorn.main()

