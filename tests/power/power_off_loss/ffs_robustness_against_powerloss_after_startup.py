# responsible: lijuan.li@thalesgroup.com
# location: Beijing
# TC0102264.001, TC0102264.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.configuration.shutdown_smso import dstl_shutdown_smso
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.devboard.devboard import dstl_turn_off_vbatt_via_dev_board
from dstl.auxiliary.devboard.devboard import dstl_turn_on_vbatt_via_dev_board
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board


class Test(BaseTest):
    """
    TC0102264.002 FfsRobustnessAgainstPowerLossAfterStartup

    Check if the module is robust against unexpected loss after module module startup

    1. Power on DUT.
    2. Wait for SYSSTART.
    3. Turn off module immediately with AT^SMSO.
    4. Repeat steps 1-3 3000 times.
    5. Power on module.
    6. Wait for SYSSTART.
    7. Restart DUT immediately with AT+CFUN.
    8. Repeat steps 6-7 3000 times.
    9. Wait for SYSSTART.
    10. Cut of DUT power.
    11. Power on DUT.
    12. Wait for SYSSTART.
    13. Repeat steps 9-11 3000 times.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_bootloader(test.dut)
        test.expect(dstl_enter_pin(test.dut))

    def run(test):
        test.log.step("Preparation . Switch off module via AT^SMSO")
        test.expect(dstl_shutdown_smso(test.dut))
        test.sleep(1)
        loop = 1
        while loop < 3001:
            test.log.step('Loop: {}'.format(loop))
            test.log.step("1. Power on DUT")
            dstl_turn_on_vbatt_via_dev_board(test.dut)
            test.sleep(1)
            dstl_turn_on_igt_via_dev_board(test.dut)

            test.log.step("2. Wait for SYSSTART")
            test.expect(test.dut.at1.wait_for('.*SYSSTART.*'))
            test.sleep(1)

            test.log.step("3. Turn off module immediately with AT^SMSO")
            test.expect(test.dut.at1.send('AT^SMSO=FAST'))
            # test.expect(dstl_shutdown_smso(test.dut))
            test.sleep(10)

            test.log.step("4. Repeat step 1 to 3, 3000 times")
            loop = loop + 1

        loop = 1
        while loop < 3001:
            test.log.step('Loop: {}'.format(loop))
            test.log.step("5. Power on DUT")
            dstl_turn_on_vbatt_via_dev_board(test.dut)
            test.sleep(1)
            dstl_turn_on_igt_via_dev_board(test.dut)

            test.log.step("6. Wait for SYSSTART")
            test.expect(test.dut.at1.wait_for('.*SYSSTART.*'))
            test.sleep(1)

            test.log.step("7. Restart DUT immediately with AT+CFUN")
            dstl_restart(test.dut)

            test.log.step("8. Cut of DUT power")
            dstl_turn_off_vbatt_via_dev_board(test.dut)

            test.log.step("9. Repeat step 5 to 9, 3000 times")
            loop = loop + 1

    def cleanup(test):
        test.log.step("Power on DUT")
        dstl_turn_on_vbatt_via_dev_board(test.dut)
        test.sleep(1)
        dstl_turn_on_igt_via_dev_board(test.dut)

        test.log.step("Wait for SYSSTART")
        test.expect(test.dut.at1.wait_for('.*SYSSTART.*'))

    if __name__ == "__main__":
        unicorn.main()