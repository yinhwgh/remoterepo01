# author: christian.gosslar@thalesgroup.com
# responsible: christian.gosslar@thalesgroup.com
# location: Berlin
# LM7864
# TC0106042.001
# Multiparty Test with chld=0
'''
Test 3 - chld 0
- DUT call R1
- R1 accept call
- DUT call R2
- R2 accept call
- R2 release call to DUT
- DUT release all held calls chld=0
- terminate all calls via chup

- DUT call R1
- R1 accept call
- DUT call R2
- R2 accept call
- DUT toggle via chld=2 the calls
- now call to R1 is active, R2 on hold
- R1 release the call
- call to R2 is on hold
- DUT release all held calls chld=0
- terminate all calls via chup

- DUT call R1
- R1 accept call
- DUT call R2
- R2 accept call
- DUT toggle via chld=2 the calls
- DUT release the hold call via chld=0
- only one call is active
- DUT release the call
'''


import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.collect_module_infos import dstl_collect_module_info
from dstl.identification.get_revision_number import dstl_get_revision_number
from dstl.identification.get_imei import dstl_get_imei
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.check_c_revision_number import dstl_check_c_revision_number
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.call.setup_voice_call import dstl_voice_call_by_number
from dstl.call.multiparty_infos import *
from dstl.auxiliary.devboard.devboard import *

import re

# define the Network setting als global variables, because it shall be used in test and cleanup function
changed_rat = False
# Value for RAT Value during the Tests. Must be adapted for 2G/3G/4G Tests
# # allowed values are: "4G" "3G" "2G"
# Parameter comes from cmd-line "multiparty_chld0.py --requested_network_rat=2G"
# But it can overrule be local parameter here, allowed values are 2G 3G 4G
requested_network_rat = ""

max_rat = 7
module_has_slcc = False
tln_dut_hang_up_call = "at+chup"
tln_r1_hang_up_call = "at+chup"
tln_r2_hang_up_call = "at+chup"
call_array_r1 = ["", "", "", "", "", "", "", "", "", ""]
call_array_r2 = ["", "", "", "", "", "", "", "", "", ""]
multi_call_array_r1 = ["", "", "", "", "", "", "", "", "", ""]
multi_call_array_r2 = ["", "", "", "", "", "", "", "", "", ""]
# flag if call waiting is not active
# shall only used as workaround
call_waiting = True
ver = "1.2"

