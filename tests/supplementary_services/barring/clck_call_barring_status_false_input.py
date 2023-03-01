#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0084432.001, TC0084432.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.security import lock_unlock_sim


class Test(BaseTest):
    """
    TC0084432.001,TC0084432.002 - TpCclckCallBarringFalseInput
    Intention:
        Call barring status test
    Steps: Loop the following tests for all Call barring related commands:'AO', 'OI', 'OX', 'AI', 'IR', 'AB', 'AC', 'AG'
           1. Wrong mode (3)/(2)&(1)
           2. Wrong password (98yz)
           3. Wrong class (256)
           4. Wrong class (0)
           5. Wrong class (string)
    """

    def setup(test):
        test.expect(hasattr(test.dut.sim, 'pin1_net') and test.dut.sim.pin1_net, critical=True,
                    msg='Property "pin1_net" is required for SIM.')
        test.dut.dstl_detect()
        test.dut.dstl_register_to_network()  # including cmee=2
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2"))
        test.sleep(5)

    def run(test):
        all_barri_facilities = ['AO', 'OI', 'OX', 'AI', 'IR', 'AB', 'AC', 'AG']
        test.ab_facilities = ['AB', 'AC', 'AG']
        test.log.step("1. Disable all previously active call barrings")
        test.expect(test.dut.dstl_lock_unlock_facility(facility="AB", lock=False, classes='255'))
        for facility in all_barri_facilities:
            test.log.step("2. Wrong Mode (3) - +CME ERROR: invalid index")
            test.expect(
                test.facility_lock(facility, mode=3, password=test.dut.sim.pin1_net, classes=255,
                                   expect_result='\+CME ERROR: invalid index'))
            test.expect(test.check_facility_is_not_lock(facility))
            if facility in test.ab_facilities:
                test.log.step("2.1 Wrong Mode (1) - +CME ERROR: invalid index")
                test.expect(
                    test.facility_lock(facility, mode=1, password=test.dut.sim.pin1_net, classes=255,
                                       expect_result='\+CME ERROR: invalid index'))
                test.log.step("2.2 Wrong Mode (2) - +CME ERROR: invalid index")
                test.expect(
                    test.facility_lock(facility, mode=2, password=test.dut.sim.pin1_net, classes=255,
                                       expect_result='\+CME ERROR: invalid index'))

            test.log.step("3. Wrong Password (98yz) - +CME ERROR: incorrect password")
            if facility in test.ab_facilities:
                test.expect(test.facility_lock(facility, mode=0, password='98yz', classes=255,
                                               expect_result='\+CME ERROR: incorrect password'))
            else:
                test.expect(test.facility_lock(facility, mode=1, password='98yz', classes=255,
                                               expect_result='\+CME ERROR: incorrect password'))
            test.expect(test.check_facility_is_not_lock(facility))

            test.log.step("4. Wrong Class (256) - +CME ERROR: incorrect password")
            test.expect(
                test.facility_lock(facility, mode=1, password=test.dut.sim.pin1_net, classes=256,
                                   expect_result='\+CME ERROR: invalid index'))
            test.expect(test.check_facility_is_not_lock(facility))

            test.log.step("5. Wrong Class (0) - +CME ERROR: incorrect password")
            test.expect(test.facility_lock(facility, mode=1, password=test.dut.sim.pin1_net, classes=0,
                                           expect_result='\+CME ERROR: invalid index'))
            test.expect(test.check_facility_is_not_lock(facility))

            test.log.step("6. Wrong Class (string) - +CME ERROR: incorrect password")
            test.expect(
                test.facility_lock(facility, mode=1, password=test.dut.sim.pin1_net, classes='abc',
                                   expect_result='\+CME ERROR: invalid index'))
            test.expect(test.check_facility_is_not_lock(facility))

    def cleanup(test):
        if hasattr(test.dut, 'sim.pin1_net') and test.dut.sim.pin1_net:
            test.dut.dstl_lock_unlock_facility(facility="AB", lock=False, classes='255')

    def facility_lock(test, facility, mode, password, classes, expect_result):
        result = test.dut.at1.send_and_verify(f'AT+CLCK="{facility}",{mode},"{password}",{classes}',
                                              expect_result)
        return result

    def check_facility_is_not_lock(test, facility):
        if facility in test.ab_facilities:
            result = True
            test.log.info("{facility} does not support mode 2.")
        else:
            result = test.dut.dstl_query_facility_lock_status(facility, None, 255)
        return result


if '__main__' == __name__:
    unicorn.main()


