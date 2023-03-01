# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0091654.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call import setup_voice_call
from dstl.supplementary_services import ccfc_set_by_starhash


class Test(BaseTest):
    '''
    TC0091654.001 - TpCatdCcfcFunc
    Intention: Testing functionality of Call forwarding via Star-hash codes.
    Subscriber: 4
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(3)
        test.r1.dstl_detect()
        test.r1.dstl_register_to_network()
        test.sleep(3)
        test.r2.dstl_detect()
        test.r2.dstl_register_to_network()
        test.sleep(3)
        test.r3.dstl_detect()
        test.r3.dstl_register_to_network()
        test.sleep(3)
        test.nat_dut_phone_num = test.dut.sim.nat_voice_nr
        test.nat_r1_phone_num = test.r1.sim.nat_voice_nr
        test.nat_r2_phone_num = test.r2.sim.nat_voice_nr
        test.nat_r3_phone_num = test.r3.sim.nat_voice_nr

        test.active_urc = f'.*CCFC: 1,1.*{test.nat_r2_phone_num}.*OK.*'
        test.deactive_urc_with_num = f'.*CCFC: 0,1.*{test.nat_r2_phone_num}.*OK.*'
        test.erase_all_urc = '.*CCFC: 0,1.*OK.*|.*CCFC: 0,255.*OK.*'

    def run(test):
        test.log.step('1. Attach modules to the network.')
        test.dut.dstl_register_to_network()
        test.log.step('2. Erase all call forwardings on all modules (ATD#002***#;)')
        test.expect(test.dut.dstl_erase_all_cf())
        test.log.step('3. Check status of DUT call forwarding (ATD*#002**#;).')
        test.expect(test.dut.dstl_check_cf_status(reason=4, expect_response='.*CCFC: 0,1.*OK.*|ERROR'))
        test.log.step(
            '4. Check status of DUT call forwarding via AT-Command (AT+CCFC=0,2; AT+CCFC=1,2; AT+CCFC=2,2) for comparison.')
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=0,2', '.*CCFC: 0,1.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=1,2', '.*CCFC: 0,1.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=2,2', '.*CCFC: 0,1.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=3,2', '.*CCFC: 0,1.*OK.*'))

        test.log.step('5.For each supported class,each reason:')
        # for viper, only test class 1 here
        test.log.info('5.0 Start test class 1, reason 0')
        test.check_cf_uncondition()
        test.log.info('5.1 Start test class 1, reason 1')
        test.check_cf_busy()
        test.log.info('5.2 Start test class 1, reason 2')
        test.check_cf_noreply()
        test.log.info('5.3 Start test class 1, reason 3')
        test.check_cf_noreach()
        test.log.info('5.4 Start test class 1, reason 4')
        test.check_cf_all_cf()
        test.log.info('5.5 Start test class 1, reason 5')
        test.check_cf_all_condition_cf()

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=4,0', 'OK|ERROR'))
        test.expect(test.r1.at1.send_and_verify('AT+CCFC=4,0', 'OK|ERROR'))
        test.expect(test.r2.at1.send_and_verify('AT+CCFC=4,0', 'OK|ERROR'))
        test.expect(test.r3.at1.send_and_verify('AT+CCFC=4,0', 'OK|ERROR'))

    def check_cf_uncondition(test):
        test.log.step('a) Register Call forwardring on DUT for specified reason, \
                            with specified class and with AUX2 number, using Star-hash code.')
        test.expect(test.dut.dstl_reg_cf_with_number(0, test.nat_r2_phone_num))
        test.log.step('b) Check status with star-hash code')
        test.expect(test.dut.dstl_check_cf_status(reason=0, expect_response=test.active_urc))
        test.log.step('c) Check status with AT+CCFC command for comparison')
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=0,2', test.active_urc))
        test.log.step('d) Dial AUX1->DUT with specified type of call and reason conditions.')
        test.r1.at1.send_and_verify(f'ATD{test.nat_dut_phone_num};', '')
        test.log.step('e) Check if call forwarding works as described by reason')
        test.expect(test.r2.at1.wait_for('RING', timeout=60))
        test.expect(test.dut.dstl_release_call())
        test.expect(test.r1.dstl_release_call())
        test.expect(test.r2.dstl_release_call())

        test.log.step('f) Disable call forwarding for this class and reason via star-hash code.')
        test.expect(test.dut.dstl_deact_cf(reason=0))
        test.log.step(
            'g) Check if specified call forwarding is disabled and number is still registered, using star-hash code')
        test.expect(test.dut.dstl_check_cf_status(reason=0, expect_response=test.deactive_urc_with_num))
        test.log.step('h) For comparison check perform step g), using AT+CCFC command.')
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=0,2', test.deactive_urc_with_num))

        test.log.step('i) Check status of all classes (255) and reasons via star-hash code.')
        test.expect(test.dut.dstl_check_cf_status(reason=0, pclass=255, expect_response=test.deactive_urc_with_num))
        test.log.step('j) Check status of all classes (255) and reasons via AT+CCFC command, for comparison')
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=0,2,,,255', expect_response=test.deactive_urc_with_num))

        test.log.step('k) Erase number from call forwarding service, using star-hash code.')
        test.expect(test.dut.dstl_erase_all_cf())
        test.log.step('l) Check status of all classes (255) and reasons via star-hash code.')
        test.expect(test.dut.dstl_check_cf_status(reason=0, pclass=255, expect_response=test.erase_all_urc))
        test.log.step('m) Check status of all classes (255) and reasons via AT+CCFC command, for comparison.')
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=0,2,,,255', expect_response=test.erase_all_urc))

    def check_cf_busy(test):
        test.log.step('a) Register Call forwardring on DUT for specified reason, \
                            with specified class and with AUX2 number, using Star-hash code.')
        test.expect(test.dut.dstl_reg_cf_with_number(1, test.nat_r2_phone_num))
        test.log.step('b) Check status with star-hash code')
        test.expect(test.dut.dstl_check_cf_status(reason=1, expect_response=test.active_urc))
        test.log.step('c) Check status with AT+CCFC command for comparison')
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=1,2', test.active_urc))
        test.log.step('d) Dial AUX1->DUT with specified type of call and reason conditions.')
        test.expect(test.dut.dstl_voice_call_by_number(test.r3, test.nat_r3_phone_num))
        test.sleep(5)
        test.r1.at1.send_and_verify(f'ATD{test.nat_dut_phone_num};', '')

        test.log.step('e) Check if call forwarding works as described by reason')
        test.expect(test.r2.at1.wait_for('RING', timeout=90))
        test.expect(test.r1.dstl_release_call())
        test.expect(test.r2.dstl_release_call())
        test.expect(test.dut.dstl_release_call())
        test.log.step('f) Disable call forwarding for this class and reason via star-hash code.')
        test.expect(test.dut.dstl_deact_cf(reason=1))
        test.log.step(
            'g) Check if specified call forwarding is disabled and number is still registered, using star-hash code')
        test.expect(test.dut.dstl_check_cf_status(reason=1, expect_response=test.deactive_urc_with_num))
        test.log.step('h) For comparison check perform step g), using AT+CCFC command.')
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=1,2', test.deactive_urc_with_num))

        test.log.step('i) Check status of all classes (255) and reasons via star-hash code.')
        test.expect(test.dut.dstl_check_cf_status(reason=1, pclass=255, expect_response=test.deactive_urc_with_num))
        test.log.step('j) Check status of all classes (255) and reasons via AT+CCFC command, for comparison')
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=1,2,,,255', expect_response=test.deactive_urc_with_num))

        test.log.step('k) Erase number from call forwarding service, using star-hash code.')
        test.expect(test.dut.dstl_erase_all_cf())
        test.log.step('l) Check status of all classes (255) and reasons via star-hash code.')
        test.expect(test.dut.dstl_check_cf_status(reason=1, pclass=255, expect_response=test.erase_all_urc))
        test.log.step('m) Check status of all classes (255) and reasons via AT+CCFC command, for comparison.')
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=1,2,,,255', expect_response=test.erase_all_urc))

    def check_cf_noreply(test):
        test.log.step('a) Register Call forwardring on DUT for specified reason, \
                                    with specified class and with AUX2 number, using Star-hash code.')
        test.expect(test.dut.dstl_reg_cf_with_number(2, test.nat_r2_phone_num, pclass=1, time=30))
        test.log.step('b) Check status with star-hash code')
        test.expect(test.dut.dstl_check_cf_status(reason=2, expect_response=test.active_urc))
        test.log.step('c) Check status with AT+CCFC command for comparison')
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=2,2', test.active_urc))
        test.log.step('d) Dial AUX1->DUT with specified type of call and reason conditions.')
        test.r1.at1.send_and_verify(f'ATD{test.nat_dut_phone_num};', '')

        test.log.step('e) Check if call forwarding works as described by reason')
        test.expect(test.r2.at1.wait_for('RING', timeout=120))
        test.expect(test.r1.dstl_release_call())
        test.expect(test.r2.dstl_release_call())
        test.expect(test.dut.dstl_release_call())
        test.log.step('f) Disable call forwarding for this class and reason via star-hash code.')
        test.expect(test.dut.dstl_deact_cf(reason=2))
        test.log.step(
            'g) Check if specified call forwarding is disabled and number is still registered, using star-hash code')
        test.expect(test.dut.dstl_check_cf_status(reason=2, expect_response=test.deactive_urc_with_num))
        test.log.step('h) For comparison check perform step g), using AT+CCFC command.')
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=2,2', test.deactive_urc_with_num))

        test.log.step('i) Check status of all classes (255) and reasons via star-hash code.')
        test.expect(test.dut.dstl_check_cf_status(reason=2, pclass=255, expect_response=test.deactive_urc_with_num))
        test.log.step('j) Check status of all classes (255) and reasons via AT+CCFC command, for comparison')
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=2,2,,,255', expect_response=test.deactive_urc_with_num))

        test.log.step('k) Erase number from call forwarding service, using star-hash code.')
        test.expect(test.dut.dstl_erase_all_cf())
        test.log.step('l) Check status of all classes (255) and reasons via star-hash code.')
        test.expect(test.dut.dstl_check_cf_status(reason=2, pclass=255, expect_response=test.erase_all_urc))
        test.log.step('m) Check status of all classes (255) and reasons via AT+CCFC command, for comparison.')
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=2,2,,,255', expect_response=test.erase_all_urc))

    def check_cf_noreach(test):
        test.log.step('a) Register Call forwardring on DUT for specified reason, \
                                    with specified class and with AUX2 number, using Star-hash code.')
        test.expect(test.dut.dstl_reg_cf_with_number(3, test.nat_r2_phone_num))
        test.log.step('b) Check status with star-hash code')
        test.expect(test.dut.dstl_check_cf_status(reason=3, expect_response=test.active_urc))
        test.log.step('c) Check status with AT+CCFC command for comparison')
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=3,2', test.active_urc))
        test.log.step('d) Dial AUX1->DUT with specified type of call and reason conditions.')
        test.expect(test.dut.at1.send_and_verify('AT+COPS=2', 'OK'))
        test.sleep(2)
        test.r1.at1.send_and_verify(f'ATD{test.nat_dut_phone_num};', '')
        test.log.step('e) Check if call forwarding works as described by reason')
        test.expect(test.r2.at1.wait_for('RING', timeout=90))
        test.expect(test.r1.dstl_release_call())
        test.expect(test.r2.dstl_release_call())
        test.dut.dstl_register_to_network()
        test.sleep(5)
        test.log.step('f) Disable call forwarding for this class and reason via star-hash code.')
        test.expect(test.dut.dstl_deact_cf(reason=3))
        test.log.step(
            'g) Check if specified call forwarding is disabled and number is still registered, using star-hash code')
        test.expect(test.dut.dstl_check_cf_status(reason=3, expect_response=test.deactive_urc_with_num))
        test.log.step('h) For comparison check perform step g), using AT+CCFC command.')
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=3,2', test.deactive_urc_with_num))

        test.log.step('i) Check status of all classes (255) and reasons via star-hash code.')
        test.expect(test.dut.dstl_check_cf_status(reason=3, pclass=255, expect_response=test.deactive_urc_with_num))
        test.log.step('j) Check status of all classes (255) and reasons via AT+CCFC command, for comparison')
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=3,2,,,255', expect_response=test.deactive_urc_with_num))

        test.log.step('k) Erase number from call forwarding service, using star-hash code.')
        test.expect(test.dut.dstl_erase_all_cf())
        test.log.step('l) Check status of all classes (255) and reasons via star-hash code.')
        test.expect(test.dut.dstl_check_cf_status(reason=3, pclass=255, expect_response=test.erase_all_urc))
        test.log.step('m) Check status of all classes (255) and reasons via AT+CCFC command, for comparison.')
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=3,2,,,255', expect_response=test.erase_all_urc))

    def check_cf_all_cf(test):
        test.log.step('a) Register Call forwardring on DUT for specified reason, \
                                    with specified class and with AUX2 number, using Star-hash code.')
        test.expect(test.dut.dstl_reg_cf_with_number(4, test.nat_r2_phone_num, pclass=1, time=30))
        test.log.step('b) Check status with star-hash code')
        # error
        test.expect(test.dut.dstl_check_cf_status(reason=4, expect_response=test.active_urc))
        test.log.step('c) Check status with AT+CCFC command for comparison')
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=0,2', test.active_urc))
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=1,2', test.active_urc))
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=2,2', test.active_urc))
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=3,2', test.active_urc))
        test.log.step('d) Dial AUX1->DUT with specified type of call and reason conditions.')

        test.sleep(2)
        test.r1.at1.send_and_verify(f'ATD{test.nat_dut_phone_num};')
        test.log.step('e) Check if call forwarding works as described by reason')
        test.expect(test.r2.at1.wait_for('RING', timeout=90))
        test.expect(test.r1.dstl_release_call())
        test.expect(test.r2.dstl_release_call())

        test.log.step('f) Disable call forwarding for this class and reason via star-hash code.')
        test.expect(test.dut.dstl_deact_cf(reason=4))
        test.log.step(
            'g) Check if specified call forwarding is disabled and number is still registered, using star-hash code')
        # error
        test.expect(test.dut.dstl_check_cf_status(reason=4, expect_response=test.deactive_urc_with_num))
        test.log.step('h) For comparison check perform step g), using AT+CCFC command.')
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=0,2', test.deactive_urc_with_num))
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=1,2', test.deactive_urc_with_num))
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=2,2', test.deactive_urc_with_num))
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=3,2', test.deactive_urc_with_num))

        test.log.step('i) Check status of all classes (255) and reasons via star-hash code.')
        # error
        test.expect(test.dut.dstl_check_cf_status(reason=4, pclass=255, expect_response=test.deactive_urc_with_num))
        test.log.step('j) Check status of all classes (255) and reasons via AT+CCFC command, for comparison')
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=0,2,,,255', expect_response=test.deactive_urc_with_num))
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=1,2,,,255', expect_response=test.deactive_urc_with_num))
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=2,2,,,255', expect_response=test.deactive_urc_with_num))
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=3,2,,,255', expect_response=test.deactive_urc_with_num))


        test.log.step('k) Erase number from call forwarding service, using star-hash code.')
        test.expect(test.dut.dstl_erase_all_cf())
        test.log.step('l) Check status of all classes (255) and reasons via star-hash code.')
        # error
        test.expect(test.dut.dstl_check_cf_status(reason=4, pclass=255, expect_response=test.erase_all_urc))
        test.log.step('m) Check status of all classes (255) and reasons via AT+CCFC command, for comparison.')
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=0,2,,,255', expect_response=test.erase_all_urc))
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=1,2,,,255', expect_response=test.erase_all_urc))
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=2,2,,,255', expect_response=test.erase_all_urc))
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=3,2,,,255', expect_response=test.erase_all_urc))

    def check_cf_all_condition_cf(test):
        test.log.step('a) Register Call forwardring on DUT for specified reason, \
                                    with specified class and with AUX2 number, using Star-hash code.')
        test.expect(test.dut.dstl_reg_cf_with_number(5, test.nat_r2_phone_num, pclass=1, time=30))
        test.log.step('b) Check status with star-hash code')
        # error
        test.expect(test.dut.dstl_check_cf_status(reason=5, expect_response=test.active_urc))
        test.log.step('c) Check status with AT+CCFC command for comparison')
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=0,2', test.erase_all_urc))
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=1,2', test.active_urc))
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=2,2', test.active_urc))
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=3,2', test.active_urc))
        test.log.step('d) Dial AUX1->DUT with specified type of call and reason conditions.')
        test.expect(test.dut.at1.send_and_verify('AT+COPS=2', 'OK'))
        test.sleep(2)
        test.r1.at1.send_and_verify(f'ATD{test.nat_dut_phone_num};', '')

        test.log.step('e) Check if call forwarding works as described by reason')
        test.expect(test.r2.at1.wait_for('RING', timeout=90))
        test.expect(test.r1.dstl_release_call())
        test.expect(test.r2.dstl_release_call())
        test.dut.dstl_register_to_network()
        test.sleep(5)
        test.log.step('f) Disable call forwarding for this class and reason via star-hash code.')
        test.expect(test.dut.dstl_deact_cf(reason=5))
        test.log.step(
            'g) Check if specified call forwarding is disabled and number is still registered, using star-hash code')
        # error
        test.expect(test.dut.dstl_check_cf_status(reason=5, expect_response=test.deactive_urc_with_num))
        test.log.step('h) For comparison check perform step g), using AT+CCFC command.')
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=0,2', test.erase_all_urc))
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=1,2', test.deactive_urc_with_num))
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=2,2', test.deactive_urc_with_num))
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=3,2', test.deactive_urc_with_num))

        test.log.step('i) Check status of all classes (255) and reasons via star-hash code.')
        # error
        test.expect(test.dut.dstl_check_cf_status(reason=5, pclass=255, expect_response=test.deactive_urc_with_num))
        test.log.step('j) Check status of all classes (255) and reasons via AT+CCFC command, for comparison')
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=0,2,,,255', test.erase_all_urc))
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=1,2,,,255', expect_response=test.deactive_urc_with_num))
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=2,2,,,255', expect_response=test.deactive_urc_with_num))
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=3,2,,,255', expect_response=test.deactive_urc_with_num))

        test.log.step('k) Erase number from call forwarding service, using star-hash code.')
        test.expect(test.dut.dstl_erase_all_cf())
        test.log.step('l) Check status of all classes (255) and reasons via star-hash code.')
        # error
        test.expect(test.dut.dstl_check_cf_status(reason=5, pclass=255, expect_response=test.erase_all_urc))
        test.log.step('m) Check status of all classes (255) and reasons via AT+CCFC command, for comparison.')
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=0,2,,,255', test.erase_all_urc))
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=1,2,,,255', expect_response=test.erase_all_urc))
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=2,2,,,255', expect_response=test.erase_all_urc))
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=3,2,,,255', expect_response=test.erase_all_urc))


if "__main__" == __name__:
    unicorn.main()
