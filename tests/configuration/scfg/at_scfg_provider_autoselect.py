# responsible: christian.gosslar@thalesgroup.com
# location: Berlin
# LM0004975.004 - LM0004985.004  - TC0093811.001
# TC0093811.001


import unicorn
import random
from dstl.auxiliary import init
from core.basetest import BaseTest
from dstl.security.lock_unlock_sim import *
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.devboard.devboard import *
from dstl.network_service import register_to_network
from dstl.identification.collect_module_infos import dstl_collect_module_info
from dstl.identification.get_revision_number import dstl_get_revision_number
from dstl.identification.get_imei import dstl_get_imei
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.check_c_revision_number import dstl_check_c_revision_number
from dstl.identification.get_part_number import dstl_check_or_read_part_number

#
testcase_id = "LM0004975.004 - LM0004985.004  - TC0093811.001"
ver = "1.2"
autoselect_setting = ""
provider_startup_setting = ""
viper_wait_timer = 480


class AtScfgProviderAutoselect(BaseTest):

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + '*****')
        test.log.com('***** Ver: ' + str(ver) + ' - Start *****')
        test.log.com("***** " + testcase_id + " *****")
        test.log.com('***** Collect some Module Infos *****')
        #test.dut.dstl_switch_off_at_echo(serial_ifc=0)
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.dut.dstl_get_bootloader()
        test.dut.dstl_check_c_revision_number()
        test.dut.dstl_collect_module_info()
        test.dut.dstl_check_or_read_part_number(only_read=True)
        pass

    def run(test):
        # define some variables
        scfg_special_response = False    # set true, if scfg response can't display "_"
        global autoselect_setting
        global provider_startup_setting
        stepline = '\n===================================================='

        provider_list = []

        if test.dut.project == 'VIPER':
            scfg_special_response = True

        test.log.step('Step 0.1: check the PIN & SIM card' + stepline)
        # ==============================================================
        test.dut.dstl_register_to_network()
        test.expect(test.dut.at1.send_and_verify("at+cscs=\"GSM\"", ".*OK.*"))
        test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/AutoSelect", ".*OK.*")
        autoselect_setting = test.dut.at1.last_response

        test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/cfg", ".*OK.*")
        provider_startup_setting = test.dut.at1.last_response
        provider_startup_setting = provider_startup_setting[provider_startup_setting.index("Cfg\",")+6:]
        provider_startup_setting = provider_startup_setting[:provider_startup_setting.index("\"")]
        if scfg_special_response:
            # special handling Viper and scfg output
            provider_startup_setting = provider_startup_setting.replace("\\11", "_")

        test.log.step('Step 1.0: check if Autofallback exist in Provider list' + stepline)
        # ==============================================================
        test.log.info("Fallback entry is marked with \"*\"")
        test.expect(test.dut.at1.send_and_verify("ati61", ".*\*.*OK.*"))

        # we have read ati61, build direct a list of the provider Names and IDs

        res = test.dut.at1.last_response
        ati_list = res.split('\r\n')
        for n in ati_list:
            if (" " in n) and ("MIMG" not in n):
                test.log.info("zeile: >" + n)
                [prov_name, prov_id] = n.split(' ')
                # if (test.dut.project == 'VIPER'):
                prov_name = prov_name.replace("*", "")
                provider_list += [prov_name, prov_id]
            # else:
            #    test.log.info ("There is no space in the line or the MIMG line")

        test.log.step('Step 2.0: check if all providers are also listed in scfg=?' + stepline)
        # ==============================================================
        scfg_line = ""
        test.expect(test.dut.at1.send_and_verify("at^scfg=?", ".*.*OK.*"))
        res = test.dut.at1.last_response
        if "MEopMode/Prov/Cfg" in res:
            responselines = test.dut.at1.last_response.splitlines()
            m = len(responselines)
            n = 0
            while n < m:
                if "MEopMode/Prov/Cfg" in responselines[n]:
                    scfg_line = responselines[n]
                    n = m
                n += 1
        n = 0
        if scfg_special_response:
            # special handling Viper and scfg output
            scfg_line = scfg_line.replace("\\11", "_")
        scfg_line = scfg_line.replace("(", "")
        scfg_line = scfg_line.replace(")", "")
        scfg_line = scfg_line.replace("*", "")

        while n < len(provider_list):
            provider = provider_list[n]
            if provider in scfg_line:
                test.log.info("found entry: " + provider_list[n] + " = " + provider_list[n+1] + " in scfg line")
                test.expect(True)
            else:
                test.log.info("entry: " + provider_list[n] + " = " + provider_list[n + 1] + " NOT found in scfg line")
                test.expect(False)
            n += 2

        scfg_prov_list = scfg_line.split(',')
        n = 1
        while n < len(scfg_prov_list):
            provider_from_scfg = scfg_prov_list[n]
            provider_from_scfg = re.sub("\"", "", provider_from_scfg)
            provider_from_scfg = re.sub("\*", "", provider_from_scfg)
            i = 0
            scfg_provider_found = False
            while i < len(provider_list):
                if provider_from_scfg in provider_list[i]:
                    test.expect(True)
                    test.log.info("Found a Provider Config name in the scfg list, which is in the ati61 list")
                    test.log.info("SCFG  entry: >" + provider_from_scfg + "<")
                    test.log.info("ati61 entry: >" + provider_list[i] + "<")
                    scfg_provider_found = True
                    i = len(provider_list)
                i += 2
            if not scfg_provider_found:
                test.log.info("Found a Provider Config name in the scfg list, which is no in the ati61 list")
                test.log.info("SCFG  entry: >" + provider_from_scfg + "<")
                test.expect(False)
            else:
                test.log.info("Found a same Provider Config name in the scfg list and ati61")
                test.log.info("SCFG  entry: >" + provider_from_scfg + "<")
                test.expect(True)

            n += 1

        test.log.step('Step 3.0: select all providers from ati61 with manual provider select' + stepline)
        # ==============================================================
        test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/AutoSelect,\"off\"", ".*OK.*"))
        test.expect(test.dut.dstl_restart())
        test.sleep(2)
        test.expect(test.dut.dstl_enter_pin())

        test.log.step('Step 3.1: select the provider from tha ati61 list' + stepline)
        i = 0
        att_switch = False
        while i < len(provider_list):
            test.log.step("Step 3.1." + str(i) + ": select the provider: >" + provider_list[i] + "<")

            if ("ATT" in provider_list[i] or "FirstNet" in provider_list[i] or "CDMAless-Verizon" in provider_list[i]
                    or att_switch is True) and (test.dut.project == 'VIPER'):
                if "ATT" in provider_list[i] or "FirstNet" in provider_list[i] or "CDMAless-Verizon" in provider_list[i]:
                    # set the flag to true
                    att_switch = True
                else:
                    # toggle flag
                    att_switch = False
                test.log.info("Viper need " + str(viper_wait_timer) + " Seconds to switch to or from ATT image")
                test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/Cfg,\"" + provider_list[i] + "\"",
                                                         ".*OK.*"))
                test.sleep(viper_wait_timer)
                test.expect(test.dut.at1.send_and_verify("ati", ".*OK.*"))
                test.log.info("need select the prov setting again")
                test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/Cfg,\"" + provider_list[i] + "\"",
                                                         ".*OK.*"))
            else:
                test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/Cfg,\"" + provider_list[i] + "\"",
                                                         ".*OK.*"))
            test.sleep(5)
            test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/Cfg"))
            if not scfg_special_response:
                test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/Cfg", provider_list[i]))
            else:
                # special Handling for module, which don't display the scfg answer correct
                res = test.dut.at1.last_response
                res = res.replace("\\11", "_")
                if provider_list[i] in res:
                    test.expect(True)
                    test.log.info("provider Entry is correct")
                else:
                    test.expect(False)
                    test.log.info("provider Entry is NOT correct for >" + str(provider_list[i]) + "<")

            test.expect(test.dut.at1.send_and_verify("ati61", ".*." + provider_list[i] + ".*OK.*"))
            i += 2

            # check if APN setting has changed and is not empty:
            test.expect(test.dut.at1.send_and_verify("at+cgdcont?", ".*OK.*"))
            if 'CGDCONT: 1,"IPV4V6","",' in test.dut.at1.last_response or \
                    'CGDCONT: 1,"IP","",' in test.dut.at1.last_response:
                test.expect(False, msg="empty APN setting found! please check if setting is correct or not!")

            # END_OF: while i < len(provider_list):

        if att_switch is True:
            test.log.info("Viper need " + str(viper_wait_timer) + " Seconds to switch to or from ATT image")
            test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/Cfg,\"" + provider_startup_setting
                                                     + "\"", ".*OK.*"))
            test.sleep(viper_wait_timer)
            test.expect(test.dut.at1.send_and_verify("ati", ".*OK.*"))
            test.log.info("need select the prov setting again")
            test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/Cfg,\"" + provider_startup_setting + "\"",
                                                     ".*OK.*"))
        pass

    def cleanup(test):
        """Cleanup method.
        Steps to be executed after test run steps.
        """
        # ==============================================================
        test.log.com('**** log  dir: ' + test.workspace + ' ****')

        test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/AutoSelect", ".*OK.*")
        res = test.dut.at1.last_response
        restart_flag = False
        if ("on" in autoselect_setting) and ("off" in res):
            test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/AutoSelect,\"on\"", ".*OK.*"))
            restart_flag = True
        elif ("off" in autoselect_setting) and ("on" in res):
            test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/AutoSelect,\"off\"", ".*OK.*"))
            test.sleep(5)
            test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/cfg," + provider_startup_setting, ".*OK.*"))
            restart_flag = True

        if restart_flag:
            test.expect(test.dut.dstl_restart())

        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')
        pass


if __name__ == "__main__":
    unicorn.main()
