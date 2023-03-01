#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0105096.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.security import lock_unlock_sim
from dstl.auxiliary import restart_module
from dstl.network_service import network_monitor
from dstl.network_service import network_access_type

class Test(BaseTest):
    """TC0105096.001 - snsrat_single_rat_selection
    Intention:
        1. Set snsrat to single rat before pin unlock, after pin unlock, module register on target rat.
        2. After module register one rat, rat also could be switched according to changing rat for smsrat.
    Description:
        1. Test under live network for 2/3/4G are all available
        2. Restart module with sim card which pin locked is enabled
        3. Keep pin locked, set first prefer rat to GSM        
            AT^SNSRAT=0
        4. Unlock pin, make module register on network by at+cops=0
            Verify cereg URC popup indicates that module register on GSM (2G)
        5. Wait for 10 minutes verify module is stable on 2G.
        6. Change first prefer rat to UTRAN
            AT^SNSRAT=2
        7. Check  cereg URC popup indicates that module register on UTRAN(3G)
        8. Wait for 10 minutes verify module is stable on 3G.
        9. Change first prefer rat to LTE
            AT^SNSRAT=7
        10. Check  cereg URC popup indicates that module register on LTE(4G)
        11. Wait for 10 minutes verify module is stable on 4G.
        12. Restart module repeat step 3-11, and follow the register order UTRAN->LTE->GSM
        13. Restart module repeat step 3-11, and follow the register order LTE->GSM->UTRAN
    """

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_lock_sim())

    def run(test):
        # time in minutes that monitoring module is stable in single rat
        test.monitor_in_minutes = 10
        # single mode should be switched following three kinds of orders
        test_sequences = [
            'GSM->UMTS->LTE',
            'UMTS->LTE->GSM',
            'LTE->GSM->UMTS'
        ]
        test.rat_number_map = {
            'GSM': 0,
            'UMTS': 2,
            'LTE': 7
        }
        test.log.step("1. Test under live network for 2/3/4G are all available")
        test.log.info("test.dut.sim.umts: " + test.dut.sim.umts)
        test.log.info("test.dut.sim.lte: " + test.dut.sim.lte)

        test.log.info("************************************************")
        test.log.info("Start loops for different single mode sequences.")
        for sequence in test_sequences:
            test.log.info(sequence)

        major_step_number = 1
        for rat_sequence in test_sequences:
            rats = rat_sequence.split('->')
            test.log.info(f"****** Select single prefer rat in order {rat_sequence} - START ******")
            test.log.step(f"{major_step_number}.2. Restart module with sim card which pin lock is enabled")
            test.expect(test.dut.dstl_restart())

            test.log.step(f"{major_step_number}.3. Keep pin locked, set first prefer rat to {rats[0]}")
            test.attempt(test.dut.at1.send_and_verify, "AT+CPIN?", "SIM PIN", retry=3, sleep=1)
            test.dut.at1.send_and_verify("AT+CREG=2")
            test.expect(test.dut.dstl_set_network_single_mode(rats[0], check_after_set=True))
            minor_step_number = 4
            test.set_single_rat_and_check_status(rats[0], major_step_number, minor_step_number,
                                                 set_rat=False)
            minor_step_number += 3
            test.set_single_rat_and_check_status(rats[1], major_step_number, minor_step_number,
                                                 set_rat=True)
            minor_step_number += 3
            test.set_single_rat_and_check_status(rats[2], major_step_number, minor_step_number,
                                                 set_rat=True)
            major_step_number += 1

    def monitor_network_stable(test, rat, monitor_in_minutes):
        rat_act_map = {
            'GSM': '2G',
            'UTRAN': '3G',
            'LTE': '4G'
        }
        # Total monitor time in seconds
        monitor_in_seconds = 60 * monitor_in_minutes
        # The time between execution of AT^SMONI
        interval_in_seconds = monitor_in_seconds / 20
        interval_in_minutes = interval_in_seconds / 60
        # Monitored time
        past_time_in_seconds = 0

        expect_act = rat_act_map[rat]
        test.log.info(f"Monitoring network every {interval_in_minutes} minutes, "
                      f"total {monitor_in_minutes} minutes.")
        result = True
        while past_time_in_seconds < monitor_in_seconds:
            test.sleep(interval_in_seconds)
            past_time_in_seconds += interval_in_seconds
            actual_act = test.dut.dstl_monitor_network_act()
            test.log.info(f"Time {past_time_in_seconds}s/{monitor_in_seconds}s")
            if actual_act == expect_act:
                test.log.info(f"Network type keeps as expected: {actual_act}.")
            else:
                result = False
                test.log.error(f"Expect network is {expect_act}, actual is {actual_act}.")
        test.expect(result, msg=f"Network is not stable in {expect_act}.")

    def set_single_rat_and_check_status(test, rat, major_step_number, minor_step_number,
                                        set_rat=True):
        rat_number = test.rat_number_map[rat]
        if set_rat:
            test.log.step(
                f"{major_step_number}. {minor_step_number}. Change first prefer rat to {rat}")
            test.expect(test.dut.dstl_set_network_single_mode(rat, check_after_set=True))
        else:
            test.log.step(f"{major_step_number}. {minor_step_number}. "
                          "Enter pin, make module register on network by at+cops=0")
            test.expect(test.dut.dstl_enter_pin())
            test.dut.at1.send_and_verify("AT+CEREG=2")
            test.dut.at1.send_and_verify("AT+CGREG=2")
            test.dut.at1.wait_for("C\w?REG: 1")

        minor_step_number += 1
        test.log.step(f"{major_step_number}. {minor_step_number}. "
                      f"Check cereg URC popup indicates that module register on {rat}")
        error_msg = f"\nCannot registered to {rat}. Skip step {major_step_number}. " \
            f"{minor_step_number + 1}.Wait for 10 minutes verify module is stable on {rat}."
        registered_to_rat = test.expect(test.dut.at1.send_and_verify("AT+COPS?", f",{rat_number}\s+OK"),
                                        msg=error_msg)
        if not registered_to_rat:
            test.dut.dstl_monitor_network_act()
            test.dut.at1.send_and_verify("AT^SNSRAT?", "OK")
            return

        minor_step_number += 1
        test.log.step(
            f"{major_step_number}. {minor_step_number}. Wait for 10 minutes verify module "
            f"is stable on {rat}.")
        test.monitor_network_stable(rat=rat, monitor_in_minutes=test.monitor_in_minutes)
        test.expect(test.dut.at1.send_and_verify("AT^SNSRAT?", f"\^SNSRAT: {rat_number}"))

    def cleanup(test):
        test.expect(test.dut.dstl_set_network_max_modes())
    

if "__main__" == __name__:
    unicorn.main()