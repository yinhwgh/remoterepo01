#responsible: christian.gosslar@thalesgroup.com
#location: Berlin
#LM0004975.001 - LM0004985.001 - LM0004985.002 - LM0004985.003 - LM0006590.001 - LM0004975.004 -
#TC0094443.001
testcase_id = "LM0004975.001 - LM0004985.001 - LM0004985.002 - LM0004985.003 - LM0006590.001 - " \
              "LM0004975.004 - TC0094443.001"

import unicorn
import os
from pathlib import Path
from dstl.auxiliary import init
from core.basetest import BaseTest
from dstl.security.lock_unlock_sim import *
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_enter_pin
import platform
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.identification.collect_module_infos import dstl_collect_module_info
from dstl.identification.get_revision_number import dstl_get_revision_number
from dstl.identification.get_imei import dstl_get_imei
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.check_c_revision_number import dstl_check_c_revision_number
from dstl.identification.get_part_number import dstl_check_or_read_part_number
from dstl.identification import get_imei
from datetime import date
from datetime import time
from datetime import datetime

default_provider_name =""
ver = "1.0"
home = True
autoselect_setting = ""

class at_scfg_provider_check_all_uicc_ids(BaseTest):

    def write_new_iccid(test, new_iccid):
        if test.expect(test.dut.at1.send_and_verify("AT+CRSM=176,12258,0,0,10", "OK")) == False:
            test.log.error("WriteNewIccid() failed - new ICCID was not written to SIM.")
        # fill up the iccid string up to 18 characters
        while len(new_iccid)< 18:
            new_iccid += "0"

        check_sum = test.check_luhn(new_iccid)
        test.log.info ("Luhn checksum: >" + str(check_sum) + "<")
        new_iccid = new_iccid + str(check_sum)
        # add filler 'F's up to max. length of 20:
        while len(new_iccid)< 20:
            new_iccid += "F"

        transformed_iccid = ""
        iCharCount=0
        k=0
        loops_rest = (len(new_iccid))%2
        while k< (int((len(new_iccid))/2)):
            transformed_iccid = transformed_iccid + new_iccid[(iCharCount+1): (iCharCount+2)]
            transformed_iccid = transformed_iccid + new_iccid[(iCharCount + 0): (iCharCount + 1)]
            iCharCount = iCharCount +2
            k = k +1

        if loops_rest >0:
            transformed_iccid = transformed_iccid + new_iccid[(iCharCount): (iCharCount + 1)]
            iCharCount = iCharCount + 1

        test.log.info( "Write iccid: >" + str(transformed_iccid) + "<")
        test.expect(test.dut.at1.send_and_verify("AT+CRSM=214,12258,0,0,10,\"" + str(transformed_iccid) + "\"", "OK"))
        return

    '''
	Luhn Check and CheckSumGenerator (used for IMEIs, ICCIDs, CreditCard numbers, and so on)
	original code source: https://de.wikipedia.org/wiki/Luhn-Algorithmus
	Check:	true/false: CheckSum is valid or not for given number (i.E. full IMEI)
	Sum:		calculate a checksum for the given number and return it (i.E. return last digit of an IMEI without checksum)
	Start from left and not from right, don't know why
	'''
    def check_luhn(test, number):
        sum = 0
        parity = len(number) % 2
        for i, digit in enumerate(int(x) for x in number):
            if i % 2 != parity:
                digit *= 2
                if digit > 9:
                    digit -= 9
            sum += digit
        res = 10 - (sum % 10)
        if res == 10:
            res=0
        return res

    def sim_retrigger(test):
        '''retrigger SIM read -> cfun=0 wait cfun=1'''
        # if (test.dut.project == 'VIPER'):
        #     # test.expect(test.dut.dstl_restart())
        #     # test.expect(test.dut.at1.send_and_verify("at^sind=prov,1"))
        #     test.expect(test.dut.at1.send_and_verify("at+cfun=0", "OK"))
        #     test.sleep(5)
        #     test.expect(test.dut.at1.send_and_verify("at+cfun=1", "OK"))
        # else:
        test.expect(test.dut.at1.send_and_verify("at+cfun=0", "OK"))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("at+cfun=1", "OK"))
        return


    def setup(test):

        test.log.com ('***** Testcase: ' + test.test_file + '*****')
        test.log.com ('***** Ver: ' + str(ver) + ' - Start *****')
        test.log.com ("***** " + testcase_id + " *****")
        test.log.com ('***** Collect some Module Infos *****')
        test.dut.dstl_detect()
        if not home:
            test.dut.dstl_get_imei()
            test.dut.dstl_get_bootloader()
            test.dut.dstl_check_c_revision_number()
            test.dut.dstl_collect_module_info()
            test.dut.dstl_check_or_read_part_number(only_read=True)
        # if this command is used with McTest4 the serial interface is dead
        # test.dut.devboard.send_and_verify("mc:asc0cfg=off",".*O.*")

    def run(test):

        provider_list_from_file = []
        provider_listarray =[]
        fallback_prov_name = ""
        test.log.step('Step 0.1: preparation')
        stepline = '\n=============================================================='

        sImsiOfSpecialSIM = "001011876543210"
        if (test.dut.project == 'BOBCAT' and test.dut.step == "2"):
            if (dstl.test.dut.product == "PLPS9"):
                product_variant = dstl.test.dut.product + "-" + dstl.test.dut.variant + "-230"
            else:
                test.dut.at1.send_and_verify("at^sinfo=ProductCfg/Ident")
                if ("210" in test.dut.at1.last_response):
                    product_variant = dstl.test.dut.product + "-" + dstl.test.dut.variant + "-210"
                else:
                    # eventuell muss hier für alte Bobcat die SW Versionunterschieden werden (200/220)
                    # not done yet
                    product_variant = dstl.test.dut.product + "-" + dstl.test.dut.variant + "-220"
        else:
            product_variant = dstl.test.dut.product + "-" + dstl.test.dut.variant
        fallback_prov_name=""
        first_provfile_line =""

        if (test.dut.project == 'VIPER'):
            scfg_special_response = True
            fallback_prov_name = "ROW_Generic_3GPP"

        test.log.step('Step 0.2: - check preconditions like SIM, reference file name' + stepline)
        # ==============================================================
        current_dir = os.path.dirname(__file__)
        testfile_path = re.sub( "tests.*" , "tests", current_dir)
        testfile_path = re.sub("/", "\\\\", testfile_path)
        testfile_path = os.path.join(testfile_path, "test_files" , "uiccd")
        testfile_name = test.dut.project.lower() + "_" + test.dut.step + "_prov_cfg.log"
        full_testfile_name = os.path.join(testfile_path, testfile_name )
        # create result filename
        full_testfile_name_result = str(datetime.today())
        full_testfile_name_result = re.sub("\..*","", full_testfile_name_result)
        mydate = full_testfile_name_result
        full_testfile_name_result = full_testfile_name_result.replace("-", "")
        full_testfile_name_result = full_testfile_name_result.replace(":", "")
        full_testfile_name_result = full_testfile_name_result.replace(' ','_')
        full_testfile_name_result = full_testfile_name_result + "_" + test.dut.project.lower() +\
                                    "_" + test.dut.step + "_prov_cfg-result.log"

        full_testfile_name_result = os.path.join(test.workspace, full_testfile_name_result)

        fname = Path(full_testfile_name)
        if fname.exists():
            test.expect(True)
            test.log.info("Provider config file found")
            test.log.info("Searchpath is: >" + full_testfile_name + "<")
            test.expect(True)
        else:
            test.expect(False)
            test.log.error("Provider config file not found")
            test.log.error("Searchpath is: >" + full_testfile_name + "<")
            test.log.error("test abort")
            test.expect(False, critical=True)

        test.dut.dstl_enter_pin()
        test.expect(test.dut.at1.send_and_verify("at+CIMI"))

        if (not sImsiOfSpecialSIM in test.dut.at1.last_response) and (not home):
            test.log.error("special SIM is needed with IMSI " +  sImsiOfSpecialSIM)
            test.log.error("test abort")
            test.expect (False, critical=True)
        else:
            test.expect(True)
            test.log.info("special SIM is used - OK")

        test.log.step('Step 0.3: - read the providerconfig build logfile' + stepline)
        # ==============================================================
        # current version must be copy from build path, no access to build results

        # read provider config log file
        test.log.info ("read Provider from File " + str(full_testfile_name))
        fname = open(full_testfile_name)
        n=0
        for line in fname:
            line.rstrip()
            if (not "MODULE" in line) and (not "ProvCfg" in line):
                # remove spaces
                line = re.sub("\s\s+", " ", line)
                line = re.sub("\n$", "", line)
                line = re.sub("\t", " ", line)
                line = re.sub("\*", "", line)
                [module_name, provider_name, mcfg_version, iccid] = line.split(' ')
                provider_list_from_file = [module_name, provider_name, mcfg_version, iccid]
                provider_listarray.append(provider_list_from_file)
                n +=1
            else:
                # read the first line for version info
                if first_provfile_line == "":
                    first_provfile_line = line
        fname.close()

        fname_log = open(full_testfile_name_result, "w")
        fname_log.write("UICCD Test from " + str(mydate) + "\n")
        fname_log.write(str(product_variant) + " SW Version: " + str(dstl.test.dut.software_number) )

        test.dut.at1.send_and_verify("ati281")
        partnumber = test.dut.at1.last_response
        if "ERROR" not in partnumber:
            partnumber = partnumber[partnumber.index("S"):]
            partnumber = partnumber[:partnumber.index("\r")]
        else:
            partnumber = "not defined"
        test.dut.at1.send_and_verify("at+gsn")
        imei = dstl_get_imei(test.dut)
        fname_log.write(" PN: " +str(partnumber) + " IMEI: " + str(imei) + "\n")
        fname_log.close()

        test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/AutoSelect", ".*OK.*")
        autoselect_setting = test.dut.at1.last_response

        ### search fallback provider and check version of provider configs
        test.expect(test.dut.at1.send_and_verify("ati61"))
        res = test.dut.at1.last_response
        ati_list  = res.split('\r\n')

        test.log.step('Step 0.4: - read the providerconfig build logfile' + stepline)
        # ========================================================
        test.log.info ("the following Provider found in ati61 response\n==============================================")
        i=1
        for n in ati_list:
            #test.log.info("Prov-name A " + str(i) + ": >" +str(n) + "<")
            if (" " in n) and (not "MIMG" in n) and (not "OK" in n):
                [prov_name, prov_ver] = n.split(' ')
                test.log.info("Prov-name B " + str(i) + ": >" + str(prov_name) + "< >" + str(prov_ver) + "<")
            i += 1
        test.log.info ("the following Provider found in fillist\n==============================================")
        i=1
        for i in range(0, len(provider_listarray)):
            if (provider_listarray[i][0] in product_variant):
                test.log.info("Prov-name " + str(i) + ": >" +str(provider_listarray[i][1]) + "<")
                i += 1
        # ========================================================

        test.log.step ("Step 1.0: Check if all provider from module have same version coming from File. \n"
                       "And check if all Provider form module are in the the filelist" + stepline)
        # =====================================================
        for n in ati_list:
            check = "not found"
            if (" " in n) and (not "MIMG" in n):
                check = "line found"
                [prov_name, prov_ver] = n.split(' ')
                if ( "*" in n) and (test.dut.project != 'VIPER'):
                    fallback_prov_name = prov_name.replace("*","")
                for i in range(0, len(provider_listarray)):
                    if (provider_listarray[i][0] in product_variant) and (provider_listarray[i][1].lower() in prov_name.lower()):
                        # test.log.info ("Check provider: " + str(provider_listarray[i][1]))
                        check = "OK"
                        if provider_listarray[i][2] in prov_ver:
                            test.log.info ("Found provider and Version check is ok, version is: >" + str(prov_ver) + "< ")
                            test.expect (True)
                        else:
                            test.expect(False)
                            test.log.error ("Found provider but Versions are differnt:")
                            test.log.error ("Version from Module: " + str(prov_ver))
                            test.log.error ("Version from file:   " + str(provider_listarray[i][2]))
                        break
                # end for loop
            if "line found" in check:
                test.log.error ("Provider >" + str(prov_name) + "< from ati61 not found in Filelist from file")
                test.expect (False)


        test.log.step ("Step 2.0: Check if all provider from filelist are in ati61 included" + stepline)
        # =====================================================
        for i in range(0, len(provider_listarray)):
            if (provider_listarray[i][0] in product_variant):
                test.log.info ("Search provider: >" + str(provider_listarray[i][1].lower() + "<"))
                for n in ati_list:
                    check = "not found"
                    if (" " in n) and (not "MIMG" in n) and (not "OK" in n):
                        check = "line found"
                        [prov_name, prov_ver] = n.split(' ')
                        if ("*" in prov_name):
                            prov_name = prov_name.replace("*", "")
                    # test.log.info(">" + str(prov_name) + " " + str(provider_listarray[i][1].lower()) + "<")
                    if (prov_name.lower() == provider_listarray[i][1].lower()):
                        test.log.info ("Found")
                        check = "OK"
                        break
                # ende for
                if (check == "OK"):
                    test.log.info ("prov from file:   " + str(provider_listarray[i][1]))
                    test.log.info ("prov from module: " + str(prov_name))
                    test.expect (True)
                else:
                    #test.log.info ("Provider >" + str(provider_listarray[i][1]) + "< not found in the Module")
                    test.log.error ("Provider >" + str(provider_listarray[i][1]) + "< not found in the Module")
                    test.expect (False)

        ##
        test.log.step ("Step 3.0: Set for all entries in the prov file the iccd and check "
                       "if the module select the correct provider" + stepline)
        # =====================================================
        test.expect(test.dut.at1.send_and_verify("at^sind=prov,1"))
        if (test.dut.project != 'VIPER'):
            test.expect(test.dut.at1.send_and_verify("at^sind=imsi,1"))
        test.expect(test.dut.at1.send_and_verify("at^sind=iccid,1"))
        test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/AutoSelect,\"on\"", ".*OK.*"))
        test.sim_retrigger()

        test.log.info("Search for Provider entries for Product Variant " + str(product_variant))
        for i in range (0, len(provider_listarray)):
            if provider_listarray[i][0] in product_variant:
                provider_list_values = provider_listarray[i][3].split(",")
                test.log.info("Found Provider entry " + str(provider_listarray[i][1]))
                test.log.info ("Check the following iccid values: " + str(provider_list_values))
                for prov_uicc in provider_list_values:
                    # can run from 1 to x
                    test.log.info ("#######################################")
                    if prov_uicc != "":
                        test.log.info("Check for Provider: " + str(provider_listarray[i][1]) +
                                      " the UUICD: >"+ str(prov_uicc) + "<")
                        test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/AutoSelect,\"on\"", ".*OK.*"))
                        test.sleep(5)
                        test.log.info ("Write now new ICCID: >" + str(prov_uicc) + "< into SIM ")
                        test.log.info  ("Provider: " + str(provider_listarray[i][1]) + " the UUICD: "+ str(prov_uicc))
                        fname_log = open(full_testfile_name_result, "a")
                        fname_log.write("Provider: " + str(provider_listarray[i][1]) + " and the UUICD: "+ str(prov_uicc) )
                        test.write_new_iccid(str(prov_uicc))
                        test.sim_retrigger()
                        test.dut.at1.wait_for("CIEV: prov,0",timeout=30)
                        # dummy = test.dut.at1.last_response
                        if ( (str(str(provider_listarray[i][1]).lower()) in test.dut.at1.last_response or
                              (str(str(provider_listarray[i][1])) in test.dut.at1.last_response))):
                            fname_log.write(" - passed\n")
                            test.expect(True)
                        else:
                            fname_log.write(" - failed\n")
                            test.expect(False)
                        fname_log.close()
                        # bobcat change the setting after reset
                        test.log.info ("search for provider name >" + str(provider_listarray[i][1]) )
                        test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/cfg"))
                        test.expect(test.dut.at1.send_and_verify("at+cpin?"))
                        test.sleep(5)
                        # switch back to fallback provider
                        test.log.info ("switch back to fallback provider")
                        test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/AutoSelect,\"off\"", ".*OK.*"))
                        test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/cfg,\"" + str(fallback_prov_name) + "\"", ".*OK.*"))
                        test.sim_retrigger()
                        test.sleep(5)
                    else:
                        test.log.info ("Check for Provider: " + str(provider_listarray[i][1]) +
                                      " the UUICD: >"+ str(prov_uicc) + "< skipped, uicc is empty")
        # end for loop

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
            restart_flag = True

        if restart_flag:
            test.expect(test.dut.dstl_restart())

        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')
        pass

if (__name__ == "__main__"):
    unicorn.main()
