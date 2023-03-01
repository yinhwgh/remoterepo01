#responsible: renata.bryla@globallogic.com
#location: Wroclaw
#TC0095055.001

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
    """TC0095055.001   TpAtCscbBasic
    This procedure provides the possibility of basic tests for the test and write command of +CSCB.

    1. Check command without and with PIN
    2. Check for several values of parameters and also with invalid values
    2a. Checking for several values of parameters with valid values
    2b. Checking for several values of parameters with invalid values
    """

    cscb_parameter_values = []

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*OK.*"))
        if re.search(r".*SIM PIN.*", test.dut.at1.last_response):
            test.expect(True, msg="SIM PIN code locked - checking if command is PIN protected could be realized")
        else:
            test.log.info("SIM PIN entered - restart is needed")
            test.expect(dstl_restart(test.dut))
            test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*OK.*"))
            if re.search(r".*SIM PIN.*", test.dut.at1.last_response):
                test.expect(True, msg="SIM PIN code locked - checking if command is PIN protected could be realized")
            else:
                test.expect(True, msg="SIM PIN code unlocked - must be locked for checking if command is PIN protected")
                test.expect(dstl_lock_sim(test.dut))
                test.expect(dstl_restart(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))

    def run(test):
        test.log.h2("Executing script for test case TC0095055.001 TpAtCscbBasic")
        test.log.step("Step 1. Check command without and with PIN")
        test.log.info("===== Check command without PIN =====")
        test.expect(test.dut.at1.send_and_verify("AT+CSCB=?", r".*\+CMS ERROR: SIM PIN required.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSCB? ", r".*\+CMS ERROR: SIM PIN required.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSCB=0,\"1-55\",\"0\"", r".*\+CMS ERROR: SIM PIN required.*"))
        test.log.info("===== Check command with PIN =====")
        test.expect(dstl_enter_pin(test.dut))
        test.sleep(10)  # waiting for module to get ready
        test.expect(test.dut.at1.send_and_verify("AT+CSCB=?", r".*\+CSCB: (\(0-1\)|\(0,1\)).*OK.*"))
        test.log.info("===== Check CSCB settings and get parameter values at the start of the test =====")
        test.expect(test.dut.at1.send_and_verify("AT+CSCB? ", r".*OK.*"))
        test.cscb_parameter_values = re.findall(r"\+CSCB:\s*(\d{1,3},\".*\",\".*\")\s*", test.dut.at1.last_response)
        if test.cscb_parameter_values:
            test.cscb_parameter_values = test.cscb_parameter_values[0].split(",")
        if len(test.cscb_parameter_values) == 3:
            test.log.info("===== Parameter <operation> value : {} =====".format(test.cscb_parameter_values[0]))
            test.log.info("===== Parameter <mids> value : {} =====".format(test.cscb_parameter_values[1]))
            test.log.info("===== Parameter <dcss> value : {} =====".format(test.cscb_parameter_values[2]))
        else:
            test.expect(False, msg="Incorrect parameter values in CSCB command")
        test.expect(test.dut.at1.send_and_verify("AT+CSCB=0,\"1-345\",\"0\"", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSCB? ", r"\+CSCB:\s*0,\"1-345\",\"0\".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSCB=1,\"1-55\",\"0\"", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSCB? ", r"\+CSCB:\s*1,\"56-345\",\"0\".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSCB=1,\"0-65535\",\"0\"", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSCB? ", r"\+CSCB:\s*1,\"\",\"0\".*OK.*"))

        test.log.step("Step 2. Check for several values of parameters and also with invalid values")
        test.log.step("Step 2a. Checking for several values of parameters with valid values")
        test.expect(test.dut.at1.send_and_verify("AT+CSCB=0,\"0,1,5,320-478,922\",\"0\"", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSCB=0,\"1111,2222,2345,32000-47200,55555,60000,65534,65534\","
                                                 "\"0-3\"", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSCB? ",
                    r"\+CSCB:\s*0,\"0-1,5,320-478,922,1111,2222,2345,32000-47200,55555,60000,65534\",\"0-3\".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSCB=1,\"0-65534\",\"0-3\"", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSCB? ", r"\+CSCB:\s*1,\"\",\"0-3\".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSCB=1,\"0-65535\",\"0\"", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSCB? ", r"\+CSCB:\s*1,\"\",\"0\".*OK.*"))

        test.log.step("Step 2b. Checking for several values of parameters with invalid values")
        invalid_values = ['a,"0,1,5,320-478,922","0"', '0,"aaa,ccc,de,trtre","0"', '0,"-5535","0"',
                          '0,"65536,72000","0"', '1,\"0-65536\",\"0\""']
        for parameters in invalid_values:
            test.expect(test.dut.at1.send_and_verify("AT+CSCB={}".format(parameters), ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSCB", ".*ERROR.*"))

    def cleanup(test):
        test.log.info("===== Restore CSCB settings from test start =====")
        if len(test.cscb_parameter_values) == 3:
            test.expect(test.dut.at1.send_and_verify("AT+CSCB={},{},{}".format(test.cscb_parameter_values[0],
                        test.cscb_parameter_values[1], test.cscb_parameter_values[2]), r".*OK.*"))
        else:
            test.log.info("Restore values impossible")
        test.dut.at1.send_and_verify("AT&F", ".*OK.*")
        test.dut.at1.send_and_verify("AT&W", ".*OK.*")


if "__main__" == __name__:
    unicorn.main()