# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0091902.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call import setup_voice_call
from dstl.call import get_release_cause


class Test(BaseTest):
    """
    TC0091902.001 - TpAtShupBasic
    Intention: This procedure provides basic tests for the command AT^SHUP.
    Subscriber: 2
    """
    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.dut.dstl_restart()
        test.r1.dstl_restart()
        test.sleep(3)
        test.r1.dstl_register_to_network()

    def run(test):
        nat_dut_phone_num = test.dut.sim.nat_voice_nr

        shup_cause = {1: '.*Unassigned \\(unallocated\\) number.*|.*Unassigned/unallocated number.*',
                      16: '.*normal call clearing.*|.*Normal call clearing.*',
                      17: '.*User busy.*',
                      18: '.*No user responding.*',
                      21: '.*Call rejected.*',
                      27: '.*Destination out of order.*',
                      31: '.*Normal, unspecified.*',
                      88: '.*incompatible destination.*|.*Incompatible destination.*',
                      128: '.*Normal call clearing.*|.*Call rejected.*'}

        support_cause = test.dut.dstl_get_supported_release_cause()

        test.log.info('1. Check AT command without PIN.')
        test.expect(test.dut.at1.send_and_verify('at+cpin?', 'SIM PIN'))
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^shup=?', 'CME ERROR: SIM PIN required'))
        test.expect(test.dut.at1.send_and_verify('at^shup', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at^shup?', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at^shup=1', 'ERROR'))

        test.log.info('2. check command with PIN.')
        test.dut.dstl_register_to_network()
        test.expect(test.dut.at1.send_and_verify('at^shup=?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^shup', 'O'))
        test.expect(test.dut.at1.send_and_verify('at^shup?', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at^shup=1', 'O'))

        test.log.info('3. functional test with MT voice calls.')

        for cause in support_cause:
            test.expect(test.dut.at1.send_and_verify('AT+CEER=0', 'OK'))
            test.log.info(f'\nCheck SHUP={cause}.')
            test.setup_call(nat_dut_phone_num)
            test.expect(test.dut.at1.send_and_verify(f'AT^SHUP={cause}', 'OK'))
            test.expect(test.r1.at1.wait_for('BUSY|NO CARRIER', 310))  # testnetwork Berlin runs 5 minutes voice message
            test.sleep(2)
            test.expect(test.r1.at1.send_and_verify('AT+CEER', '.*\+CEER: '+shup_cause[cause]+'.*OK.*'))
            test.r1.dstl_clear_blacklist()

    def cleanup(test):
        test.log.info('***Test End***')

    def setup_call(test, number):
        test.expect(test.r1.at1.send_and_verify(f'atd{number};', ''))
        test.expect(test.dut.at1.wait_for('RING'))


if "__main__" == __name__:
    unicorn.main()
