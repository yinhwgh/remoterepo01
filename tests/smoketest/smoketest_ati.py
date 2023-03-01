# author: christian.gosslar@thalesgroup.com
# responsible: christian.gosslar@thalesgroup.com
# location: Berlin
# TC0095597.001
# jira: xxx
# feature: LM0002316.001 LM0002433.001 LM0002483.001 LM0002550.001 LM0003240.001 LM0002433.002 LM0004202.001
# LM0003809.002 LM0003809.003 LM0003809.005 LM0003240.002 LM0005733.001 LM0004202.002 LM0003240.003 LM0003240.004
# LM0002550.002 LM0003240.008 LM0007702.001

import unicorn
from dstl.network_service.register_to_network import  dstl_enter_pin
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.collect_module_infos import dstl_collect_module_info
from dstl.identification.get_part_number import dstl_check_or_read_part_number
from dstl.identification.get_revision_number import dstl_get_revision_number
from dstl.identification.get_hwid import dstl_get_hwid
from dstl.identification.get_imei import dstl_get_imei
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.check_c_revision_number import dstl_check_c_revision_number
from dstl.identification.get_identification import dstl_get_defined_ati_parameters
from dstl.auxiliary.devboard import devboard

import re

class Test(BaseTest):


    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.log.com('***** Collect some Module Infos *****')
        test.dut.dstl_detect()
        test.dut.dstl_switch_off_at_echo(serial_ifc=0)
        test.expect(test.dut.dstl_get_hwid())
        test.dut.dstl_get_imei()
        test.dut.dstl_get_bootloader()
        test.dut.dstl_check_c_revision_number()
        test.dut.dstl_collect_module_info()
        test.dut.dstl_check_or_read_part_number(only_read=True)
        test.dut.dstl_collect_module_info_for_mail()

    def run(test):
        """
        Intention:
        Simple check of the ati command with all parameters
        """
        test.log.step('Step 1: check HW ID of the Module - Start')
        test.expect(test.dut.dstl_get_hwid())

        test.log.step('Step 2: check the function, when PIN was not entered - Start')

        test.log.step('Step 3a: If PIN was entered reset the SIM-PIN via cfun=0/1 change')
        test.dut.at1.send_and_verify("at+cpin?", "OK")
        res = test.dut.at1.last_response
        if "READY" in res:
            test.log.step('Step 3b: PIN was enter, set Module to Airplane mode and switch back')
            test.dut.at1.send_and_verify("at+cfun=0", "OK")
            test.sleep(5)
            test.dut.at1.send_and_verify("at+cfun=1", "OK")
            test.sleep(5)
            test.dut.at1.send_and_verify("at+cpin?", "OK")
            res = test.dut.at1.last_response
            if "READY" in res:
                test.log.step("Step 3c: After switch to Airplanemode and back, PIN is still disabled")
                test.dut.at1.send_and_verify('at+clck="SC",2', "OK")
                if 'CLCK: 0' in test.dut.at1.last_response:
                    test.log.info('Correct, SIM PIN is disabled')
                    test.expect(True)
                else:
                    test.log.info('DIF SIM PIN will not be lost after cfun=0/1')
                    test.expect(False)
            else:
                test.log.step("Step 3c: After switch to Airplanemode and back, SIM PIN is active")
                test.log.com('Test can start')
        test.dut.at1.send_and_verify("at+cmee=2", "OK")

        test.log.step("Step 4: first check the standard ati response")
        test.dut.at1.send_and_verify("ati", "O")
        res = test.dut.at1.last_response

        resp_aticheck = test.dut.dstl_get_revision_number()
        if re.search(resp_aticheck, res, re.DOTALL):
            logtext = "Step 4: check ati response is correct!"
        elif re.search(resp_aticheck, "noatiresponse"):
            logtext = 'There is no ATI response define for this Project ' + test.dut.project
        else:
            test.log.error("Step 4: check ati response has an error!")
            logtext = '"Step 4: check ati response has a general error, returned with: {}"'.format(resp_aticheck)
            test.expect(False)

        test.log.info(logtext)

        test.log.step("Step 5: Check the defined ati<value>, Do not check the response value")
        test.log.info("        Definition comes from dstl_get_defined_ati_parameterse")
        test.log.info("        Special handling for ati2, because these command need the SIM-PIN")

        atiliste = test.dut.dstl_get_defined_ati_parameters()
        if "undefined" in atiliste:
            test.log.info("Please check in dstl_get_defined_ati_parameters the list of ATI- Values")
            test.expect(False)
        else:
            for ati_param in atiliste:
                # check only, if the ATI command return OK
                if ati_param != 2: # ati2 shall show the UICC Version, which need the SIM-PIN, therefore extra handling
                    test.log.info("ATI-Value: " + str(ati_param))
                    test.expect(test.dut.at1.send_and_verify("ati" + str(ati_param), "OK"))
                else:
                    test.log.info("ATI-Value: " + str(ati_param))
                    test.expect(test.dut.at1.send_and_verify("ati" + str(ati_param), "ERROR"))

        test.log.step("Step 6: Enter SIM PIN")
        test.expect(test.dut.dstl_enter_pin())

        test.log.step("Step 7: Check some invalid values")
        # Check ATI with invalid parameter, SIM is entered
        ati_invalid_params = "=?,?,=0,9876,-1,=-1"
        ati_invalid_params_list = ati_invalid_params.split(',')
        for ati_param in ati_invalid_params_list:
            # check only, if the ati command return OK
            test.log.info("ATI-Value: " + ati_param)
            test.expect(test.dut.at1.send_and_verify("ati" + ati_param, "ERROR"))

        test.log.step("Step 8: Check the defined ati<value> after PIN, Do not check the response value")
        test.log.info("        Definition comes from dstl_get_defined_ati_parameters")

        atiliste = test.dut.dstl_get_defined_ati_parameters()
        if "undefined" in atiliste:
            test.log.info("Please check in dstl_get_defined_ati_parameters the list of ATI- Values")
            test.expect(False)
        else:
            for ati_param in atiliste:
                # check only, if the ati command return OK
                test.log.info("ATI-Value: " + str(ati_param))
                test.expect(test.dut.at1.send_and_verify("ati" + str(ati_param), "OK"))

        test.log.step("Step 9: Check the part Number")
        test.expect(test.dut.dstl_check_or_read_part_number(only_read=False))



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
