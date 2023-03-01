#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0000396.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.network_service import register_to_network
from dstl.configuration import set_autoattach
from dstl.call.setup_voice_call import dstl_is_voice_call_supported


class CeerFunction(BaseTest):
    '''
    TC0000396.002  Ceer
    Intention: Check extended error reports for different scenarios.
    Subscriber: 2
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.dut.dstl_enable_ps_autoattach()
        test.dut.dstl_restart()
        test.sleep(3)

    def run(test):

        test.log.step('1.last GPRS detach:at+cgatt=0 (+CEER: 5,0,0)')
        test.dut.dstl_register_to_network()

        test.attempt(test.dut.at1.send_and_verify, 'at+cgatt?', expect='CGATT: 1', sleep=5, retry=5)
        test.sleep(5)
        test.dut.at1.send_and_verify('at+cgatt=0', 'OK')
        test.expect(test.dut.at1.send_and_verify('at+ceer', 'CEER: 5,0,0'))
        test.sleep(5)
        test.log.step('2: last GPRS attach:at+cgatt=0 (+CEER: 4,0,0)')
        test.dut.at1.send_and_verify('at+cgatt=1', 'OK', timeout=10)
        test.expect(test.dut.at1.send_and_verify('at+ceer', 'CEER: 4,0,0'))

        test.log.step('3.atd*99# (+CEER: 2,0,0)')
        test.dut.at1.send_and_verify('atd*99#', expect='.*CONNECT.*')
        #test.expect(test.dut.at2.send_and_verify('at+ceer', 'CEER: 2,0,0'))
        test.dut.at1.wait_for('NO CARRIER', timeout=180)

        test.log.step('4: Dial up release (+CEER: 3,0,0)')
        test.expect(test.dut.at1.send_and_verify('at+ceer', 'CEER: 3,0,0'))

        if(test.dut.dstl_is_voice_call_supported()):
            test.step5to14()
        else:
            test.log.info('Not support call function, test finished.')

    def cleanup(test):
        pass

    def step5to14(test):
        test.dut.at1.send_and_verify('at^sm20=0', 'OK|ERROR')
        test.log.step('5: Subscriber1 tries to make a voice call with a not existing number ')
        test.dut.at1.send_and_verify('atd9876543210;')
        test.dut.at1.wait_for('NO CARRIER|NO ANSWER', timeout=180)
        test.expect(test.dut.at1.send_and_verify('at+ceer', 'CEER: 0,1,0'))
        test.sleep(30)
        test.log.step('6: Subscriber1 terminates the voice call (+CEER: 0,16,0)')
        test.dut.at1.send_and_verify('atd{};'.format(test.r1.sim.nat_voice_nr))
        test.r1.at1.wait_for('RING')
        test.dut.at1.send_and_verify('ath')
        test.expect(test.dut.at1.send_and_verify('at+ceer', 'CEER: 0,16,0'))
        test.sleep(15)
        test.log.step('7: Subscriber1 tries to make a voice call to his own (+CEER: 0,17,0)')
        test.dut.at1.send_and_verify('atd{};'.format(test.dut.sim.nat_voice_nr))
        test.dut.at1.wait_for('BUSY')
        test.expect(test.dut.at1.send_and_verify('at+ceer', 'CEER: 0,17,0'))
        test.sleep(15)
        test.log.step('8: Reset module of Subscriber2 to ensure that Subscriber2 is not booked in to the network and'
                      ' Subscriber1 tries to make a voice call to Subscriber2 (+CEER: 0,18,0);')
        test.r1.dstl_restart()
        test.dut.at1.send_and_verify('atd{};'.format(test.r1.sim.nat_voice_nr))
        test.dut.at1.wait_for('NO CARRIER')
        test.expect(test.dut.at1.send_and_verify('at+ceer', 'CEER: 0,18,0'))

        test.log.step('9:Subscriber1 tries to make a voice call to Subscriber2, but Subscreiber 2 '
                      'does not answer the call (+CEER: 0,19,0)')
        test.r1.dstl_register_to_network()
        test.dut.at1.send_and_verify('atd{};'.format(test.r1.sim.nat_voice_nr))
        test.dut.at1.wait_for('NO CARRIER|NO ANSWER',timeout=180)
        test.expect(test.dut.at1.send_and_verify('at+ceer', 'CEER: 0,19,0'))

        test.log.step('10: Subscriber1 tries to make a voice call to Subscriber2, Subscriber2 rejects the call (+CEER: 0,21,0);')
        test.dut.at1.send_and_verify('atd{};'.format(test.r1.sim.nat_voice_nr))
        test.r1.at1.wait_for('RING')
        test.r1.at1.send_and_verify('ath')
        test.expect(test.dut.at1.send_and_verify('at+ceer', 'CEER: 0,21,0'))

        test.log.step('11: Subscriber1 tries to make a call with an incomplete number (+CEER: 0,28,0);')
        test.dut.at1.send_and_verify('atd{};'.format(test.r1.sim.nat_voice_nr[:9]))
        test.expect(test.dut.at1.send_and_verify('at+ceer', 'CEER: 0,28,0'))

        test.log.step('12: Subscriber1 tries to call number of Subscriber2 who is not part of the FDN list (+CEER: 0,9,0)')
        #pending

        test.log.step('13: Call setup is terminated with NO CARRIER(+CEER: 0,31,0);')
        test.dut.at1.send_and_verify('at+cops=2')
        test.dut.at1.send_and_verify('atd{};'.format(test.r1.sim.nat_voice_nr),wait_for='NO CARRIER')
        test.expect(test.dut.at1.send_and_verify('at+ceer', 'CEER: 0,31,0'))
        test.dut.at1.send_and_verify('at+cops=0')
        test.sleep(5)

        test.log.step('14: Hash code to active Supplementary Service, such as:atd*21*123*456#(+CEER: 0,28,0)')
        test.dut.at1.send_and_verify('atd*21*123*456#')
        test.expect(test.dut.at1.send_and_verify('at+ceer', 'CEER: 0,28,0'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=4,0','O'))





if "__main__" == __name__:
    unicorn.main()
