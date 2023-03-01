# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0091853.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call import setup_voice_call


class Test(BaseTest):
    """
    TC0091853.001 - TpAtClccBasic
    Intention: This procedure provides basic tests for the command at+clcc.
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
        int_dut_phone_num = test.dut.sim.int_voice_nr
        nat_dut_phone_num = test.dut.sim.nat_voice_nr
        int_r1_phone_num = test.r1.sim.int_voice_nr
        nat_r1_phone_num = test.r1.sim.nat_voice_nr

        test.log.info('1. Check AT command without PIN.')
        test.expect(test.dut.at1.send_and_verify('at+cpin?', 'SIM PIN'))
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+clcc=?', 'CME ERROR: SIM PIN required'))
        test.expect(test.dut.at1.send_and_verify('at+clcc', 'CME ERROR: SIM PIN required'))
        test.expect(test.dut.at1.send_and_verify('at+clcc?', 'CME ERROR: SIM PIN required|CME ERROR: unknown'))
        test.expect(test.dut.at1.send_and_verify('at+clcc=1', 'CME ERROR: SIM PIN required|CME ERROR: unknown'))

        test.log.info('2. Enter PIN and wait for registering.')
        test.dut.dstl_register_to_network()
        test.log.info('3. Check various parameters of the AT command without active call.')
        test.expect(test.dut.at1.send_and_verify('at+clcc=?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+clcc', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+clcc?', 'CME ERROR: unknown'))
        test.expect(test.dut.at1.send_and_verify('at+clcc=1', 'CME ERROR: unknown'))
        test.expect(test.dut.at1.send_and_verify('at+clcc=a', 'CME ERROR: unknown'))

        test.log.info('4. Establish MO- and MT- voice and data calls and check AT+CLCC output '
                      'for each active call and after each call.')
        # voice call
        clcc_voice_int = f'"\\{int_r1_phone_num}",145'
        clcc_voice_nat = f'"{nat_r1_phone_num}",\(128|161|129\)'

        test.log.info('4.1 test MT voice call.')
        test.expect(test.r1.at1.send_and_verify('atd{};'.format(int_dut_phone_num), '', wait_for=''))
        test.dut.at1.wait_for('RING')
        test.expect(test.dut.at1.send_and_verify('at+clcc', '.*CLCC: 1,1,4,0,0,.*OK.*'))
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify('ata'))
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify('at+clcc', f'.*\+CLCC: 1,1,0,0,0,({clcc_voice_int}|{clcc_voice_nat}).*OK.*'))
# clcc_voice_mo = '.*CLCC: 1,0,0,0,0,"\\' + int_r1_phone_num + '",145.*OK.*'
# clcc_voice_mt = '.*CLCC: 1,1,0,0,0,"' + nat_r1_phone_num + '",(128|161|129)' + '.*OK.*'
        test.expect(test.dut.at1.send_and_verify('at+chup'))
        test.expect(test.r1.at1.wait_for('.*NO CARRIER.*'))
        test.sleep(3)

        test.log.info('4.2 test MO voice call.')
        test.expect(test.dut.at1.send_and_verify('atd{};'.format(int_r1_phone_num), '', wait_for=''))
        test.r1.at1.wait_for('RING')
        test.expect(test.dut.at1.send_and_verify('at+clcc', '.*CLCC: 1,0,3,0,0,.*OK.*'))
        test.sleep(2)
        test.expect(test.r1.at1.send_and_verify('ata'))
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify('at+clcc', f'.*\+CLCC: 1,0,0,0,0,{clcc_voice_nat}.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+chup'))
        test.expect(test.r1.at1.wait_for('.*NO CARRIER.*'))

        # data call part skipped temporary because current product not support data call.
        if test.dut.dstl_is_data_call_supported():
            test.log.info('4.3 test MO data call.')
            test.log.info('4.4 test MT data call.')

    def cleanup(test):
        test.log.info('***Test End***')


if "__main__" == __name__:
    unicorn.main()
