# responsible: dan.liu@thalesgroup.com
# Dalian
# TC0107812.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.auxiliary.devboard.devboard import DevboardInterface
from dstl.auxiliary.devboard import gpio_on_devboard
from dstl.configuration.shutdown_smso import dstl_shutdown_smso
from tests.rq6.resmed_ehealth_initmodule_normal_flow import uc_init_module


class Test(BaseTest):
    """
    TC0107812.001_Resmed_eHealth_ShutDownModule_NormalFlow_StressTest
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_turn_off_dev_board_urcs()
        test.dut.dstl_turn_on_vbatt_via_dev_board()
        test.dut.dstl_set_gpio_direction(pin_id=3, direction="outp")
        test.expect(test.dut.dstl_set_gpio_state(pin_id=3, value=1))
        test.dut.dstl_set_urc(urc_str="PWRIND")
        uc_init_module(test, 1)

    def run(test):
        main_process(test)

    def cleanup(test):
        pass

def shutdown_by_smso(test):
    test.expect(test.dut.dstl_shutdown_smso(device_interface="at1"))
    test.expect(test.dut.devboard.wait_for("PWRIND: 1"))
    test.expect(test.dut.dstl_turn_on_igt_via_dev_board(igt_time=5000, time_to_sleep=5))
    test.expect(test.dut.at1.wait_for("^SYSSTART", timeout=35))

def shutdown_by_smso_fast(test):
    # test.expect(test.dut.dstl_shutdown_smso(device_interface="at1", fast=True))
    test.expect(test.dut.at1.send("AT^SMSO=FAST"))
    test.expect(test.dut.devboard.wait_for("PWRIND: 1"))
    test.dut.dstl_turn_on_igt_via_dev_board(igt_time=5000, time_to_sleep=5)
    test.expect(test.dut.at1.wait_for("^SYSSTART", timeout=35))

def shutdown_by_fast_shutdown_gpio(test):
    test.expect(test.dut.dstl_set_gpio_state(pin_id=3, value=0))
    test.dut.devboard.wait_for('.*PWRIND: 1.*', timeout=5)
    test.expect(test.dut.dstl_set_gpio_state(pin_id=3, value=1))
    test.expect(test.dut.dstl_turn_on_igt_via_dev_board(igt_time=5000, time_to_sleep=5))
    test.expect(test.dut.at1.wait_for("^SYSSTART", timeout=35))


def main_process(test):
    for i in range(1, 250):
        test.log.info('loop {}'.format(i))
        test.log.step('1. AT^SMSO with new parameter: (AT^SMSO[,]). ')
        shutdown_by_smso_fast(test)
        test.log.step('2. ^SCFG: "Gpio/mode/FSR" must set to "std" ')
        test.dut.at1.send_and_verify('AT^SCFG="Gpio/mode/FSR","std"', ".*OK.*")
        test.log.step('3. Perform exec command at^smso and check module behavior.')
        shutdown_by_smso(test)
        test.log.step('4. Perform exec command at^smso,"fast" and check module behavior.')
        shutdown_by_smso_fast(test)
        test.log.step(
            '5. Change FST_SHUDWN line(GPIO4) from HIGH to LOW and keep LOW at least 10ms')
        shutdown_by_fast_shutdown_gpio(test)


if __name__ == "__main__":
    unicorn.main()
