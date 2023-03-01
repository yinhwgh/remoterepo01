#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0092616.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.status_control import extended_indicator_control
from dstl.network_service import customization_network_types
from dstl.call import setup_voice_call

import re


class Test(BaseTest):
    """TC0092616.001 - TpAtSindCeer
    Intention:
        Check ^SIND: CEER-URC for different call scenarios for 2G and 3G
    """

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.r1.dstl_register_to_network()

    def run(test):
        # for producing URC ceer,5 in case C.
        # invalid APN for one SIM provider may be valid for another one.
        invalid_pdps = ['IP,""', 'IP,"ims"', 'IP,"invalidapn"']

        dut_networks = test.dut.dstl_customized_network_types()
        test_rats = []
        for rat, is_supported in dut_networks.items():
            if is_supported and rat in ['GSM', 'UMTS']:
                test_rats.append(rat)

        test.log.info(f"********** Test for networks: {test_rats}. **********")
        step = 0
        for rat in test_rats:
            step += 1
            test.log.info(f"********** Tests for {rat} - START **********")

            register_to_rat = eval(f"test.dut.dstl_register_to_{rat.lower()}")

            test.log.step(f"{step}.1  {rat} - Registering to network.")
            if not test.expect(register_to_rat()):
                test.log.error(
                    f"Register to network {rat} failed, cannot continue tests for {rat}.")
                continue

            test.log.step(f"{step}.2  {rat} - Test release cause groups.")
            ceer_release_cause_groups = {
                1: "CS Internal Cause",
                2: "CS Network Cause",
                3: "CS Network Reject",
                4: "PS Internal Cause",
                5: "PS Network Cause",
                6: "Other Release Cause",
                7: "PS LTE Cause",
                8: "PS LTE Local Cause",
                9: "PS LTE SIP Cause",
                40: "ITU Q.850 Release Cause",
                41: "SIP Release Cause",
                99: "All Release Causes"
            }

            test_groups = test.get_supported_ceer_release_cause_groups()
            for group in test_groups:
                g_index = 0
                if group in ceer_release_cause_groups:
                    g_index += 1
                    test.log.step(f"{step}.2.{g_index}  {rat} - Test release cause {group} - "
                                  f"{ceer_release_cause_groups[group]}.")
                else:
                    test.log.step(f"{step}.2.{g_index}  {rat} - Test release cause {group}")

                test.expect(test.dut.dstl_enable_one_indicator("ceer", indicator_value=group, write_indicator_value=True), critical=True,
                            msg="Fail to enable ceer indicator, tests are blocked.")

                test.log.info(f"****** case A: check URC of releasing call during ring for ceer: {group}, rat: {rat}. ******")
                test.dut.at1.send_and_verify(f"ATD{test.r1.sim.nat_voice_nr};")
                test.r1.at1.wait_for("RING")
                test.sleep(2)
                test.dut.dstl_release_call()
                test.check_ceer_urc(loop_ceer=group, expect_ceer=1)
                test.r1.dstl_release_call()
                test.sleep(2)

                test.log.info(f"****** case B: check URC remote party answer and release the call for ceer: {group}, rat: {rat}. ******")
                test.expect(test.dut.dstl_voice_call_by_number(test.r1, test.r1.sim.nat_voice_nr))
                test.sleep(2)
                test.r1.dstl_release_call()
                test.dut.at1.wait_for("NO CARRIER", timeout=10)
                test.check_ceer_urc(loop_ceer=group, expect_ceer=2)
                test.sleep(2)

                test.log.info(f"****** case C: check URC packet related CEER reasons GPRS/LTE for ceer: {group}, rat: {rat}. ******")
                for invalid_pdp in invalid_pdps:
                    test.dut.at1.send_and_verify(f'AT+CGDCONT=10,{invalid_pdp}')
                    if test.dut.at1.send_and_verify('AT+CGACT=1,10', 'ERROR'):
                        test.check_ceer_urc(loop_ceer=group, expect_ceer=5)
                        break
                else:
                    test.log.error("Cannot produce invalid PDP context, skip tests for case C.")
                    test.dut.at1.send_and_verify("AT+CGACT=0,10")
                test.dut.at1.send_and_verify('AT+CGDCONT=10')
                test.sleep(2)

                test.log.info(f"****** case D: check URC remote party is way from the call for ceer: {group}, rat: {rat}. ******")
                test.dut.at1.send_and_verify(f"ATD{test.r1.sim.nat_voice_nr};")
                test.r1.at1.wait_for("RING")
                test.dut.at1.wait_for("NO CARRIER", timeout=60)
                test.check_ceer_urc(loop_ceer=group, expect_ceer=6)
                test.sleep(2)

                test.log.info(f"****** case E: check URC call non-existing number for ceer: {group}, rat: {rat}. ******")
                if not test.dut.at1.send_and_verify("ATD7654321;"):
                    test.sleep(10)
                    test.dut.at1.send_and_verify("ATD7654321;")
                test.dut.at1.wait_for("NO CARRIER", timeout=60)
                test.check_ceer_urc(loop_ceer=group, expect_ceer=40)
                test.sleep(2)

                test.expect(test.dut.dstl_disable_one_indicator("ceer"))

    def cleanup(test):
        test.dut.dstl_release_call()
        test.r1.dstl_release_call()
        test.expect(test.dut.dstl_disable_one_indicator("ceer"))

    def get_supported_ceer_release_cause_groups(test):
        test.log.info("******** Reading supported ceer release cause group values by AT^SIND=? "
                      "********")
        release_cause_groups = []
        test.dut.at1.send_and_verify("AT^SIND=?", "OK")
        values = re.findall("ceer,\((.+?)\)", test.dut.at1.last_response)
        if values:
            groups_text = values[0]
            groups = groups_text.split(',')
            for group in groups:
                numbers = re.findall('(\d+)\-(\d+)', group)
                # format: 0-9
                if numbers:
                    start_number = int(numbers[0][0])
                    end_number = int(numbers[0][1])
                    release_cause_groups += range(start_number, end_number+1)
                # format: 40,41
                else:
                    release_cause_groups.append(int(group.strip()))
        return release_cause_groups

    def check_ceer_urc(test, loop_ceer, expect_ceer):
        if loop_ceer == expect_ceer or loop_ceer == 99:
            test.expect(test.dut.at1.wait_for(f'\+CIEV: ceer,{expect_ceer}', append=True, timeout=10))
        else:
            test.log.info(f"Ceer {expect_ceer} should not display if sind URC is enable for {loop_ceer}.")
            test.expect(not test.dut.at1.wait_for(f'\+CIEV: ceer', timeout=10))
        test.dut.at1.send_and_verify("AT+CEER", "OK")
        test.dut.at1.send_and_verify("AT^SIND?", f"\^SIND: ceer,1,{loop_ceer}")

if "__main__" == __name__:
    unicorn.main()