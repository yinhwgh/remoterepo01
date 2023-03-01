#responsible: christian.gosslar@thalesgroup.com
#location: Berlin
#LM0003577.001 - TC0094445.001
testcase_id = "LM0003577.001 - TC0094445.001"

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

class at_clac_basic(BaseTest):

    def setup(test):

        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.log.com("***** " + testcase_id + " *****")
        test.log.com('***** Collect some Module Infos *****')
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.dut.dstl_get_bootloader()
        test.dut.dstl_check_c_revision_number()
        test.dut.dstl_collect_module_info()
        test.dut.dstl_check_or_read_part_number(only_read=True)
        test.dut.devboard.send_and_verify("mc:asc0cfg=off",".*O.*")
        pass

    def run(test):
        if (test.dut.project == 'VIPER'):
            #at_list = ".*AT[&]C.*AT[&]D.*AT[&]F.*ATA.*AT[\]Q.*AT[+]CACM.*"
            at_list = "AT[&]C.*AT[&]D.*AT[&]F.*AT[&]S.*AT[&]V.*AT[&]W.*ATA.*AT[\]Q.*AT[+]CACM.*AT[+]CAMM.*AT[+]CAOC.*" \
                      "AT[+]CPUC.*AT[+]CAVIMS.*AT[+]CCFC.*AT[+]CCHC.*AT[+]CCHO.*AT[+]CCLK.*AT[+]CCWA.*AT[+]CEER.*" \
                      "AT[+]CEMODE.*AT[+]CEREG.*AT[+]CESQ.*AT[+]CFUN.*AT[+]CGACT.*AT[+]CGATT.*AT[+]CGCONTRDP.*" \
                      "AT[+]CGDATA.*AT[+]CGDCONT.*AT[+]CGDSCONT.*AT[+]CGEQOSRDP.*AT[+]CGEQOS.*AT[+]CGEREP.*AT[+]CGMI.*" \
                      "AT[+]CGMM.*AT[+]CGMR.*AT[+]CGLA.*AT[+]CGPADDR.*AT[+]CGPIAF.*AT[+]CGREG.*AT[+]CGSCONTRDP.*" \
                      "AT[+]CGSMS.*AT[+]CGSN.*AT[+]CGTFTRDP.*AT[+]CGTFT.*AT[+]CHLD.*AT[+]CHUP.*AT[+]CIMI.*AT[+]CLCC.*" \
                      "AT[+]CLCK.*AT[+]CLIP.*AT[+]CLIR.*AT[+]CMEE.*AT[\^]SPOW.*AT[+]CMGD.*AT[+]CMGF.*AT[+]CMGL.*" \
                      "AT[+]CMGR.*AT[+]CMGS.*AT[+]CMGC.*AT[+]CMMS.*AT[+]CMGW.*AT[+]CMSS.*AT[+]CMUT.*AT[+]CNMA.*" \
                      "AT[+]CNMI.*AT[+]CNMPSD.*AT[+]CNUM.*AT[+]COLP.*AT[+]COPN.*AT[+]COPS.*AT[+]CPBR.*AT[+]CPBS.*" \
                      "AT[+]CPBW.*AT[+]CPIN.*AT[+]CPLS.*AT[+]CPOL.*AT[+]CPMS.*AT[+]CPWD.*AT[+]CREG.*AT[+]CRSM.*" \
                      "AT[+]CRC.*AT[+]CSCA.*AT[+]CSCB.*AT[+]CSCS.*AT[+]CSDH.*AT[+]CSIM.*AT[+]CSMP.*AT[+]CSMS.*" \
                      "AT[+]CSQ.*AT[+]CSSN.*AT[+]CSVM.*AT[+]CTZU.*AT[+]CTZR.*AT[+]CUSD.*AT[+]CCUG.*AT[+]CVMOD.*" \
                      "ATD[*]99.*ATDT[*]99.*ATD>.*ATD.*ATH.*ATE.*AT[+]GCAP.*AT[+]GMI.*AT[+]GMM.*AT[+]GMR.*AT[+]GSN.*" \
                      "AT[+]IPR.*AT[+]ICF.*ATI.*ATO.*ATQ.*ATS0.*ATS3.*ATS4.*ATS5.*AT[\^]SAD.*AT[\^]SAIC.*AT[\^]SBLK.*" \
                      "AT[\^]SBV.*AT[\^]SCFG.*AT[\^]SCID.*AT[+]CCID.*AT[\^]SCKS.*AT[\^]SCML.*AT[\^]SCMR.*AT[\^]SCMS.*" \
                      "AT[\^]SCMW.*AT[\^]SCPIN.*" \
                      "AT[\^]SFDL.*AT[\^]SGPSE.*AT[\^]SICS.*AT[\^]SISE.*AT[\^]SISS.*AT[\^]SLCC.*" \
                      "AT[\^]SNFI.*AT[\^]SSDA.*AT[+]VTS.*OK"

        resp_test_without_pin = ".*[+]CME ERROR: unknown.*"
        resp_test_with_pin = ".*[+]CME ERROR: unknown.*"
        resp_exec_without_pin = at_list
        resp_exec_with_pin  = at_list

        test.log.step('Step 1.0: check test and exec command without PIN')
        # ==============================================================
        test.dut.at1.send_and_verify("at+CPIN?",".*O.*")
        if ("READY" in test.dut.at1.last_response):
            # restart the module
            test.expect(test.dut.dstl_restart())

        test.expect(test.dut.at1.send_and_verify("AT+clac=?", resp_test_without_pin))
        test.expect(test.dut.at1.send_and_verify("AT+clac", resp_exec_without_pin ))

        test.log.step('Step 2.0: check test and exec command with PIN')
        # ==============================================================
        test.expect(test.dut.dstl_register_to_network())

        test.expect(test.dut.at1.send_and_verify("AT+clac=?", resp_test_with_pin ))
        test.log.info('Run the command more then one times, because the response is differnt')
        test.log.info("See IPIS100325908 Run at+clac serval times,the return value changes")
        test.expect(test.dut.at1.send_and_verify("AT+clac", resp_exec_with_pin ))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("AT+clac", resp_exec_with_pin ))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("AT+clac", resp_exec_with_pin ))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("AT+clac", resp_exec_with_pin ))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("AT+clac", resp_exec_with_pin ))
        test.sleep(5)
        pass

    def cleanup(test):
        """Cleanup method.
        Steps to be executed after test run steps.
        """
        # ==============================================================
        test.log.com('**** log  dir: ' + test.workspace + ' ****')
        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')
        pass

if (__name__ == "__main__"):
    unicorn.main()
