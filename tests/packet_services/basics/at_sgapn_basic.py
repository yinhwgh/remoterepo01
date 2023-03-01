# responsible: christian.gosslar@thalesgroup.com
# location: Berlin
# LM0004034.001 - LM0004045.001 - LM0004045.003 - LM0004045.004 - TC0094484.001
# TC0094484.001

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

ver = "1.0"


class AtSgapnBasic(BaseTest):
    testcase_id = "LM0004034.001 - LM0004045.001 - LM0004045.003 - LM0004045.004 " \
                  "- TC0094484.001"

    org_provider_config_name = ""

    def delete_cgdcont(test):
        """delete all cgdcont entries
        to call via test.delect_cgdcont()"""
        test.expect(test.dut.at1.send_and_verify("at+cgdcont=?", "OK"))
        res = test.dut.at1.last_response
        max_id = int(res[res.index("-")+1:res.index(")")])
        n = 1
        while n < (max_id+1):
            test.expect(test.dut.at1.send_and_verify("at+cgdcont=" + str(n), "OK"))
            n += 1
        test.expect(test.dut.at1.send_and_verify("at+cgdcont?", "OK"))
        return

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' Ver: ' + str(ver) + ' - Start *****')
        test.log.com("***** " + test.testcase_id + " *****")
        test.log.com('***** Collect some Module Infos *****')
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.dut.dstl_get_bootloader()
        test.dut.dstl_check_c_revision_number()
        test.dut.dstl_collect_module_info()
        test.dut.dstl_check_or_read_part_number(only_read=True)
        test.dut.devboard.send_and_verify("mc:asc0cfg=ext", ".*O.*")
        test.dut.devboard.send_and_verify("mc:asc1cfg=ext", ".*O.*")
        pass

    def run(test):
        # define some variables
        read_response = ".*\\^SGAPN: 1,1,\"IPV4V6\",\"vzwims\",\"LTE\",\"Enabled\",0" \
                        "\\s+\\^SGAPN: 2,2,\"IPV4V6\",\"vzwadmin\",\"LTE\",\"Enabled\",0" \
                        "\\s+\\^SGAPN: 3,3,\"IPV4V6\",\"vzwinternet\",\"LTE\",\"Enabled\",0" \
                        "\\s+\\^SGAPN: 4,4,\"IPV4V6\",\"vzwapp\",\"LTE\",\"Enabled\",0\\s+" + "OK.*"
        test_response = ".*\\^SGAPN: \\(1-16\\),\\(0-16\\),\\(\"IP\",\"PPP\",\"IPV6\",\"IPV4V6\"\\),," \
                        "\\(\"GSM\",\"WCDMA\",\"LTE\",\"ANY\"\\),\\(\"Enabled\",\"Disabled\"\\),\\(0-122820\\)\\s+" \
                        + "OK.*"
        '''
        default_setting = ["1,1,\"IPV4V6\",\"vzwims\",\"ANY\",\"Enabled\",0",
                            "2,2,\"IPV4V6\",\"VZWADMIN\",\"ANY\",\"Enabled\",0",
                            "3,3,\"IPV4V6\",\"VZWINTERNET\",\"ANY\",\"Enabled\",0",
                            "4,4,\"IPV4V6\",\"VZWAPP\",\"ANY\",\"Enabled\",0",
                            "6,0,\"IPV4V6\",\"VZWEMERGENCY\",\"ANY\",\"Enabled\",0"]
        '''
        icid_first_free = 1
        icid_max = 16
        step_separator = '\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'

        # define some project Varaibles
        if re.search(test.dut.project, 'VIPER'):
            vzw_image_name = "CDMAless-Verizon"
            read_response = ".*\\^SGAPN: 1,1,\"IPV4V6\",\"ims\",\"ANY\",\"Enabled\",0" \
                            "\\s+\\^SGAPN: 2,2,\"IPV4V6\",\"VZWADMIN\",\"ANY\",\"Enabled\",0" \
                            "\\s+\\^SGAPN: 3,3,\"IPV4V6\",\"VZWINTERNET\",\"ANY\",\"Enabled\",0" \
                            "\\s+\\^SGAPN: 4,4,\"IPV4V6\",\"VZWAPP\",\"ANY\",\"Enabled\",0" \
                            "\\s+\\^SGAPN: 5,0,\"IPV4V6\",\"VZWEMERGENCY\",\"ANY\",\"Enabled\",0" \
                            "\\s+\\^SGAPN: 6,0,\"IPV4V6\",\"VZWCLASS6\",\"ANY\",\"Enabled\",0"
            icid_first_free = 7

        icid_2nd = icid_first_free + 1
        # =============================================================

        test.log.step('Step 0.1: check Provider Config and change to VzW' + step_separator)
        # ==============================================================
        test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/Cfg", ".*OK.*"))
        res = test.dut.at1.last_response
        dummy, selected_image = res.split(',')
        selected_image = test.org_provider_config_name = selected_image[1:selected_image.find("\"", 2)].replace('*', '')

        if test.dut.project == 'VIPER':
            test.log.info('defect IPIS100335552 was set to not_to_fix for Viper, '
                          'output of the command is not correct formated')
            test.org_provider_config_name = test.org_provider_config_name.replace("\\11", "_")

        if selected_image in vzw_image_name:
            test.expect(True)
        else:
            test.log.info("VZW Image not active, try to change")
            test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/Autoselect,off", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/Cfg," + vzw_image_name, ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/Cfg", ".*OK.*"))
            res = test.dut.at1.last_response
            dummy, selected_image = res.split(',')
            # selected_image = selected_image[1:selected_image.find("\"", 2)]
            if vzw_image_name not in selected_image:
                test.expect(False)
                test.log.error("Can't set to Verizon provider Config - Test Abort")
                test.expect(False, critical=True)
            else:
                test.expect(True)
                test.log.info("VZW Image is active")

        test.log.step('Step 0.2: restart module if needed' + step_separator)
        # ==============================================================
        # SIM PIN must be active
        test.dut.at1.send_and_verify("AT+CPIN?", "OK")
        res = test.dut.at1.last_response
        if "READY" in res:
            # check if SIM PIN is active
            test.dut.dstl_lock_sim()
            test.dut.dstl_restart()
        else:
            test.log.info("SIM PIN was not entered - OK")

        test.dut.at1.send_and_verify("AT+CMEE=1", "OK")

        test.log.step('Step 0.3: delete all unused CGDCONT settings first' + step_separator)
        # ==============================================================

        # log(1, " *** delete all unused CGDCONT settings first *** ");
        # for (int k = icid_first_free; k <= icid_max; k++) {
        #     atCmd(wm1, "at+cgdcont=" + k, ".*O.*");
        # }
        for n in range(icid_first_free, icid_max+1):
            test.expect(test.dut.at1.send_and_verify("AT+CGDCONT=" + str(n), "OK"))

        test.log.step('Step 1.0: check without PIN' + step_separator)
        # ==============================================================
        test.expect(test.dut.at1.send_and_verify("AT^SGAPN?", read_response))
        test.expect(test.dut.at1.send_and_verify("AT^SGAPN", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("AT^SGAPN=?",  test_response))
        test.expect(test.dut.at1.send_and_verify("AT^SGAPN=", "CME ERROR: 21"))

        test.log.step('Step 1.1: check illegal parameters' + step_separator)
        # ==============================================================
        test.expect(test.dut.at1.send_and_verify("AT^SGAPN=17,15", "CME ERROR: 21"))
        test.expect(test.dut.at1.send_and_verify("AT^SGAPN=15,17", "CME ERROR: 21"))
        test.expect(test.dut.at1.send_and_verify("AT^SGAPN=1,1", "OK"))

        test.log.step('Step 1.2: check influence of +CGDCONT' + step_separator)
        # ==============================================================
        # test step:
        # The write command can be used to set the APN class parameters for a PDP context already
        # defined by AT+CGDCONT and identified by the context identifier <cid>.
        # If a context is newly defined by using AT+CGDCONT, then its APN class is 0,
        # the APN bearer is "ANY", it is enabled and its inactivity timer is disabled.
        test.expect(test.dut.at1.send_and_verify("AT+cgdcont=16", "OK"))
        test.expect(test.dut.at1.send_and_verify("at^sgapn=16,16,\"IP\"", "CMS ERROR: 302"))
        test.expect(test.dut.at1.send_and_verify("at+cgdcont=16,\"IP\",\"test12\"", "OK"))
        test.expect(test.dut.at1.send_and_verify("at^sgapn=16,16,\"IP\",\"test12b\",\"WCDMA\",disabled,12", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT^SGAPN?", "SGAPN: 16,16,\"IP"))
        # now delete cid 16
        test.expect(test.dut.at1.send_and_verify("at+cgdcont=16", "OK"))
        test.expect(test.dut.at1.send_and_verify("at+cgdcont?", "OK"))

        test.expect(test.dut.at1.send_and_verify("at^sgapn?", "OK"))
        res = test.dut.at1.last_response
        if "SGAPN: 16" in res:
            test.expect(False)
            test.log.error("sgapn entry was not deleted")
        else:
            test.expect(True)
            test.log.info("sgapn entry was deleted")

        # create new CID
        test.expect(test.dut.at1.send_and_verify("at+cgdcont=16,\"IPV6\",\"test12c\"", "OK"))
        test.expect(test.dut.at1.send_and_verify("at^sgapn?", "SGAPN: 16,0,\"IPV6\",\"test12c\",\"ANY\",\"Enabled\",0"))
        # atCmd(wm1, "at^sgapn?", ".*\\^SGAPN: 16,0,\"IPV6\",\"test12c\",\"ANY\",\"Enabled\",0\\s.*OK.*");

        test.log.step('Step 2.0: functional test with PIN' + step_separator)
        # ==============================================================
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify("at+cgdcont?", "CGDCONT: 16,\"IPV6\",\"test12c\",.*OK"))
        test.expect(test.dut.at1.send_and_verify("at+cgdcont?", "CGDCONT: 16,\"IPV6\",\"test12c\","))
        test.expect(test.dut.at1.send_and_verify("at^sgapn?", "SGAPN: 16,0,\"IPV6\",\"test12c\",\"ANY\",\"Enabled\",0"))

        test.dut.dstl_register_to_network()

        test.log.step('Step 2.1: check with active context' + step_separator)
        test.log.info('change should take effect after closing+reestablishing')
        # ==============================================================
        # When parameter settings are changed for an active context, it is necessary to
        # close and reestablish the connection to make the changes take effect.
        # Modules manufactured / configured for other operators are delivered with all contexts
        # undefined.
        test.expect(test.dut.at1.send_and_verify("at+cgdcont=" + str(icid_first_free) + ",\"IPV4V6\",\"ber4.ericsson\"",
                                                 "OK"))
        test.expect(test.dut.at1.send_and_verify("at^sgapn?", "SGAPN: " + str(icid_first_free)
                                                 + ",0,\"IPV4V6\",\"ber4.ericsson\",\"ANY\",\"Enabled\",0"))
        test.expect(test.dut.at1.send_and_verify("at+cgpaddr"))
        test.expect(test.dut.at1.send_and_verify("at+cgact?"))
        test.expect(test.dut.at1.send_and_verify("AT+cgdcont?"))

        test.log.step('Step 2.1b: try to activate context again to check if it is now useable' + step_separator)
        # ==============================================================
        test.expect(test.dut.at1.send_and_verify("at+cgact=0," + str(icid_first_free), "OK"))
        test.expect(test.dut.at1.send_and_verify("at+cgpaddr"))
        # missing error is displayed in public network
        test.expect(test.dut.at1.send_and_verify("at+cgact=1," + str(icid_first_free), 'OK|missing or unknown APN'))
        test.expect(test.dut.at1.send_and_verify("AT+cgdcont?"))
        test.sleep(15)

        test.log.step('Step 2.2: set context completly new to check if it is now useable' + step_separator)
        # ==============================================================
        test.expect(test.dut.at1.send_and_verify("at+cgact=0," + str(icid_first_free), "OK"))
        test.expect(test.dut.at1.send_and_verify("at+cgatt=0"))
        test.sleep(30)
        test.expect(test.dut.at1.send_and_verify("at+cgact?"))
        test.expect(test.dut.at1.send_and_verify("at+cgdcont=" + str(icid_first_free)))
        test.expect(test.dut.at1.send_and_verify("at+cgdcont?"))
        test.expect(test.dut.at1.send_and_verify("at+cgact?"))
        test.expect(test.dut.at1.send_and_verify("at+cgdcont=" + str(icid_first_free)
                                                 + ",\"IPV4V6\",\"ber7.ericsson\""))
        # // now SGAPN is performed before activating the context:
        test.expect(test.dut.at1.send_and_verify("at^SGAPN=" + str(icid_first_free) + "," + str(icid_first_free)
                                                 + ",\"IPV4V6\",\"ber7.ericsson\",\"ANY\",\"Enabled\",180"))
        test.expect(test.dut.at1.send_and_verify("at+cgpaddr"))
        test.expect(test.dut.at1.send_and_verify("at+cgact?"))
        test.expect(test.dut.at1.send_and_verify("AT+cgdcont?", "OK"))
        # // activate now with SGAPN setting - is it working ?
        test.expect(test.dut.at1.send_and_verify("at+cgact=1," + str(icid_first_free), "OK|missing or unknown APN"))
        test.expect(test.dut.at1.send_and_verify("at+cgpaddr"))
        test.sleep(15)

        test.expect(test.dut.at1.send_and_verify("at^SGAPN?"))
        test.expect(test.dut.at1.send_and_verify("at+cgdcont?"))
        test.expect(test.dut.at1.send_and_verify("at+cgpaddr"))

        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify("at+cgdcont=" + str(icid_first_free)
                                                 + ",\"IPV4V6\",\"ber8.ericsson\""))
        test.expect(test.dut.at1.send_and_verify("at^SGAPN?"))
        test.expect(test.dut.at1.send_and_verify("at+CGDCONT?"))

        test.log.step('Step 2.3: take a different context to check if it is now useable' + step_separator)
        # ==============================================================
        test.expect(test.dut.at1.send_and_verify("at+cgact=0," + str(icid_2nd), "O"))
        test.expect(test.dut.at1.send_and_verify("at+cgatt=0"))
        test.expect(test.dut.at1.send_and_verify("at+cgdcont=" + str(icid_2nd)))
        test.expect(test.dut.at1.send_and_verify("at+cgdcont?"))
        test.expect(test.dut.at1.send_and_verify("at+cgact?"))
        test.expect(test.dut.at1.send_and_verify("at+cgdcont=" + str(icid_2nd) + ",\"IPV4V6\",\"ber7.ericsson\""))
        # // now SGAPN is performed before activating the context:
        test.expect(test.dut.at1.send_and_verify("at^SGAPN=" + str(icid_2nd) + "," + str(icid_2nd)
                                                 + ",\"IPV4V6\",\"ber7.ericsson\",\"ANY\",\"Enabled\",180"))
        test.expect(test.dut.at1.send_and_verify("at+cgpaddr"))
        test.expect(test.dut.at1.send_and_verify("at+cgdcont?"))
        test.expect(test.dut.at1.send_and_verify("at+cgact?"))

        test.expect(test.dut.at1.send_and_verify("at+cgact=1," + str(icid_2nd),
                                                 "OK|missing or unknown APN", timeout=25))
        test.expect(test.dut.at1.send_and_verify("AT+cgdcont?", "OK"))
        test.expect(test.dut.at1.send_and_verify("at+cgpaddr"))

        test.expect(test.dut.at1.send_and_verify("at^SGAPN?"))
        test.expect(test.dut.at1.send_and_verify("at+cgdcont?"))
        test.expect(test.dut.at1.send_and_verify("at+cgpaddr"))

        test.expect(test.dut.at1.send_and_verify("at+cgdcont=" + str(icid_2nd) + ",\"IPV4V6\",\"ber7.ericsson\""))
        test.expect(test.dut.at1.send_and_verify("at^SGAPN?"))
        test.expect(test.dut.at1.send_and_verify("at+CGDCONT?"))
        pass

    def cleanup(test):
        """Cleanup method.
        Steps to be executed after test run steps.
        """
        # ==============================================================
        test.log.com('**** log  dir: ' + test.workspace + ' ****')
        test.expect(test.dut.at1.send_and_verify("at+cgatt=0"))
        test.delete_cgdcont()
        test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/Cfg,"
                                                 + test.org_provider_config_name, ".*OK.*"))

        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')
        pass


if __name__ == "__main__":
    unicorn.main()
