#responsible: renata.bryla@globallogic.com
#location: Wroclaw
#TC0091832.001

import re
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.security.lock_unlock_sim import dstl_lock_sim


class Test(BaseTest):
    """
    This procedure provides the possibility of basic tests for the test, read and write command of +CNMI.

    1. check command without and with PIN
    1.1. scenario without PIN authentication: test, read and write commands should be PIN protected
    1.2. scenario with PIN authentication
    - disable Phase 2+ (if supported) and check CNMI test command
    - enable Phase 2+ (if supported) compatible SMS command syntax and check CNMI test command
    - check read command default settings (after AT&F) - actual settings: default value
    - set only first parameter of CNMI - mode=1
    - read actual settings: mode=1
    - set the first two parameters of CNMI - mode=1 and mt=1
    - read actual settings: mode=1, mt=1
    - set the first three parameters of CNMI - mode=1, mt=1 and bm=0
    - read actual settings: mode=1, mt=1, bm=0
    - set the first four parameters of CNMI - mode=1, mt=1, bm=0 and ds=0
    - read actual settings: mode=1, mt=1, bm=0, ds=0
    - set all parameters of CNMI - mode=1, mt=1, bm=0, ds=0 and bfr=1
    - read actual settings: mode=1, mt=1, bm=0, ds=0, bfr=1
    2. check all parameters and also with invalid values
    - check EXEC command
    - check test command invalid value
    - check read command invalid value
    - try to set not supported value for parameters:
    e.g. mode/mt: -1,4, bm/ds: -1,3, bfr: -1,5, and for mix parameters
    - try to set empty write command (result according to ATC)
    - try to set write command with more than 1 parameter

    A functional check is not done here:
    - functionality in combination with +CNMI which has an influence to +CSMS is checking in TC: Csms
    - functionality by sending and receiving SMS for different settings of +CNMI,
    then check if indication  CMTI / CMT appears or should not will be checking in TCs: CnmiAllText and CnmiAllPDU
    """

    TIMEOUT = 30
    CMS_ERROR_SIM_PIN = r"\+CMS ERROR: SIM PIN required"
    CMS_ERROR = r"\+CMS ERROR:.*"
    OK = r".*OK.*"

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", test.OK))
        if re.search(r".*SIM PIN.*", test.dut.at1.last_response):
            test.expect(True, msg="SIM PIN code locked - checking if command is PIN protected could be realized")
        else:
            test.log.info("SIM PIN entered - restart is needed")
            test.expect(dstl_restart(test.dut))
            test.expect(test.dut.at1.send_and_verify("AT+CPIN?", test.OK))
            if re.search(r".*SIM PIN.*", test.dut.at1.last_response):
                test.expect(True, msg="SIM PIN code locked - checking if command is PIN protected could be realized")
            else:
                test.expect(True, msg="SIM PIN code unlocked - must be locked for checking if command is PIN protected")
                test.expect(dstl_lock_sim(test.dut))
                test.expect(dstl_restart(test.dut))
                test.expect(test.dut.at1.send_and_verify('AT+CPIN?', '.*SIM PIN.*OK.*'))
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", test.OK))
        test.sleep(10)

    def run(test):
        test.log.step('Step 1. check command without and with PIN')
        test.log.step('Step 1.1. scenario without PIN authentication '
                      '- test, read and write commands should be PIN protected')
        test.expect(test.dut.at1.send_and_verify('AT+CNMI=?', test.CMS_ERROR_SIM_PIN))
        test.expect(test.dut.at1.send_and_verify('AT+CNMI?', test.CMS_ERROR_SIM_PIN))
        test.expect(test.dut.at1.send_and_verify('AT+CNMI=1,1', test.CMS_ERROR_SIM_PIN))

        test.log.step('Step 1.2. scenario with PIN authentication')
        project = test.dut.project.upper()
        if project == "BOBCAT" or project == "VIPER":
            test_regex_csms_0 = r'.*\+CNMI: \(0,1,2\),\(0,1\),\(0,2\),\(0\),\(1\)\s*OK.*'
            test_regex_csms_1 = r'.*\+CNMI: \(0,1,2\),\(0,1,2,3\),\(0,2\),\(0,1\),\(1\)\s*OK.*'
        else:
            test_regex_csms_0 = r'.*\+CNMI: \(0,1,2\),\(0,1\),\(0\),\(0\),\(1\)\s*OK.*'
            test_regex_csms_1 = r'.*\+CNMI: \(0,1,2\),\(0,1,2,3\),\(0\),\(0,1\),\(1\)\s*OK.*'
        test.expect(dstl_enter_pin(test.dut))
        test.sleep(10)  # waiting for module to get ready
        test.expect(test.dut.at1.send_and_verify('AT+CREG=2', test.OK))

        test.log.step('- disable Phase 2+ (if supported) and check CNMI test command')
        test.expect(test.dut.at1.send_and_verify('AT+CSMS=0', test.OK))
        test.expect(test.dut.at1.send_and_verify('AT+CNMI=?', test_regex_csms_0, timeout=test.TIMEOUT))

        test.log.step('- enable Phase 2+ (if supported) compatible SMS command syntax and check CNMI test command')
        test.expect(test.dut.at1.send_and_verify('AT+CSMS=1', test.OK))
        test.expect(test.dut.at1.send_and_verify('AT+CNMI=?', test_regex_csms_1, timeout=test.TIMEOUT))

        test.log.step('- check read command default settings (after AT&F) - actual settings: default value')
        test.dut.at1.send_and_verify("AT&F", test.OK)
        test.expect(test.dut.at1.send_and_verify('AT+CNMI?', r'.*\+CNMI: 0,0,0,0,1.*OK.*', timeout=test.TIMEOUT))

        test.log.step('- set only first parameter of CNMI - mode=1')
        test.expect(test.dut.at1.send_and_verify('AT+CNMI=1', test.OK, timeout=test.TIMEOUT))

        test.log.step('- read actual settings: mode=1')
        test.expect(test.dut.at1.send_and_verify('AT+CNMI?', r'.*\+CNMI: 1,\d,\d,\d,\d.*OK.*', timeout=test.TIMEOUT))

        test.log.step('- set the first two parameters of CNMI - mode=1 and mt=1')
        test.expect(test.dut.at1.send_and_verify('AT+CNMI=1,1', test.OK, timeout=test.TIMEOUT))

        test.log.step('- read actual settings: mode=1, mt=1')
        test.expect(test.dut.at1.send_and_verify('AT+CNMI?', r'.*\+CNMI: 1,1,\d,\d,\d.*OK.*', timeout=test.TIMEOUT))

        test.log.step('- set the first three parameters of CNMI - mode=1, mt=1 and bm=0')
        test.expect(test.dut.at1.send_and_verify('AT+CNMI=1,1,0', test.OK, timeout=test.TIMEOUT))

        test.log.step('- read actual settings: mode=1, mt=1, bm=0')
        test.expect(test.dut.at1.send_and_verify('AT+CNMI?', r'.*\+CNMI: 1,1,0,\d,\d.*OK.*', timeout=test.TIMEOUT))

        test.log.step('- set the first four parameters of CNMI - mode=1, mt=1, bm=0 and ds=0')
        test.expect(test.dut.at1.send_and_verify('AT+CNMI=1,1,0,0', test.OK, timeout=test.TIMEOUT))

        test.log.step('- read actual settings: mode=1, mt=1, bm=0, ds=0')
        test.expect(test.dut.at1.send_and_verify('AT+CNMI?', r'.*\+CNMI: 1,1,0,0,\d.*OK.*', timeout=test.TIMEOUT))

        test.log.step('- set all parameters of CNMI - mode=1, mt=1, bm=0, ds=0 and bfr=1')
        test.expect(test.dut.at1.send_and_verify('AT+CNMI=1,1,0,0,1', test.OK, timeout=test.TIMEOUT))

        test.log.step('- read actual settings: mode=1, mt=1, bm=0, ds=0, bfr=1')
        test.expect(test.dut.at1.send_and_verify('AT+CNMI?', r'.*\+CNMI: 1,1,0,0,1.*OK.*', timeout=test.TIMEOUT))

        test.log.step('Step 2. check all parameters and also with invalid values')
        test.log.step('- check EXEC command')
        test.expect(test.dut.at1.send_and_verify('AT+CNMI', test.CMS_ERROR, timeout=test.TIMEOUT))

        test.log.step('- check test command invalid value')
        test.expect(test.dut.at1.send_and_verify('AT+CNMI=1?', test.CMS_ERROR, timeout=test.TIMEOUT))

        test.log.step('- check read command invalid value')
        test.expect(test.dut.at1.send_and_verify('AT+CNMI1?', test.CMS_ERROR, timeout=test.TIMEOUT))

        test.log.step('- try to set not supported value for parameters: \n'
                      'e.g. mode/mt: -1,4, bm/ds: -1,3, bfr: -1,5, and for mix parameters')
        invalid_parameters_pdu = ["-1", "4", "1,-1", "1,4", "1,1,-1", "1,1,3", "1,1,0,-1", "1,1,0,3",
                                  "1,1,0,0,-1", "1,1,0,0,5", "1,-1,0,3,5"]
        for param in invalid_parameters_pdu:
            test.expect(test.dut.at1.send_and_verify("AT+CNMI={}".format(param), test.CMS_ERROR))

        test.log.step('- try to set empty write command (result according to ATC)')
        test.expect(test.dut.at1.send_and_verify('AT+CNMI=', test.OK, timeout=test.TIMEOUT))
        test.expect(test.dut.at1.send_and_verify('AT+CNMI?', r'.*\+CNMI: 1,1,0,0,1.*OK.*', timeout=test.TIMEOUT))

        test.log.step('- try to set write command with more than 1 parameter')
        test.expect(test.dut.at1.send_and_verify('AT+CNMI=1,1,0,0,1,1', test.CMS_ERROR, timeout=test.TIMEOUT))

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT&F", test.OK))


if "__main__" == __name__:
    unicorn.main()
