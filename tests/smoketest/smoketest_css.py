# author: christian.gosslar@thalesgroup.com
# responsible: christian.gosslar@thalesgroup.com
# location: Berlin
# TC0095598.001
# jira: xxx
# feature: LM0000029.001, LM0000032.001, LM0000033.001, LM0000040.001, LM0000057.001, LM0001216.001, LM0001218.001
# LM0001220.001, LM0001478.001, LM0003202.001, LM0003202.002, LM0003202.003, LM0005638.001, LM0005638.003
# LM0007422.001

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
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.sms_memory_capacity import dstl_get_sms_memory_capacity
from dstl.sms.write_sms_to_memory import dstl_write_sms_to_memory
# from dstl.sms.send_sms_message import dstl_send_sms_message_from_memory
from dstl.network_service.register_to_network import dstl_register_to_network

#from dstl.network_service.register_to_network import dstl_enter_pin
#from dstl.security.lock_unlock_sim import dstl_unlock_sim
#from dstl.security.lock_unlock_sim import dstl_lock_sim
#from dstl.auxiliary.restart_module import dstl_restart
#from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board

import re

class Test(BaseTest):

    def CheckForVoLteCall(test,CheckVoLteTN):
        ' check if we have a VoLTE call'
        if CheckVoLteTN :
            if not (re.search(test.dut.project, 'DAHLIA')):
                test.dut.at1.send_and_verify("at+CAVIMS?", "OK")
            test.dut.at1.send_and_verify("at^smoni", "OK")
            res = test.dut.at1.last_response
            if not ("4G" in res):
                test.log.info("no 4G entry found")
                test.expect(False)
        return 0

    def CheckCall(test):
        if not (re.search(test.dut.project, 'TIGER')):
            test.expect(test.dut.at1.send_and_verify("at+clcc", "OK"))
        if not (re.search(test.dut.project, 'VIPER')):
            test.expect(test.dut.at1.send_and_verify("at+cpas", "OK"))
        test.expect(test.r1.at1.send_and_verify("at+clcc", "OK"))
        return 0


    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.log.com('***** Collect some Module Infos *****')
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.dut.dstl_get_bootloader()
        test.dut.dstl_check_c_revision_number()
        test.dut.dstl_collect_module_info()
        test.dut.dstl_collect_module_info_for_mail()

        test.r1.dstl_detect()
        test.r1.dstl_get_imei()

    def run(test):
        """
        Intention:
        Check of CCS calls MO and MT
        """

        # define some fixe values
        #

        waitTimeBeforeClcc = 3
        iWaitTimeBeforeRing = 30

        tln1nat = test.dut.sim.nat_voice_nr
        tln1int = test.dut.sim.nat_voice_nr
        tln2nat = test.r1.sim.nat_voice_nr
        tln2int = test.r1.sim.int_voice_nr
        tln1natB = tln1nat

        NetworkID = test.dut.sim.imsi[:5]

        bDataCentricOnly = False
        ModulHasATTP =True
        bWithoutShup = False
        bVoiceDisabledViaSpec = False
        bCheckForVoLTEonTN = False
        bLongVoiceCall = True

        tln1HangUpCall = "ath"
        tln2HangUpCall = "ath"

        test.log.step('Step 1: Enter pin')
        test.dut.dstl_register_to_network()
        test.r1.dstl_register_to_network()

        # set project depend values
        if (re.search(test.dut.project, 'TIGER|QUINN|RHEA|URANUS|WIRTANEN|HALIFAX|MIAMI|FLORENCE|ZURICH|BOBCAT')):
            tln1HangUpCall = "at+chup"
            bCheckForVoLTEonTN = False

        if (re.search(test.dut.project, 'JAKARTA|VIPER')):
            ModulHasATTP = False

        if (re.search(test.r1.project, 'IRIS|QUINN|RHEA|URANUS|WIRTANEN|HALIFAX|MIAMI|FLORENCE|ZURICH|BOBCAT')):
            tln2HangUpCall = "at+chup"
            test.expect(test.r1.at1.send_and_verify("atx4", "OK")) 	# QCT has ATX0 as default, but BUSY detection is necessary here

        if bCheckForVoLTEonTN:
            test.log.info (" ### VoLTE only product  - we check for VoLTE specific calls here ###")
            test.log.info (" ### due to restrictions of LTE-TN we perform int. calls only ###")
            tln2nat = tln2int
            tln1nat = tln1int

        if bDataCentricOnly:
            test.log.info('The Module has no Voice calls, only data calls. Make some negativ tests')
            if bVoiceDisabledViaSpec:
                test.expect(test.dut.at1.send_and_verify("at+CAVIMS?", ".*CAVIMS: 0.*OK"))
            else:
                test.expect(test.dut.at1.send_and_verify("at+CAVIMS?", ".*+CME ERROR: 4.*"))
                #test.expect(test.dut.at1.send_and_verify("atd911;", ".*NO CARRIER.*"))
                # hangup call, we will not make a emergency call
                #test.dut.at1.send_and_verify(tln1HangUpCall, ".*")
                test.expect(test.dut.at1.send_and_verify("atd" + str(tln2nat) + ";", ".*NO CARRIER.*"))
                test.dut.at1.send_and_verify(tln1HangUpCall, ".*")
                test.expect(test.dut.at1.send_and_verify("at+ccwa=1,1", ".*ERROR.*"))
                test.expect(test.dut.at1.send_and_verify("at+clip?", ".*ERROR.*"))
                test.expect(test.dut.at1.send_and_verify("at+clir?", ".+ERROR.*"))
                test.expect(test.dut.at1.send_and_verify("at+ccfc?", ".*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("at+CVMOD=?", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("at+CVMOD?", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("at+clcc", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("at+cpas", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("ata", ".*NO CARRIER.*"))
            test.expect(test.dut.at1.send_and_verify("at+ccwa?", ".*OK.*"))

            test.log.info("##> Abort Testcase, module has no voice call.")
            test.fail()
            ######## end else

        test.log.step('Step 2: check the provider config if needed')
        if bCheckForVoLTEonTN:
            test.log.info(" ### VoLTE product found - we check for VoLTE specific calls here ###")
            test.expect(test.dut.at1.send_and_verify("at^scfg?"))
            response = test.dut.at1.last_response
            test.log.info("### For TestNet Bln we set the Provider config, for all other please check ###")
            if (( "26295" in NetworkID) and  not ( "SCFG: \"MEopMode/Prov/Cfg\",\"tn1de\"" in response) ):
                test.log.info("Testnet is active and provider coinfig is NOT set to testNet, change it")
                test.log.info("disabling AutoSelect will need a restart, but we will not do it here")
                test.expect(test.dut.at1.send_and_verify("at^scfg=\"MEopMode/Prov/AutoSelect\",\"off\""))
                test.expect(test.dut.at1.send_and_verify("at^scfg=\"MEopMode/Prov/Cfg\",\"tn1de\""))

        # todo later, because Tiger has no band selcetion
        #	# activate all Band of the module
        #	TpMcBand.callTp(_wmName[wm1],_wmName[wm3], "ALL0");

        # test.log.info("###=> Test with at+cops=0")
        # test.expect(test.dut.at1.send_and_verify("at+cops=0","OK"))
        # test.sleep(30)

        test.log.step("Step 3: normal MO calls: DUT -> remote")
        test.expect(test.dut.at1.send_and_verify("atd" + str(tln2nat) + ";", ".*OK.*"))
        test.r1.at1.wait_for("RING", timeout=iWaitTimeBeforeRing)
        test.expect(test.r1.at1.send_and_verify("ata", "OK"))
        test.sleep(waitTimeBeforeClcc)
        test.CheckCall()
        if bLongVoiceCall:
            test.log.info ("first MO call, hold the call for 90 sec")
            test.sleep(90)
            bLongVoiceCall = False
        if "ath" in tln1HangUpCall:
            if bWithoutShup:
                test.expect(test.dut.at1.send_and_verify(tln1HangUpCall, "OK"))
            else:
                if ("26201" in NetworkID) or ("26001" in NetworkID):
                    test.expect(test.dut.at1.send_and_verify("ath", "OK"))
                else:
                    test.expect(test.dut.at1.send_and_verify("at^shup=27", "OK"))
        else:
            test.expect(test.dut.at1.send_and_verify(tln1HangUpCall, "OK"))

        test.r1.at1.wait_for("NO CARRIER", timeout=30)

        bLongVoiceCall = True
        test.sleep(5)

        test.log.step("Step 4: normal MT calls: remote -> DUT")

        test.log.info("LTE-TN and 2nd device is 3G only, then add prefix")
        if (("26295" in NetworkID) and ( re.search(test.dut.project, 'JAKARTA'))):
            if tln1nat.startswith("0"):
                tln1natB = "9749" + tln1nat[:1]
            elif tln1nat.startswith("+49"):
                tln1natB = "9749" + tln1nat[:2]
            test.log.info("using dailing Prefix: " + tln1natB)

        test.expect(test.r1.at1.send_and_verify("atd" + str(tln1natB) + ";", ".*OK.*"))
        if (re.search(test.dut.project, 'TIGER')):
            test.sleep(5)
            test.expect(test.dut.at1.send_and_verify("at+clcc", "OK"))
        else:
            test.dut.at1.wait_for("RING", timeout=iWaitTimeBeforeRing)
        test.expect(test.dut.at1.send_and_verify("ata", "OK"))
        test.sleep(waitTimeBeforeClcc)
        test.CheckCall()
        if bLongVoiceCall:
            test.log.info ("first MT call, hold the call for 90 sec")
            test.sleep(90)
            bLongVoiceCall = False
        test.sleep(10)
        test.expect(test.r1.at1.send_and_verify(tln2HangUpCall, "OK"))
        if not (re.search(test.dut.project, 'TIGER')):
            test.dut.at1.wait_for("NO CARRIER", timeout=30)

        test.sleep(5)

        test.log.step("Step 5: normal calls MO with Tone and Puls setting att & atp")

        for i in range (0,2):
            if ( ModulHasATTP):
                # select Pulse and tone dailing if possible
                if i==0:
                    test.log.step("Step 5.1: tone calls")
                    test.expect(test.dut.at1.send_and_verify("att","OK"))
                else:
                    test.log.step("Step 5.2: tone calls")
                    test.expect(test.dut.at1.send_and_verify("atP", "OK"))
            test.expect(test.dut.at1.send_and_verify("atd" + tln2nat + ";", "OK"))
            test.r1.at1.wait_for("RING", timeout=iWaitTimeBeforeRing)
            test.expect(test.r1.at1.send_and_verify("ata", "OK"))
            test.sleep(waitTimeBeforeClcc)
            test.CheckForVoLteCall(bCheckForVoLTEonTN)
            test.CheckCall()
            test.expect(test.dut.at1.send_and_verify(tln1HangUpCall, "OK"))
            test.r1.at1.wait_for("NO CARRIER", timeout=30)
            test.sleep(5)

        test.log.step("Step 6: normal calls MO with modifiers ")
        if ((re.search(test.dut.project, 'BOBCAT') and ((test.dut.step == '2') or (test.dut.step == '3'))) ):
            test.log.info("Workaround for IPIS100264424 - Dialing modifiers of ATD are not ignored")
            test.log.info("Bobcat2 can't use modifier")
            dailingArray = ["","","","","","","","",""]
        elif (re.search(test.dut.project, 'TIGER')):
            dailingArray =["W", ",", "T", "P"]
        elif (re.search(test.dut.project, 'VIPER')):
            dailingArray = [",", "T", "!", "W", "@", "A", "B", "C", "D", "P"]
        elif test.dut.platform == 'QCT':
            dailingArray = [",", "T", "!", "W", "@", "A", "B", "C", "D"]
        else:
            dailingArray = [",", "T", "!", "W", "@", ",", ",", ",", ","]
        modi=""
        for n in range(0, len(dailingArray)):
            modi = modi + " - " + dailingArray[n]
        test.log.step("use modifiers \"" + modi + "\"")

        for n in range(0, len(dailingArray)):
            test.log.info("make call and use modifier =>" + dailingArray[n] + "<=")
            test.expect(test.dut.at1.send_and_verify("atd" + dailingArray[n] + tln2nat + ";", "OK"))
            test.expect(test.r1.at1.wait_for("RING", timeout=iWaitTimeBeforeRing))
            test.expect(test.r1.at1.send_and_verify("ata", "OK"))
            test.sleep(waitTimeBeforeClcc)
            test.CheckForVoLteCall(bCheckForVoLTEonTN)
            test.CheckCall()
            test.expect(test.dut.at1.send_and_verify(tln1HangUpCall, "OK"))
            if not (re.search(test.dut.project, 'TIGER')):
                test.r1.at1.wait_for("NO CARRIER", timeout=30)
                test.expect(test.dut.at1.send_and_verify("at^sblk", "OK"))
            test.sleep(5)

        test.log.step("Step 7: normal calls MT ")
        test.expect(test.r1.at1.send_and_verify("atd" + str(tln1natB) + ";", ".*OK.*"))
        if (re.search(test.dut.project, 'TIGER')):
            test.sleep(5)
            test.expect(test.dut.at1.send_and_verify("at+clcc", "OK"))
        else:
            test.dut.at1.wait_for("RING", timeout=iWaitTimeBeforeRing)
        test.expect(test.dut.at1.send_and_verify("ata", "OK"))
        test.sleep(waitTimeBeforeClcc)
        test.CheckCall()
        test.sleep(10)
        test.expect(test.r1.at1.send_and_verify(tln1HangUpCall, "OK"))
        if not (re.search(test.dut.project, 'TIGER')):
            test.dut.at1.wait_for("NO CARRIER", timeout=30)

        test.log.step("Step 8: call remote user and remote user rejected the call ")
        test.expect(test.dut.at1.send_and_verify("atd" + tln2nat + ";", "OK"))
        test.r1.at1.wait_for("RING", timeout=iWaitTimeBeforeRing)
        test.expect(test.r1.at1.send_and_verify(tln2HangUpCall, "OK"))
        if not (re.search(test.dut.project, 'TIGER')):
            # todo step 3 aus dem alten smoketestcss einbauen, unterschiedliche result codes
            test.dut.at1.wait_for("NO CARRIER", timeout=30)
        test.sleep(5)

        test.log.step("Step 9: call from remote user and DUT rejected the call ")
        test.expect(test.r1.at1.send_and_verify("atd" + str(tln1nat) + ";", "OK"))
        if (re.search(test.dut.project, 'TIGER')):
            test.sleep(5)
        else:
            test.dut.at1.wait_for("RING", timeout=iWaitTimeBeforeRing)

        if bWithoutShup:
            test.expect(test.dut.at1.send_and_verify("ath", "OK"))
        else:
            test.expect(test.dut.at1.send_and_verify("at^SHUP=17", "OK"))
            test.expect(test.r1.at1.send_and_verify(tln2HangUpCall, "OK"))
            # todo create extra behaviour for TestNet Berlin if needed
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify(tln1HangUpCall, "OK"))
        test.expect(test.dut.at1.send_and_verify("at+cops=0", "OK"))
        test.expect(test.r1.at1.send_and_verify(tln2HangUpCall, "OK"))

    def cleanup(test):
        """Cleanup method.
		Nothing to do in this Testcase
        Steps to be executed after test run steps.
        """

        test.log.com(' ')
        test.log.com('****  log dir: ' + test.workspace + ' ****')

        test.log.com(' ')
        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')


if "__main__" == __name__:
    unicorn.main()
