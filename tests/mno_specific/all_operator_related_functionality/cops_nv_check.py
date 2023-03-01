#responsible: yuan.gao@thalesgroup.com
#location: Dalian
#TC0104153.001

import unicorn

from core.basetest import BaseTest
from dstl.security import lock_unlock_sim
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.network_service import register_to_network
from dstl.configuration import shutdown_smso
from dstl.auxiliary.devboard import devboard
from dstl.network_service import customization_cops_properties
from dstl.network_service import operator_selector
from dstl.network_service import customization_operator_id


class TpCopsNvCheck(BaseTest):
    """
        TC0104153.001 - CopsNVCheck
        Check whether the Parameter value of at+cops is stored in non-volatile memory if the command support for (NV)
        Subscribers: dut
        Debugged products: Boxwood Step7
        Duration: 30 mins
        Author: yuan.gao@thalesgroup.com
    """

    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        # Init expected response when reading or writing before pin is entered
            
        test.log.info("Test in every port module supports")
        for port in [test.dut.at1, test.dut.at2]:
            test.log.info("********* Set the module with pin locked: SIM PIN *********")
            res_pin_lock_unlock = "CPIN: SIM PIN"

            # COPS commands can be full or partly pin protected
            read_res_before_pin = "CME ERROR: SIM PIN required"
            write_res_before_pin = "CME ERROR: SIM PIN required"
            cops_pin_protected_properties = test.dut.dstl_customized_cops_pin_protected()
            if cops_pin_protected_properties["AT+COPS?"] == True:
                read_res_before_pin = "CME ERROR: SIM PIN required"
            if cops_pin_protected_properties["AT+COPS?"] == False:
                write_res_before_pin = "OK"
            
            test.dut.dstl_lock_sim()
            test.dut.dstl_restart()

            check_cops_nv(test, res_pin_lock_unlock, read_res_before_pin, write_res_before_pin, port)

            test.log.info("********* Set the module with pin unlocked: READY *********")
            test.dut.dstl_enter_pin()
            test.dut.dstl_unlock_sim()
            res_pin_lock_unlock = "CPIN: READY"
            res_err_ok = "OK"
            res_cops = "COPS: 0"
            check_cops_nv(test, res_pin_lock_unlock, res_err_ok, res_cops, port)


    def cleanup(test):
        test.dut.dstl_lock_sim()
        test.dut.dstl_restart()


def check_cops_nv(test, res_pin_lock_unlock, res_err_ok, res_cops, port):
    timeout = 30
    port.send_and_verify("at+cmee=2", "OK")
    port.send_and_verify("at&w", "OK")
    test.expect(port.send_and_verify("at+cpin?", res_pin_lock_unlock))
    test.expect(port.send_and_verify("at+cops?", res_cops))
    smso_shutdown = True
    test.log.info(f"Step 1.Configuring new value parameters of at+cops command supported, then check the value with read command: pin status {res_pin_lock_unlock}")
    test.expect(port.send_and_verify("at+cops=2", res_err_ok, timeout=timeout))
    res_cops = "COPS: 2" if "READY" in res_pin_lock_unlock else res_cops
    test.attempt(port.send_and_verify,"at+cops?", res_cops, retry=3, sleep=5)

    test.log.info("Step 2. Restart the module and check the parameters for the command: pin status {res_pin_lock_unlock}")
    test.expect(test.dut.dstl_restart())
    test.attempt(port.send_and_verify, "at+cpin?", expect=res_pin_lock_unlock, retry=3, sleep=2)
    res_cops = "COPS: 0" if "READY" in res_pin_lock_unlock else res_cops
    test.expect(port.send_and_verify("at+cops?", res_cops))

    test.log.info("Step 3.Configuring new value parameters of at+cops module supported: pin status {res_pin_lock_unlock}")
    operator_number = test.dut.dstl_get_operator_id()
    test.expect(port.send_and_verify(f"at+cops=2", res_err_ok, timeout=90))
    res_cops = f"COPS: 2" if "READY" in res_pin_lock_unlock else res_cops
    test.expect(port.send_and_verify("at+cops?", res_cops))

    test.log.info("Step 4.Using at command to make module shut down: pin status {res_pin_lock_unlock}")
    if smso_shutdown and test.dut.dstl_shutdown_smso():
        test.log.info("Shutdown module with command \"AT^SMSO\" successfully.")
    else:
        test.sleep(3)
        test.log.error("Shutdown failure with \"AT^SMSO\", use MCTest board to power off module.")
        test.expect(test.dut.dstl_turn_off_vbatt_via_dev_board())
        smso_shutdown = False
    test.sleep(3)

    test.log.info("Step 5.Trigger the ignition signal to start the module and check the parameters for the command: pin status {res_pin_lock_unlock}")
    test.dut.dstl_turn_on_vbatt_via_dev_board()
    test.expect(test.dut.dstl_turn_on_igt_via_dev_board(1000))
    test.expect(port.wait_for(".*(SYSSTART|SYSLOADING).*", timeout=90))
    test.sleep(3)
    test.expect(port.send_and_verify("at+cpin?", res_pin_lock_unlock))
    res_cops = "COPS: 0" if "READY" in res_pin_lock_unlock else res_cops
    test.expect(port.send_and_verify("at+cops?", res_cops))

    test.log.info("Step 6.Configuring new value parameters of at+cops command module supported, then execute at&F, and check the value: pin status {res_pin_lock_unlock}")
    test.expect(port.send_and_verify("at+cops=2", res_err_ok, timeout=timeout))
    res_cops = "COPS: 2" if "READY" in res_pin_lock_unlock else res_cops
    test.sleep(1)
    test.attempt(port.send_and_verify,"at+cops?", res_cops, sleep=5,retry=3)
    test.expect(port.send_and_verify("at&f", "OK"))
    test.expect(port.send_and_verify("at+cops?", res_cops))

    test.log.info("Step 7.Restart the module and check the parameters for the command: pin status {res_pin_lock_unlock}")
    test.expect(test.dut.dstl_restart())
    test.sleep(3)
    res_cops = "COPS: 0" if "READY" in res_pin_lock_unlock else res_cops
    test.expect(port.send_and_verify("at+cops?", res_cops))


if "__main__" == __name__:
    unicorn.main()
