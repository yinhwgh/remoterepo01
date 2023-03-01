# author: christian.gosslar@thalesgroup.com
# responsible: christian.gosslar@thalesgroup.com
# location: Berlin
# LM7864
# TC0107188.001
# Multiparty Test with chld2
'''Test 1 - chld 3
- DUT call R1
- R1 accept call
- DUT call R2
- R2 accept call
- DUT start conference call
- terminate all calls via chup

Test 2a - chld 3
- DUT call R1
- R1 accept call
- R2 call DUT
- DUT accept call
- DUT start conference call
- terminate all calls via chup

Test 2b - chld 3
- R1 call DUT
- DUT accept call
- R2 call DUT
- DUT accept call
- DUT start conference call
- terminate all calls via chup

Test 2b - chld 3
- R1 call DUT
- DUT accept call
- DUT call R2
- R2 accept call
- DUT start conference call
- terminate all calls via chup


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
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.call.setup_voice_call import dstl_voice_call_by_number
from dstl.call.multiparty_infos import dstl
from dstl.auxiliary.devboard import devboard

import re

# define the Network setting als global variables, because it shall be used in test and cleanup function
changed_rat = False
# Value for RAT Value during the Tests. Must be adapted for 2G/3G/4G Tests
# # allowed values are: "4G" "3G" "2G"
requested_network_rat = "3G"
# global Parameter for the max RAT Value of the module, is used also in the cleanup routine
# it will be set in the test case automatic (project dependent). Here is only the default value define
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
ver = "1.0"

class multiparty_chld3_3g(BaseTest):

    def setup(test):
        test.log.com ('***** Testcase: ' + test.test_file + ' Ver: ' + str(ver) + ' - Start *****')
        test.log.com ('***** Collect some Module Infos *****')
        test.dut.dstl_detect()
        test.dut.dstl_switch_off_at_echo(serial_ifc=0)
        # test.dut.devboard.send_and_verify("mc:asc0cfg=off", ".*O.*")
        test.dut.dstl_get_imei()
        test.dut.dstl_get_bootloader()
        test.dut.dstl_check_c_revision_number()
        test.dut.dstl_collect_module_info()
        test.dut.dstl_collect_module_info_for_mail()
        test.r1.dstl_detect()
        test.r1.dstl_get_imei()
        test.r2.dstl_detect()
        test.r2.dstl_get_imei()
        test.log.com ('***** register all Module into Network if needed *****')
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.r1.dstl_register_to_network())
        test.expect(test.r2.dstl_register_to_network())
        test.log.info("log the network state for all modules")
        test.dut.at1.send_and_verify("at+COPS?")
        test.dut.at1.send_and_verify("at^SMONI")
        test.dut.at1.send_and_verify("at+cimi")
        test.r1.at1.send_and_verify("at+COPS?")
        test.r1.at1.send_and_verify("at^SMONI")
        test.r1.at1.send_and_verify("at+cimi")
        test.r2.at1.send_and_verify("at+COPS?")
        test.r2.at1.send_and_verify("at^SMONI")
        test.r2.at1.send_and_verify("at+cimi")

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
        global call_waiting
        if "262014244054638" in test.dut.sim.imsi:
            call_waiting = False

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

        wait_time = 3
        global module_has_slcc

        if (re.search(test.dut.project, 'BOBCAT|VIPER')):
            module_has_slcc = True
            max_rat = 7

        test.log.step ('Step 0.1: check call state before test')
        #==============================================================
        test.dut.dstl_check_call_state_all(test.r1, test.r2, module_has_slcc, tln_dut_hang_up_call, tln_r1_hang_up_call,
                                           tln_r2_hang_up_call)

        test.log.step ('Step 0.2: check Network RAT and change if needed')
        # ==============================================================
        changed_rat = test.dut.dstl_set_requested_rat_value(requested_network_rat)
        test.log.info("active CLIR")
        test.expect(test.dut.at1.send_and_verify("at+CLIR=2"))
        test.expect(test.r1.at1.send_and_verify("at+CLIR=2"))
        test.expect(test.r2.at1.send_and_verify("at+CLIR=2"))

        # ==============================================================
        test.log.step('Step 1.0: Multiparty Test 1 # \n'
                      '- DUT call R1 and R1 accept call\n'
                      '- DUT call R2 and R2 accept call\n'
                      '- DUT start conference call \n'
                      '- terminate all calls via chup')

        test.log.step ('Step 1.1: DUT call R1 and R1 accept the call')
        # ==============================================================
        test.expect(test.dut.dstl_voice_call_by_number(test.r1, tln_r1_nat))

        test.sleep(wait_time)
        call_array_r1 = test.dut.dstl_clcc_slcc_check(tln_r1_nat, module_has_slcc)

        test.log.step ('Step 1.2: DUT call R2 and R2 accept the call')
        # ==============================================================
        test.expect(test.dut.dstl_voice_call_by_number(test.r2, tln_r2_nat))

        test.sleep(wait_time)
        call_array_r2 = test.dut.dstl_clcc_slcc_check(tln_r2_nat, module_has_slcc)

        test.log.step ('Step 1.3: start multiparty with chld=3')
        # ==============================================================
        test.expect(test.dut.at1.send_and_verify("at+chld=3", "OK"))
        test.sleep(wait_time)
        test.expect(test.dut.at1.send_and_verify("at+clcc"))

        test.log.step ('Step 1.4: Compare the call IDs before and after the start of Mulitparty')
        # ==============================================================
        multi_call_array_r1 = test.dut.dstl_clcc_slcc_check (tln_r1_nat, module_has_slcc)
        multi_call_array_r2 = test.dut.dstl_clcc_slcc_check (tln_r2_nat, module_has_slcc)

        test.log.info("check if the call IDs are correct")
        test.expect(test.dut.dstl_compare_call_ids (call_array_r1, multi_call_array_r1, module_has_slcc))
        test.expect(test.dut.dstl_compare_call_ids (call_array_r2, multi_call_array_r2, module_has_slcc))

        test.log.info("check if the calls are in Multiparty State")
        test.expect(test.dut.dstl_check_call(multi_call_array_r1, "0", tln_r1_nat, module_has_slcc, True))
        test.expect(test.dut.dstl_check_call(multi_call_array_r2, "0", tln_r2_nat, module_has_slcc, True))

        test.log.info("check the number of calls in clcc/slcc")
        test.expect(test.dut.dstl_check_number_of_calls(2, module_has_slcc))

        test.log.info("check the current Network")
        test.expect(test.dut.dstl_check_current_network(requested_network_rat))

        test.log.step ('Step 1.5: terminate the calls via chup')
        # ==============================================================
        test.expect(test.dut.at1.send_and_verify(tln_dut_hang_up_call, "OK"))
        #test.sleep(wait_time)
        test.sleep(wait_time)
        test.dut.dstl_check_call_state_all(test.r1, test.r2, module_has_slcc, tln_dut_hang_up_call, tln_r1_hang_up_call,
                                           tln_r2_hang_up_call)
        test.clean_arrays()
        test.sleep(wait_time)


        if not call_waiting:
            # ==============================================================
            test.log.step('Step 2.0: skipped, because multiparty is not working for these SIM\n'
                          'Multiparty Test 2 #\n'
                          '- DUT call A and A accept call\n'
                          '- B call DUT and DUT accept call\n'
                          '- DUT start conference call\n'
                         '- terminate all calls via chup')
        else:
            # ==============================================================
            test.log.step('Step 2.0: Multiparty Test 2 #\n'
                          '- DUT call A and A accept call\n'
                          '- B call DUT and DUT accept call\n'
                          '- DUT start conference call\n'
                          '- terminate all calls via chup')

            test.log.step ('Step 2.1: DUT call R1 and R1 accept the call')
            # ==============================================================
            test.log.info("active call waiting")
            test.expect(test.dut.at1.send_and_verify("atd*43#;", "CCWA: 1,"))
            test.expect(test.dut.at1.send_and_verify("at+CCWA=1;", "OK"))

            test.expect(test.dut.dstl_voice_call_by_number(test.r1, tln_r1_nat))

            test.sleep(wait_time)
            call_array_r1 = test.dut.dstl_clcc_slcc_check(tln_r1_nat, module_has_slcc)
            test.log.info("Call ID form Call DUT to Remote 1 " + tln_r1_nat + " is " + call_array_r1[0])
            if (module_has_slcc):
                test.log.info("The Call ID from SLCC is " + call_array_r1[1])
                if not call_array_r1[4]:
                    test.log.info("ID for CLCC and SLCC is not the same")
                    test.expect(False)

            test.log.step ('Step 2.2: R2 call DUT call and DUT accept the call')
            # ==============================================================
            test.expect(test.r2.at1.send_and_verify("atd" + "*31#" + str(tln_dut_nat) + ";" , "OK"))
            test.expect(test.dut.at1.wait_for("CCWA: ", timeout=30))
            incoming_number = test.dut.dstl_strip_number(test.dut.at1.last_response)
            call_array_r2 = test.dut.dstl_clcc_slcc_check(incoming_number, module_has_slcc)
            test.expect(test.dut.dstl_requested_call_state("Waiting_mtc", call_array_r2, module_has_slcc))
            test.expect(test.dut.at1.send_and_verify("at+chld=2", "OK"))
            test.sleep(wait_time)

            test.log.info("Call state from R2 call is: " + str(call_array_r2[2]))

            call_array_r2 = test.dut.dstl_clcc_slcc_check(incoming_number, module_has_slcc)
            multi_call_array_r1 = test.dut.dstl_clcc_slcc_check (tln_r1_nat, module_has_slcc)

            test.log.step ('Step 2.3: check Call states')
            # ==============================================================
            # check the call states and IDs
            # call to R1 must be active
            # test.expect(test.dut.dstl_requested_call_state("held", call_array_r1, module_has_slcc))
            test.expect(test.dut.dstl_requested_call_state("held", multi_call_array_r1, module_has_slcc))
            test.expect(test.dut.dstl_requested_call_state("active", call_array_r2, module_has_slcc))

            # # call from R2 must be waiting
            # test.expect(test.dut.dstl_check_call(call_array_r2, "0", incoming_number, module_has_slcc, False))

            test.log.step('Step 2.4: DUT toggle the call with at+chld=2')
            # ==================================================================
            test.expect(test.dut.at1.send_and_verify("at+chld=2", "OK"))
            test.sleep(wait_time)
            multi_call_array_r1 = test.dut.dstl_clcc_slcc_check(tln_r1_nat, module_has_slcc)
            multi_call_array_r2 = test.dut.dstl_clcc_slcc_check(incoming_number, module_has_slcc)

            test.expect(test.dut.dstl_compare_call_ids (call_array_r1, multi_call_array_r1, module_has_slcc))
            test.expect(test.dut.dstl_compare_call_ids (call_array_r2, multi_call_array_r2, module_has_slcc))
            test.expect(test.dut.dstl_requested_call_state("active", multi_call_array_r1, module_has_slcc))
            test.expect(test.dut.dstl_requested_call_state("held", multi_call_array_r2, module_has_slcc))

            test.log.step('Step 2.5: DUT start conference call with at+chld=3')
            # ==================================================================
            test.expect(test.dut.at1.send_and_verify("at+chld=3", "OK"))
            test.sleep(wait_time)
            test.expect(test.dut.at1.send_and_verify("at+clcc"))

            test.log.step ('Step 2.6: Compare the call IDs before and after the start of Mulitparty')
            # ==============================================================
            multi_call_array_r1 = test.dut.dstl_clcc_slcc_check (tln_r1_nat, module_has_slcc)
            multi_call_array_r2 = test.dut.dstl_clcc_slcc_check (incoming_number, module_has_slcc)

            test.log.info("check if the call IDs are correct")
            test.expect(test.dut.dstl_compare_call_ids (call_array_r1, multi_call_array_r1, module_has_slcc))
            test.expect(test.dut.dstl_compare_call_ids (call_array_r2, multi_call_array_r2, module_has_slcc))

            test.log.info("check if the calls are in Multiparty State")
            test.expect(test.dut.dstl_check_call(multi_call_array_r1, "0", tln_r1_nat, module_has_slcc, True))
            test.expect(test.dut.dstl_check_call(multi_call_array_r2, "0", incoming_number, module_has_slcc, True))

            test.log.info("check the number of calls in clcc/slcc")
            test.expect(test.dut.dstl_check_number_of_calls(2, module_has_slcc))

            test.log.info("check the current Network")
            test.expect(test.dut.dstl_check_current_network(requested_network_rat))

            test.log.step ('Step 2.7: terminate the calls via chup')
            # ==============================================================
            test.expect(test.dut.at1.send_and_verify(tln_dut_hang_up_call, "OK"))
            test.dut.dstl_check_call_state_all(test.r1, test.r2, module_has_slcc, tln_dut_hang_up_call, tln_r1_hang_up_call,
                                               tln_r2_hang_up_call)
            test.clean_arrays()
            test.sleep(wait_time)
        # ==============================================================

        if not call_waiting:
            # ==============================================================
            test.log.step('Step 3.0: skipped, because multiparty is not working for these SIM\n'
                          'Multiparty Test 3 #\n'
                          '- B call DUT and DUT accept call\n'
                          '- DUT call A and A accept call\n'
                          '- DUT start conference call\n'
                         '- terminate all calls via chup')
        else:
            # ==============================================================
            test.log.step('Step 3.0: Multiparty Test 2 #\n'
                          '- B call DUT and DUT accept call\n'
                          '- DUT call A and A accept call\n'
                          '- DUT start conference call\n'
                          '- terminate all calls via chup')

            test.log.step ('Step 3.1: R1 call DUT call and DUT accept the call')
            # ==============================================================
            test.log.info("active call waiting")
            test.expect(test.dut.at1.send_and_verify("atd*43#;", "CCWA: 1,"))
            test.expect(test.dut.at1.send_and_verify("at+CCWA=1;", "OK"))
            test.sleep(wait_time)

            test.expect(test.r1.dstl_voice_call_by_number(test.dut, tln_dut_int))
            #incoming_number = test.dut.dstl_strip_number(test.dut.at1.last_response)
            call_array_r1 = test.dut.dstl_clcc_slcc_check(tln_r1_int, module_has_slcc)
            test.expect(test.dut.dstl_requested_call_state("active", call_array_r1, module_has_slcc))
            test.log.info("Call state from R1 call is: " + str(call_array_r1[2]))
            test.sleep(wait_time)

            test.log.step ('Step 3.2: R2 call DUT call and DUT accept the call')
            # ==============================================================
            test.expect(test.r2.at1.send_and_verify("atd" + "*31#" + str(tln_dut_nat) + ";" , "OK"))
            test.expect(test.dut.at1.wait_for("CCWA: ", timeout=30))
            incoming_number = test.dut.dstl_strip_number(test.dut.at1.last_response)
            call_array_r2 = test.dut.dstl_clcc_slcc_check(incoming_number, module_has_slcc)
            test.expect(test.dut.dstl_requested_call_state("Waiting_mtc", call_array_r2, module_has_slcc))
            test.expect(test.dut.at1.send_and_verify("at+chld=2", "OK"))
            test.sleep(wait_time)
            call_array_r2 = test.dut.dstl_clcc_slcc_check(incoming_number, module_has_slcc)
            test.log.info("Call state from R2 call is: " + str(call_array_r2[2]))

            call_array_r2 = test.dut.dstl_clcc_slcc_check(incoming_number, module_has_slcc)
            multi_call_array_r1 = test.dut.dstl_clcc_slcc_check (tln_r1_int, module_has_slcc)

            test.log.step ('Step 3.3: check Call states')
            # ==============================================================
            # check the call states and IDs
            # call to R1 must be active
            test.expect(test.dut.dstl_requested_call_state("held", multi_call_array_r1, module_has_slcc))
            test.expect(test.dut.dstl_requested_call_state("active", call_array_r2, module_has_slcc))

            test.log.step('Step 3.4: DUT toggle the call with at+chld=2')
            # ==================================================================
            test.expect(test.dut.at1.send_and_verify("at+chld=2", "OK"))
            test.sleep(wait_time)
            multi_call_array_r1 = test.dut.dstl_clcc_slcc_check(tln_r1_int, module_has_slcc)
            multi_call_array_r2 = test.dut.dstl_clcc_slcc_check(incoming_number, module_has_slcc)

            test.expect(test.dut.dstl_compare_call_ids (call_array_r1, multi_call_array_r1, module_has_slcc))
            test.expect(test.dut.dstl_compare_call_ids (call_array_r2, multi_call_array_r2, module_has_slcc))
            test.expect(test.dut.dstl_requested_call_state("active", multi_call_array_r1, module_has_slcc))
            test.expect(test.dut.dstl_requested_call_state("held", multi_call_array_r2, module_has_slcc))

            test.log.step('Step 3.5: DUT start conference call with at+chld=3')
            # ==================================================================
            test.expect(test.dut.at1.send_and_verify("at+chld=3", "OK"))
            test.sleep(wait_time)
            test.expect(test.dut.at1.send_and_verify("at+clcc"))

            test.log.step ('Step 3.6: Compare the call IDs before and after the start of Mulitparty')
            # ==============================================================
            multi_call_array_r1 = test.dut.dstl_clcc_slcc_check (tln_r1_int, module_has_slcc)# int nummer
            multi_call_array_r2 = test.dut.dstl_clcc_slcc_check (incoming_number, module_has_slcc)

            test.log.info("check if the call IDs are correct")
            test.expect(test.dut.dstl_compare_call_ids (call_array_r1, multi_call_array_r1, module_has_slcc))
            test.expect(test.dut.dstl_compare_call_ids (call_array_r2, multi_call_array_r2, module_has_slcc))

            test.log.info("check if the calls are in Multiparty State")
            test.expect(test.dut.dstl_check_call(multi_call_array_r1, "0", tln_r1_int, module_has_slcc, True))
            test.expect(test.dut.dstl_check_call(multi_call_array_r2, "0", incoming_number, module_has_slcc, True))

            test.log.info("check the number of calls in clcc/slcc")
            test.expect(test.dut.dstl_check_number_of_calls(2, module_has_slcc))

            test.log.info("check the current Network")
            test.expect(test.dut.dstl_check_current_network(requested_network_rat))

            test.log.step ('Step 3.7: terminate the calls via chup')
            # ==============================================================
            test.expect(test.dut.at1.send_and_verify(tln_dut_hang_up_call, "OK"))
            test.dut.dstl_check_call_state_all(test.r1, test.r2, module_has_slcc, tln_dut_hang_up_call, tln_r1_hang_up_call,
                                               tln_r2_hang_up_call)
            test.clean_arrays()
            test.sleep(wait_time)

        # ==============================================================
        test.log.step('Step 4.0: Multiparty Test 2 #\n'
                      '- A call DUT and DUT accept call\n'
                      '- DUT call B and B accept call\n'
                      '- DUT start conference call\n'
                      '- terminate all calls via chup')

        test.log.step('Step 4.1: R1 call DUT call and DUT accept the call')
        # ==============================================================
        test.expect(test.r1.dstl_voice_call_by_number(test.dut, tln_dut_int))
        # incoming_number = test.dut.dstl_strip_number(test.dut.at1.last_response)
        call_array_r1 = test.dut.dstl_clcc_slcc_check(tln_r1_int, module_has_slcc)
        test.expect(test.dut.dstl_requested_call_state("active", call_array_r1, module_has_slcc))
        test.log.info("Call state from R1 call is: " + str(call_array_r1[2]))
        test.sleep(wait_time)

        test.log.step('Step 4.2: DUT call R2 and R2 accept the call')
        # ==============================================================
        test.expect(test.dut.dstl_voice_call_by_number(test.r2, tln_r2_nat))
        test.sleep(wait_time)
        call_array_r2 = test.dut.dstl_clcc_slcc_check(tln_r2_nat, module_has_slcc)
        multi_call_array_r1 = test.dut.dstl_clcc_slcc_check(tln_r1_int, module_has_slcc)
        multi_call_array_r2 = test.dut.dstl_clcc_slcc_check(tln_r2_nat, module_has_slcc)

        test.sleep(wait_time)

        test.log.step('Step 4.3: start multiparty with chld=3')
        # ==============================================================
        test.expect(test.dut.at1.send_and_verify("at+chld=3", "OK"))
        test.sleep(wait_time)
        test.expect(test.dut.at1.send_and_verify("at+clcc"))

        test.log.step('Step 4.4: Compare the call IDs before and after the start of Mulitparty')
        # ==============================================================
        multi_call_array_r1 = test.dut.dstl_clcc_slcc_check(tln_r1_int, module_has_slcc)
        multi_call_array_r2 = test.dut.dstl_clcc_slcc_check(tln_r2_nat, module_has_slcc) ###

        test.log.info("check if the call IDs are correct")
        test.expect(test.dut.dstl_compare_call_ids(call_array_r1, multi_call_array_r1, module_has_slcc))
        test.expect(test.dut.dstl_compare_call_ids(call_array_r2, multi_call_array_r2, module_has_slcc))

        test.log.info("check if the calls are in Multiparty State")
        test.expect(test.dut.dstl_check_call(multi_call_array_r1, "0", tln_r1_int, module_has_slcc, True))
        test.expect(test.dut.dstl_check_call(multi_call_array_r2, "0", tln_r2_nat, module_has_slcc, True))

        test.log.info("check the number of calls in clcc/slcc")
        test.expect(test.dut.dstl_check_number_of_calls(2, module_has_slcc))

        test.log.info("check the current Network")
        test.expect(test.dut.dstl_check_current_network(requested_network_rat))

        test.log.step('Step 4.5: terminate the calls via chup')
        # ==============================================================
        test.expect(test.dut.at1.send_and_verify(tln_dut_hang_up_call, "OK"))
        test.sleep(wait_time)
        test.dut.dstl_check_call_state_all(test.r1, test.r2, module_has_slcc, tln_dut_hang_up_call, tln_r1_hang_up_call,
                                           tln_r2_hang_up_call)
        test.clean_arrays()
        test.sleep(wait_time)
        # ==============================================================




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

        test.log.info("hangup calls, if the test abort before")
        test.dut.dstl_check_call_state_all(test.r1, test.r2, module_has_slcc, tln_dut_hang_up_call, tln_r1_hang_up_call,
                                           tln_r2_hang_up_call)

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
