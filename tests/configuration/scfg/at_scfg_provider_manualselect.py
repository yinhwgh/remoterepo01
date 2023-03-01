# responsible: christian.gosslar@thalesgroup.com
# location: Berlin
# LM0004048.003 - LM0004689.001 - LM0004689.002 - LM0004975.001 - LM0004975.002 - LM0004975.003 - LM0004975.004 -
# LM0004976.001 - LM0004976.002 - LM0004976.003 - LM0005586.001 -  LM0006684.001  - TC0094149.001
# TC0094149.001

import unicorn
from dstl.auxiliary import init
from core.basetest import BaseTest
from dstl.security.lock_unlock_sim import *
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.identification.collect_module_infos import dstl_collect_module_info
from dstl.identification.get_revision_number import dstl_get_revision_number
from dstl.identification.get_imei import dstl_get_imei
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.check_c_revision_number import dstl_check_c_revision_number
from dstl.identification.get_part_number import dstl_check_or_read_part_number
from dstl.packet_domain.pdp_context_operation import dstl_clear_contexts

testcase_id = "LM0004048.003 - LM0004689.001 - LM0004689.002 - LM0004975.001 - LM0004975.002 - LM0004975.003 - " \
              "LM0004975.004 - LM0004976.001 - LM0004976.002 - LM0004976.003 - LM0005586.001 -  LM0006684.001  " \
              "- TC0094149.001"

ver = "1.31"
default_provider_name = ""
att_switch = False
provider_startup_setting = ""
autoselect_setting = ""
viper_wait_timer = "480"


