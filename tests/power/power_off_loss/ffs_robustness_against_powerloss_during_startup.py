# responsible: lijuan.li@thalesgroup.com
# location: Beijing
# TC0095054.002 FfsRobustnessAgainstPowerLossDuringStartup

from decimal import Decimal
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.shutdown_smso import dstl_shutdown_smso
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.devboard.devboard import dstl_turn_off_vbatt_via_dev_board, dstl_turn_on_vbatt_via_dev_board, \
    dstl_turn_on_igt_via_dev_board


class Test(BaseTest):
    """
    TC0095054.002 FfsRobustnessAgainstPowerLossDuringStartup

    Check if the module is robust against unexpected loss of power during module startup.

    0. Turn off module immediately with AT^SMSO
    1. Power on DUT.
    2. Cut off power after delay. If ^SYSSTART will apear then delay = 0 ms.
    3. Power on DUT.
    4. Wait for ^SYSSTART.
    5. Switch OFF module
    Repeat all above described 100000 loops with delay increased by 1 ms.
    """

    def setup(test):
        dstl_turn_off_vbatt_via_dev_board(test.dut)
        test.sleep(1)
        dstl_turn_on_vbatt_via_dev_board(test.dut)
        dstl_turn_on_igt_via_dev_board(test.dut)
        test.dut.devboard.wait_for('SYSSTART')
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_bootloader(test.dut)
        test.expect(dstl_enter_pin(test.dut))

    def run(test):
        test.log.step("0. Turn off module immediately with AT^SMSO")
        test.expect(dstl_shutdown_smso(test.dut))
        test.sleep(1)

        delay = 0
        loop = 1
        while loop < 100001:
            test.log.step('Loop: {}'.format(loop) + ' with  ' + 'delay: {}'.format(delay * 1000) + 'ms')
            test.log.step("1. Power on DUT")
            dstl_turn_off_vbatt_via_dev_board(test.dut)
            test.sleep(1)
            test.dut.devboard.send_and_verify("MC:VBATT=ON", ".*OK.*")
            test.dut.devboard.send_and_verify("MC:IGT=555", ".*OK.*")
            sysstart_ready = test.dut.at1.wait_for('SYSSTART', delay)
            if sysstart_ready:
                delay = 0
            else:
                test.log.step("2. Cut off power after delay.")
                dstl_turn_off_vbatt_via_dev_board(test.dut)
                test.sleep(1)
                test.log.step("3. Power on DUT")
                dstl_turn_on_vbatt_via_dev_board(test.dut)
                dstl_turn_on_igt_via_dev_board(test.dut)
                test.log.step("4. Wait for SYSSTART")
                test.dut.devboard.wait_for('SYSSTART')
                test.sleep(1)
                test.log.step("5. Switch OFF module")
                test.expect(dstl_shutdown_smso(test.dut))
                delay = Decimal(str(delay)) + Decimal(str(0.01))
            loop = loop + 1

    def cleanup(test):
        test.log.step("Clean Up")
        dstl_turn_off_vbatt_via_dev_board(test.dut)
        test.sleep(1)
        dstl_turn_on_vbatt_via_dev_board(test.dut)
        dstl_turn_on_igt_via_dev_board(test.dut)
        test.expect(test.dut.at1.wait_for('.*SYSSTART.*'))


if __name__ == "__main__":
    unicorn.main()