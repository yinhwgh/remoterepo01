# responsible: lei.chen@thalesgroup.com
# location: Dalian
# TC0094803.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.packet_domain import config_pdp_context
from dstl.security import lock_unlock_sim
from dstl.configuration import configure_scfg_provider_profile
from dstl.configuration import scfg_radio_band
from dstl.network_service import network_monitor
from dstl.call import setup_voice_call
from dstl.call import enable_voice_call_with_ims
from dstl.call import get_voice_call_modes


class Test(BaseTest):
    """
    TC0094803.001 - TpAtCsfbBasic
    Check if the the function of the cvmod command and the CSFB works without problems.

    The Test check, if the module setting of cvmod works fine. The TP runs a loop
    - loop 1, set the Module with radio band to all Networks, GSM-LTE, GSM-UMTS only
    - loop 2. check all cvmod mode:
     0 CS only
     1 VOIP only
     2 CS prefferred
     3 VOIP prefferred
    - loop 3: make with every cvmod a MT and MO call to/from the module
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_enter_pin()
        test.r1.dstl_detect()
        test.r1.dstl_register_to_network()
        test.dut.dstl_set_all_radio_bands()
        pass

    def run(test):
        network_loops_map = {
            1: 'radio band -> all network.',
            2: 'radio band -> GSM-LTE',
            3: 'radio band -> GSM-UMTS'
        }
        network_count = len(network_loops_map)
        cvmodes = test.dut.dstl_get_voice_call_modes()
        for network_loop in range(1, network_count + 1):
            for cvmode in cvmodes:
                # Volte call is not allowed for GSM/UMTS
                if network_loop == 3 and cvmode == 1:
                    call_result = "NO CARRIER"
                else:
                    call_result = "OK"
                test.set_radio_bands(network_loop)
                test.expect(test.dut.at1.send_and_verify(f"AT+CVMOD={cvmode}"))
                test.sleep(2)
                test.log.step(f"Loop {network_loop} - {network_loops_map[network_loop]}, "
                              f"CVMODE {cvmode}, MO Call.")
                rat_before_call = test.dut.dstl_monitor_network_act()
                test.expect(test.dut.dstl_voice_call_by_number(test.r1, test.r1.sim.nat_voice_nr,
                                                               expect_result=call_result))
                test.check_status_during_call(network_loop, cvmode, is_mo=True,
                                              rat_before_call=rat_before_call)
                test.dut.dstl_release_call()
                test.sleep(5)

                test.log.step(f"Loop {network_loop} - {network_loops_map[network_loop]}, "
                              f"CVMODE {cvmode}, MT Call.")
                rat_before_call = test.dut.dstl_monitor_network_act()
                test.expect(test.r1.dstl_voice_call_by_number(test.dut, test.dut.sim.nat_voice_nr,
                                                              expect_result='OK'))
                test.check_status_during_call(network_loop, cvmode, is_mo=False,
                                              rat_before_call=rat_before_call)
                test.r1.dstl_release_call()
                test.dut.dstl_release_call()
        pass

    def cleanup(test):
        test.dut.dstl_switch_on_provider_auto_select()
        test.dut.dstl_set_all_radio_bands()
        test.dut.dstl_restart()
        pass

    def set_radio_bands(test, loop_number):
        if loop_number == 1:
            test.log.h3("Setting radio band to all network.")
            test.expect(test.dut.dstl_set_all_radio_bands())
            test.expect(test.dut.dstl_enable_voice_call_with_ims(manually_register_to_lte=False))
        elif loop_number == 2:
            test.log.h3("Setting radio band to GSM-LTE by disabling 3G.")
            test.expect(test.dut.dstl_set_radio_band(rba1='0', rat='3G'))
            test.expect(test.dut.dstl_enable_voice_call_with_ims(manually_register_to_lte=False))
        elif loop_number == 3:
            test.log.h3("Setting radio band to GSM-UMTS by disabling 4G.")
            test.expect(test.dut.dstl_set_all_radio_bands())
            test.expect(test.dut.dstl_set_radio_band(rba1='0', rba2='0', rat='4G'))
            test.dut.dstl_register_to_network()
            test.dut.at1.send_and_verify("AT+CAVIMS?", "CAVIMS: 0")
        else:
            test.log.error(f"Invalid loop number {loop_number}.")
        test.sleep(2)
        pass

    def check_status_during_call(test, loop_number, cvmode, is_mo, rat_before_call):
        """
        For MT calls, network should the one before making call.
        For MO calls:
            loop_number 1 (rat: all): cvmode 0: 2G/3G
                                      cvmode 1: 4G
                                      cvmode 3: 4G
            loop_number 2 (rat: 2G&4G): cvmode 0: 2G
                                        cvmode 1: 4G
                                        cvmode 3: 4G
            loop_number 3 (rat: 2G&3G): cvmode 0: 2G/3G
                                        cvmode 1: 2G/3G (Actually no call is in progress)
                                        cvmode 3: 2G/3G
        """
        if is_mo and cvmode == 0:
            if loop_number == 2:
                expect_act = '2G'
            else:
                expect_act = ('2G', '3G')
        else:
            expect_act = rat_before_call
        if '4G' in expect_act:
            expect_cavims = 1
        else:
            expect_cavims = 0
        network_act = test.dut.dstl_monitor_network_act()
        test.expect(network_act in expect_act, msg=f"Expect network is {expect_act} while actual is {network_act}.")
        test.expect(test.dut.at1.send_and_verify("AT+CAVIMS?", f"CAVIMS: {expect_cavims}"))
        pass


if __name__ == "__main__":
    unicorn.main()