class AtScfgProviderManualselect(BaseTest):

    def delete_cgdcont(test):
        """
        please use dstl/packet_domain/pdp_context_operation.py

        delete all cgdcont entries
        to call via test.delect_cgdcont()"""
        test.expect(test.dut.at1.send_and_verify("at+cgdcont=?", "OK"))
        res = test.dut.at1.last_response
        max_id = int(res[res.index("1-")+2:res.index(")")])
        n = 1
        while n < (max_id+1):
            test.expect(test.dut.at1.send_and_verify("at+cgdcont=" + str(n), "OK"))
            n += 1
        test.expect(test.dut.at1.send_and_verify("at+cgdcont?", "OK"))
        return

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + '*****')
        test.log.com('***** Ver: ' + str(ver) + ' - Start *****')
        test.log.com("***** " + testcase_id + " *****")
        test.log.com('***** Collect some Module Infos *****')
        test.dut.dstl_switch_off_at_echo(serial_ifc=0)
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.dut.dstl_get_bootloader()
        test.dut.dstl_check_c_revision_number()
        test.dut.dstl_collect_module_info()
        test.dut.dstl_check_or_read_part_number(only_read=True)
        pass

    def run(test):
        # define some variables
        scfg_special_response = False
        provider_list = []
        global default_provider_name
        global autoselect_setting
        global att_switch
        global provider_startup_setting

        if test.dut.project == 'VIPER':
            default_provider_name = "ROW_Generic_3GPP"
            scfg_special_response = True
        if test.dut.project == 'BOBCAT':
            default_provider_name = "fallb3gpp"

        test.log.step('Step 0.1: delete cgdcont entries')
        # ==============================================================
        test.dut.dstl_clear_contexts()

        test.log.step('Step 0.2: save settings before Test')
        # ==============================================================
        test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/AutoSelect", ".*OK.*")
        autoselect_setting = test.dut.at1.last_response

        test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/cfg", ".*OK.*")
        provider_startup_setting = test.dut.at1.last_response
        provider_startup_setting = provider_startup_setting[provider_startup_setting.index("Cfg\",")+6:]
        provider_startup_setting = provider_startup_setting[:provider_startup_setting.index("\"")]
        provider_startup_setting = provider_startup_setting.replace("\*", "")
        if scfg_special_response:
            # special handling Viper and scfg output
            provider_startup_setting = provider_startup_setting.replace("\\11", "_")

        test.log.step('Step 0.3: disable autoselect')
        # ==============================================================
        test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/AutoSelect,\"off\"", ".*OK.*"))

        test.log.step('Step 0.4: build provider list from ati61')
        # ==============================================================
        test.expect(test.dut.at1.send_and_verify("ati61", ".*OK.*"))
        res = test.dut.at1.last_response
        ati_list = res.split('\r\n')
        for n in ati_list:
            if (" " in n) and ("MIMG" not in n):
                test.log.info("zeile: >" + n)
                n = re.sub("\*", "", n)
                [prov_name, prov_id] = n.split(' ')
                provider_list += [prov_name, prov_id]

        test.log.step('Step 1.1: select the last provider from list')
        # ==============================================================
        prov = provider_list[len(provider_list)-2]
        n = 4
        while ("ATT" in prov or "FirstNet" in prov or "CDMAless-Verizon" in prov) and (test.dut.project == 'VIPER'):
            prov = provider_list[len(provider_list) - n]
            n += 2

        test.expect(
            test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/Cfg,\"" + prov + "\"", ".*OK.*"))

        test.log.step('Step 1.2: restart module')
        # ==============================================================
        test.expect(test.dut.dstl_restart())

        # loop start
        test.log.step('Step 2.0: Loop start')
        # ==============================================================
        n = 0
        loop = 1
        att_switch = False
        while n < len(provider_list):
            test.log.step("Step 2." + str(n) + ": Loop " + str(loop)
                          + " start with Provider entry >" + provider_list[n] + "<")
            # ==============================================================

            test.log.step("Step 2." + str(n) + ": Loop " + str(loop) + 'delect cgdcont list')
            # ==============================================================
            test.dut.dstl_clear_contexts()

            test.log.info('check if cgdcont is empty')
            # ==============================================================
            test.expect(test.dut.at1.send_and_verify("at+cgdcont?", ".*OK.*"))
            res = test.dut.at1.last_response
            if "+CGDCONT: " in res:
                test.expect(False)
                test.log.info("CGDCONT entry is not empty")

            test.log.step("Step 2." + str(n) + ": Loop " + str(loop) + ' select provider '
                          + provider_list[n] + 'from ati61 list')
            # ==============================================================
            if ("ATT" in provider_list[n] or "FirstNet" in provider_list[n] or "CDMAless-Verizon" in provider_list[n] \
                    or att_switch is True) and (test.dut.project == 'VIPER'):
                if "ATT" in provider_list[n] or "FirstNet" in provider_list[n] or "CDMAless-Verizon" in provider_list[n]:
                    # set the flag to true
                    att_switch = True
                else:
                    # toggle flag
                    att_switch = False
                test.log.info("Viper need " + str(viper_wait_timer) + " Seconds to switch to or from ATT image")
                test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/Cfg,\"" + provider_list[n] + "\"", ".*OK.*"))
                test.sleep(viper_wait_timer)
                test.expect(test.dut.at1.send_and_verify("ati", ".*OK.*"))
                test.log.info("need select the prov setting again")
                test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/Cfg,\"" + provider_list[n] + "\"", ".*OK.*"))
            else:
                test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/Cfg,\"" + provider_list[n] + "\"", ".*OK.*"))
                test.sleep(5)

            test.log.info('restart module')
            # ==============================================================
            test.expect(test.dut.dstl_restart())

            test.log.info('check the current provider')
            # ==============================================================
            # test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/Cfg", provider_list[n]))
            test.expect(test.dut.at1.send_and_verify("ati"))
            if test.dut.project == 'BOBCAT':
                test.log.info ("Bobcat needs soem time, before all is ok with provider setting")
                test.sleep (60)
            test.expect(test.dut.at1.send_and_verify("at^scfg?"))
            test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/Cfg"))
            if not scfg_special_response:
                test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/Cfg", provider_list[n]))
            else:
                # special Handling for Viper, whcih don't display the scfg answer correct
                res = test.dut.at1.last_response
                res = res.replace("\\11", "_")
                if provider_list[n] in res:
                    test.expect(True)
                    test.log.info("provider Entry is correct")
                else:
                    test.expect(False)
                    test.log.info("provider Entry is NOT correct for >" + str(provider_list[n]) + "<")

            test.log.info('check if cgdcont is not empty')
            # ==============================================================
            test.expect(test.dut.at1.send_and_verify("at+cgdcont?", ".*OK.*"))
            res = test.dut.at1.last_response
            if "+CGDCONT: " in res:
                test.expect(True)
                test.log.info("CGDCONT entries exist - passed")
            else:
                test.expect(False)
                test.log.info("CGDCONT entry is empty - failed for provider: >" + provider_list[n] + "<")

            n += 2
            loop += 1
            # loop end
        test.log.step('Step 2.1: Loop end')
        # ==============================================================


    def cleanup(test):
        """Cleanup method.
        Steps to be executed after test run steps.
        """
        # ==============================================================
        test.log.com('**** log  dir: ' + test.workspace + ' ****')
        # global provider_startup_setting
        # autoselect_setting
        test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/AutoSelect", ".*OK.*")
        res = test.dut.at1.last_response
        if ("on" in autoselect_setting) and ("off" in res):
            test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/AutoSelect,\"on\"", ".*OK.*"))
            test.expect(test.dut.dstl_restart())
        elif "off" in autoselect_setting:
            test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/AutoSelect,\"off\"", ".*OK.*"))
            test.sleep(5)
            if att_switch is True:
                test.log.info("Viper need " + str(viper_wait_timer) + " Seconds to switch to or from ATT image")
                test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/Cfg,\""
                                                         + provider_startup_setting + "\"", ".*OK.*"))
                test.sleep(viper_wait_timer)
                test.expect(test.dut.at1.send_and_verify("ati", ".*OK.*"))
                test.log.info("need select the prov setting again")
                test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/Cfg,\"" + default_provider_name + "\"", ".*OK.*"))
            else:
                test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/Cfg,\"" + provider_startup_setting + "\"", ".*OK.*"))

        #        test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/AutoSelect,\"off\"", ".*OK.*"))
        # test.expect(test.dut.dstl_restart())

        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')
        pass


if __name__ == "__main__":
    unicorn.main()