class multiparty_chld0(BaseTest):

    def clean_arrays (test):
        global call_array_r1
        global call_array_r2
        global multi_call_array_r1
        global multi_call_array_r2
        call_array_r1 = ["", "", "", "", "", "", "", "", "", ""]
        call_array_r2 = ["", "", "", "", "", "", "", "", "", ""]
        multi_call_array_r1= ["","","","","","","","","",""]
        multi_call_array_r2= ["","","","","","","","","",""]
        return

    def setup(test):
        test.log.com ('***** Testcase: ' + test.test_file + ' Ver: ' + str(ver) + ' - Start *****')
        test.log.com ('***** Collect some Module Infos *****')
        # add these here only for fast abort if some parameter are missing
        global requested_network_rat
        # read cmd-line parameter, but if local parameter is used, it's overrule
        if requested_network_rat == "":
            requested_network_rat = test.requested_network_rat
        if requested_network_rat == "":
            test.expect(False)
        test.log.com('***** Run with Parameter requested_network_rat: ' + test.requested_network_rat + " *****")
        test.dut.dstl_detect()
        test.dut.dstl_switch_off_at_echo(serial_ifc=0)
        test.dut.dstl_get_bootloader()
        test.dut.dstl_check_c_revision_number()
        test.dut.dstl_collect_module_info()
        test.dut.dstl_collect_module_info_for_mail()
        test.r1.dstl_detect()
        test.r2.dstl_detect()
        test.log.com ('***** register all Module into Network if needed *****')
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.r1.dstl_register_to_network())
        test.expect(test.r2.dstl_register_to_network())
        test.log.info("log the network state for all modules")
        test.dut.at1.send_and_verify("at+COPS?")
        test.dut.at1.send_and_verify("at^SMONI")
        test.dut.at1.send_and_verify("at+cimi")
        test.dut.at1.send_and_verify("at^scfg=\"URC/Dstifc\"")
        test.r1.dstl_get_imei()
        test.r1.at1.send_and_verify("at+COPS?")
        test.r1.at1.send_and_verify("at^SMONI")
        test.r1.at1.send_and_verify("at+cimi")
        test.r1.at1.send_and_verify("at^sqport")
        test.r1.at1.send_and_verify("at^scfg=\"URC/Dstifc\",app")
        test.r2.dstl_get_imei()
        test.r2.at1.send_and_verify("at+COPS?")
        test.r2.at1.send_and_verify("at^SMONI")
        test.r2.at1.send_and_verify("at+cimi")
        test.r2.at1.send_and_verify("at^sqport")
        test.r2.at1.send_and_verify("at^scfg=\"URC/Dstifc\",app")

    def run(test):
        """
        Intention:
        base Testcase for multipary
        """
        # arrays for the response of clcc and slcc
        # Every call has a own array
        # If multiparty is active there are two other arrays
        # currently no a array of a array is used (shall be used, if multiparty with more then two parties shall be tested
        # saved values are:
        #[0:CallID_Rx, 1:CallIDSlcc_Rx, 2:CallState_Rx, 3:CallStateSlcc_Rx, 4:CLCC_equal_SLCC, 5:Number, 6:mpty-state CLCC, 7:mpty-state SLCC]
        # call_array_r1
        # call_array_r2
        # multi_call_array_r1
        # multi_call_array_r2

        # definition of some fix values
        # ==============================
        tln_dut_nat = test.dut.sim.nat_voice_nr
        tln_dut_int = test.dut.sim.nat_voice_nr
        tln_r1_nat = test.r1.sim.nat_voice_nr
        tln_r1_int = test.r1.sim.int_voice_nr
        tln_r2_nat = test.r2.sim.nat_voice_nr
        tln_r2_int = test.r2.sim.int_voice_nr

        # NetworkID = test.dut.sim.imsi[:5]
        global tln_dut_hang_up_call
        global tln_r1_hang_up_call
        global tln_r2_hang_up_call

        # set the requested network for DUT, allowed values are 2G (GSM), 3G (UTRAN), 4G /E-UTRAN) and don't care
        # Network is set via cops=0,,,x (0,2,7,0)
        # use global variables
        global requested_network_rat
        global changed_rat
        global max_rat
        global call_array_r1
        global call_array_r2
        global multi_call_array_r1
        global multi_call_array_r2
        if "262014244054638" in test.dut.sim.imsi:
            call_waiting = False # these SIM has no call waiting

        wait_time = 3
        global module_has_slcc

        if (re.search(test.dut.project, 'BOBCAT|VIPER')):
            module_has_slcc = True
            max_rat = 7

        test.log.step ('Step 0.2: check call state before test')
        #==============================================================
        test.dut.dstl_check_call_state_all(test.r1, test.r2, module_has_slcc, tln_dut_hang_up_call, tln_r1_hang_up_call,
                                           tln_r2_hang_up_call)

        test.log.step ('Step 0.1: check Network RAT and change if needed')
        #==============================================================
        changed_rat = test.dut.dstl_set_requested_rat_value(requested_network_rat)
        test.log.info("active CLIR")
        test.expect(test.dut.at1.send_and_verify("at+CLIR=2"))

        #==============================================================
        #==============================================================
        test.log.step('Step 1.0: Multiparty Test 3 # '
                      '- DUT call R1 - R1 accept call\n'
                      '- DUT call R2 - R2 accept call\n'
                      '- R2 release call to DUT\n'
                      '- R2 release call to DUT\n'
                      '- DUT release all held calls chld=0')

        test.log.step ('Step 1.1: DUT call R1 and R1 accept the call')
        #==============================================================
        test.expect(test.dut.dstl_voice_call_by_number(test.r1, tln_r1_nat))

        test.sleep(wait_time)
        call_array_r1 = test.dut.dstl_clcc_slcc_check(tln_r1_nat, module_has_slcc)

        test.log.step ('Step 1.2: DUT call R2 and R2 accept the call')
        #==============================================================
        test.expect(test.dut.dstl_voice_call_by_number(test.r2, tln_r2_nat))

        test.sleep(wait_time)
        call_array_r2 = test.dut.dstl_clcc_slcc_check(tln_r2_nat, module_has_slcc)

        test.log.info("check the number of calls in clcc/slcc")
        test.expect(test.dut.dstl_check_number_of_calls(2, module_has_slcc))

        test.log.step ('Step 1.3: Check the call state from R1 (hold) and R2 (active)')
        #==============================================================
        multi_call_array_r1 = test.dut.dstl_clcc_slcc_check(tln_r1_nat, module_has_slcc)

        test.expect(test.dut.dstl_requested_call_state("held", multi_call_array_r1, module_has_slcc))
        test.expect(test.dut.dstl_requested_call_state("active", call_array_r2, module_has_slcc))

        test.log.info("check the current Network")
        test.expect(test.dut.dstl_check_current_network(requested_network_rat))

        test.log.step ('Step 1.4: R2 release call to DUT')
        #==============================================================

        test.expect(test.r2.at1.send_and_verify(tln_r2_hang_up_call, "OK"))
        test.sleep(wait_time)

        multi_call_array_r1 = test.dut.dstl_clcc_slcc_check(tln_r1_nat, module_has_slcc)
        test.expect(test.dut.dstl_compare_call_ids(call_array_r1, multi_call_array_r1, module_has_slcc))
        test.log.info("check the number of calls in clcc/slcc")
        test.expect(test.dut.dstl_check_number_of_calls(1, module_has_slcc))

        test.log.info("check the call a´state from call to R1 again (still hold)")
        test.expect(test.dut.dstl_requested_call_state("held",multi_call_array_r1,module_has_slcc))

        test.log.step ('Step 1.5: DUT release all held calls chld=0')
        #==============================================================
        test.expect(test.dut.at1.send_and_verify("at+chld=0", "OK"))
        test.sleep(wait_time)
        test.expect(test.dut.dstl_check_number_of_calls(0, module_has_slcc))
        test.sleep(wait_time)
        test.dut.dstl_check_call_state_all(test.r1, test.r2, module_has_slcc, tln_dut_hang_up_call, tln_r1_hang_up_call,
                                           tln_r2_hang_up_call)
        test.clean_arrays()
        test.sleep(wait_time)
        #==============================================================
        #==============================================================
        test.log.step('Step 2.0: Multiparty Test 3 # \n'
                      '- DUT call R1 and R1 accept call\n'
                      '- DUT call R2 and R2 accept call \n'
                      '- DUT toggle via chld=2 the calls\n'
                      '- now call to R1 is active, R2 on hold\n'
                      '- R1 release the call, call to R2 is on hold\n'
                      '- DUT release all held calls chld=0')

        test.log.step ('Step 2.1: DUT call R1 and R1 accept the call')
        #==============================================================
        test.expect(test.dut.dstl_voice_call_by_number(test.r1, tln_r1_nat))

        test.sleep(wait_time)
        call_array_r1 = test.dut.dstl_clcc_slcc_check(tln_r1_nat, module_has_slcc)

        test.log.step ('Step 2.2: DUT call R2 and R2 accept the call')
        #==============================================================
        test.expect(test.dut.dstl_voice_call_by_number(test.r2, tln_r2_nat))

        test.sleep(wait_time)
        call_array_r2 = test.dut.dstl_clcc_slcc_check(tln_r2_nat, module_has_slcc)

        test.log.info("check the number of calls in clcc/slcc")
        test.expect(test.dut.dstl_check_number_of_calls(2, module_has_slcc))

        test.log.step ('Step 2.3: Check the call state from R1 (hold) and R2 (active)')
        #==============================================================
        test.log.info("check the call state from call to R1 again (still hold)")
        multi_call_array_r1 = test.dut.dstl_clcc_slcc_check(tln_r1_nat, module_has_slcc)
        test.expect(test.dut.dstl_requested_call_state("held",multi_call_array_r1,module_has_slcc))

        test.log.info("check the call state from call to R2 (active)")
        test.expect(test.dut.dstl_requested_call_state("active",call_array_r2,module_has_slcc))

        test.log.step ('Step 2.4: DUT toggle via chld=2 the calls')
        # ==============================================================
        test.expect(test.dut.at1.send_and_verify("at+chld=2", "OK"))
        test.sleep(wait_time)

        test.log.step ('Step 2.5: now call to R1 is active, R2 on hold')
        # ==============================================================
        multi_call_array_r1 = test.dut.dstl_clcc_slcc_check(tln_r1_nat, module_has_slcc)
        multi_call_array_r2 = test.dut.dstl_clcc_slcc_check(tln_r2_nat, module_has_slcc)
        test.log.info("check the call state from call to R1 (active)")
        test.expect(test.dut.dstl_requested_call_state("active",multi_call_array_r1,module_has_slcc))
        test.log.info("check the call state from call to R2 (hold)")
        test.expect(test.dut.dstl_requested_call_state("held",multi_call_array_r2,module_has_slcc))

        test.expect(test.dut.dstl_compare_call_ids (call_array_r1, multi_call_array_r1, module_has_slcc))
        test.expect(test.dut.dstl_compare_call_ids (call_array_r2, multi_call_array_r2, module_has_slcc))

        test.log.info("check the current Network")
        test.expect(test.dut.dstl_check_current_network(requested_network_rat))

        test.log.step ('Step 2.6: R1 release the call - call to R2 is on hold')
        # ==============================================================
        test.expect(test.r1.at1.send_and_verify(tln_r1_hang_up_call, "OK"))
        test.sleep(wait_time)
        multi_call_array_r2 = test.dut.dstl_clcc_slcc_check(tln_r2_nat, module_has_slcc)
        test.log.info("check the call state from call to R2 (hold)")
        test.expect(test.dut.dstl_requested_call_state("held",multi_call_array_r2,module_has_slcc))

        test.log.step ('Step 2.7: DUT release all held calls chld=0')
        #==============================================================
        test.expect(test.dut.at1.send_and_verify("at+chld=0", "OK"))
        test.sleep(wait_time)
        test.log.info("check the number of calls in clcc/slcc")
        test.expect(test.dut.dstl_check_number_of_calls(0, module_has_slcc))
        test.sleep(wait_time)
        test.dut.dstl_check_call_state_all(test.r1, test.r2, module_has_slcc, tln_dut_hang_up_call, tln_r1_hang_up_call,
                                           tln_r2_hang_up_call)
        test.clean_arrays()
        test.sleep(wait_time)

        # ==============================================================
        # ==============================================================
        test.log.step('Step 3.0: Multiparty Test 3 # \n'
                      '- DUT call R1 and R1 accept call \n'
                      '- DUT call R2 and R2 accept call \n'
                      '- DUT toggle via chld=2 the calls\n'
                      '- DUT release the hold call via chld=0 - only one call is active\n'
                      '- DUT release the call')

        test.log.step ('Step 3.1: DUT call R1 and R1 accept the call')
        # ==============================================================
        test.expect(test.dut.dstl_voice_call_by_number(test.r1, tln_r1_nat))

        test.sleep(wait_time)
        call_array_r1 = test.dut.dstl_clcc_slcc_check(tln_r1_nat, module_has_slcc)

        test.log.step ('Step 3.2: DUT call R2 and R2 accept the call')
        # ==============================================================
        test.expect(test.dut.dstl_voice_call_by_number(test.r2, tln_r2_nat))

        test.sleep(wait_time)
        call_array_r2 = test.dut.dstl_clcc_slcc_check(tln_r2_nat, module_has_slcc)

        test.log.info("check the number of calls in clcc/slcc")
        test.expect(test.dut.dstl_check_number_of_calls(2, module_has_slcc))

        test.log.step ('Step 3.3: DUT toggle via chld=2 the calls')
        # ==============================================================
        test.expect(test.dut.at1.send_and_verify("at+chld=2", "OK"))
        test.sleep(wait_time)
        multi_call_array_r1 = test.dut.dstl_clcc_slcc_check(tln_r1_nat, module_has_slcc)
        multi_call_array_r2 = test.dut.dstl_clcc_slcc_check(tln_r2_nat, module_has_slcc)
        test.log.info("check the number of calls in clcc/slcc")
        test.expect(test.dut.dstl_check_number_of_calls(2, module_has_slcc))
        test.log.info("check the call state from call to R2 (hold)")
        test.expect(test.dut.dstl_requested_call_state("held",multi_call_array_r2,module_has_slcc))
        test.log.info("check the call state from call to R1 (active)")
        test.expect(test.dut.dstl_requested_call_state("active",multi_call_array_r1,module_has_slcc))

        test.log.info("check the current Network")
        test.expect(test.dut.dstl_check_current_network(requested_network_rat))

        test.log.step ('Step 3.4: DUT release the hold call via chld=0 - only one call is active')
        # ==============================================================
        test.expect(test.dut.at1.send_and_verify("at+chld=0", "OK"))
        test.sleep(wait_time)
        test.expect(test.dut.dstl_check_number_of_calls(1, module_has_slcc))
        multi_call_array_r1 = test.dut.dstl_clcc_slcc_check(tln_r1_nat, module_has_slcc)
        test.log.info("check the call state from call to R1 (active)")
        test.expect(test.dut.dstl_requested_call_state("active",multi_call_array_r1,module_has_slcc))

        test.log.step ('Step 3.5: DUT release the call')
        # ==============================================================
        test.expect(test.dut.at1.send_and_verify(tln_dut_hang_up_call, "OK"))
        test.sleep(wait_time)

    def cleanup(test):
        """Cleanup method.
        Steps to be executed after test run steps.
        """
        global module_has_slcc
        global tln_dut_hang_up_call
        global tln_r1_hang_up_call
        global tln_r2_hang_up_call

        test.log.com(' ')
        test.log.com('****  log dir: ' + test.workspace + ' ****')
        test.dut.dstl_check_call_state_all(test.r1, test.r2, module_has_slcc,tln_dut_hang_up_call, tln_r1_hang_up_call, tln_r2_hang_up_call)

        test.log.info("If RAT was changed, set back to max_rat value, not to the value at the Test start")
        global changed_rat
        global max_rat
        if changed_rat:
            test.expect(test.dut.at1.send_and_verify("at+cops=0,,," + str(max_rat), "OK"))
            test.sleep(30)

        test.log.com(' ')
        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')

if "__main__" == __name__:
    unicorn.main()
