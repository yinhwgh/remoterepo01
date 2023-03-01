#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0105650.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.security import spc_security
from dstl.security import lock_unlock_sim
from dstl.configuration import functionality_modes
import os
import time

class Test(BaseTest):
    """
 	TC0105650.001 - SsecugBasic
    Intention: Check basic functionality of SSECUG command.

    """

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_lock_sim())
        test.expect(test.dut.dstl_restart())

    def run(test):
        test.spc_pwd = test.dut.dstl_get_spc_password()
        test.log.step("1. Check command without SIM PIN input.")
        test.attempt(test.dut.at1.send_and_verify, "AT+CPIN?", "SIM PIN", retry=3, sleep=2)
        unlocked = test.dut.at1.send_and_verify(f'AT^SSECUG="Factory/Debug","unlock",'
                                                f'"{test.spc_pwd}"', "OK")
        test.expect(unlocked,
                    msg=f"Unable to unlock Factory/Debug, please check if SPC "
                    f"password is {test.spc_pwd}.", critical=True)
        test.expect(test.dut.at1.send_and_verify('AT^SSECUG="Factory/Debug"',
                                                 '\^SSECUG: "Factory/Debug", UNLOCK'))
        test.expect(test.dut.at1.send_and_verify(f'AT^SSECUG="Factory/Debug","lock",'
                                                 f'"{test.spc_pwd}"', "OK"))
        test.expect(test.dut.at1.send_and_verify('AT^SSECUG="Factory/Debug"',
                                                 '\^SSECUG: "Factory/Debug", LOCK'))
        test.expect(test.dut.at1.send_and_verify(f'AT^SSECUG="Factory/Debug","unlock",'
                                                 f'"{test.spc_pwd}"', "OK"))

        test.log.step("2. Enter SIM PIN.")
        test.expect(test.dut.dstl_enter_pin())


        test.log.step("3. CFUN: 1 -> Check parameters for valid and invalid values")
        test.expect(test.dut.at1.send_and_verify(f'AT^SSECUG="Factory/Debug","lock",'
                                                 f'"{test.spc_pwd}"', "OK"))
        test.expect(test.dut.at1.send_and_verify('AT^SSECUG="Factory/Debug"',
                                                 '\^SSECUG: "Factory/Debug", LOCK'))
        test.expect(test.dut.at1.send_and_verify(f'AT^SSECUG="Factory/Debug","unlock",'
                                                 f'"{test.spc_pwd}"', "OK"))
        test.expect(test.dut.at1.send_and_verify('AT^SSECUG="Factory/Debug"',
                                                 '\^SSECUG: "Factory/Debug", UNLOCK'))
        test.log.info("LOCK does not need a password.")
        test.expect(test.dut.at1.send_and_verify('AT^SSECUG="Factory/Debug","LOCK"',
                                                 '\^SSECUG: "Factory/Debug", LOCK'))
        # A dictionary consist of ATC and its expected response, description
        invalid_cmds = {'AT^SSECUG': ["ERROR", "Execute command is invalid."],
                        'AT^SSECUG?': ["ERROR", "Read command is invalid."],
                        'AT^SSECUG=?': ["ERROR", "Test command is invalid."],
                        'AT^SSECUG="Factory/Debug","unlock"':
                            ["ERROR", "Write command without password is invalid."],
                        'AT^SSECUG="Factory/Debug","unlock"':
                            ["ERROR", "Write command without password is invalid."],
                        'AT^SSECUG="Factory/run"':
                            ["ERROR", "Write command with invalid parameter \"run\"."],
                        'AT^SSECUG="Factory/Debug","abc"':
                            ["ERROR", "Write command with invalid parameter \"abc\"."],
                        f'AT^SSECUG="Factory/Debug","abc","{test.spc_pwd}"':
                            ["ERROR", "Write command with invalid parameter, valid password."],
                        f'AT^SSECUG="Factory/Debug","unlock","{test.spc_pwd}1"':
                            ["ERROR", "Write command - unlock with invalid password length+1."],
                        'AT^SSECUG="Factory/Debug","unlock","abcdef"':
                            ["ERROR", "Write command - unlock with invalid password - alphas."],
                        'AT^SSECUG="Factory/Debug","unlock","111111"':
                            ["ERROR", "Write command - unlock with invalid password - digits."],
                        'AT^SSECUG="Factory/Debug","unlock",""':
                            ["ERROR", "Write command - unlock with empty password."]
                        
        }
        sub_step = 0
        for cmd, value in invalid_cmds.items():
            sub_step += 1
            expect = value[0]
            description = value[1]
            test.log.h3(f"3.{sub_step} CFUN:1 -> {description}")
            test.expect(test.dut.at1.send_and_verify(cmd, expect))

        test.log.step("4. Check if is non-volatile")
        test.expect(test.dut.at1.send_and_verify(f'AT^SSECUG="Factory/Debug","lock",'
                                                 f'"{test.spc_pwd}"', "OK"))
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_restart())
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify('AT^SSECUG="Factory/Debug"', '\^SSECUG: '
                                                                              '"Factory/Debug", LOCK'))
        test.expect(test.dut.at1.send_and_verify(f'AT^SSECUG="Factory/Debug","unlock",'
                                                 f'"{test.spc_pwd}"', "OK"))
        test.expect(test.dut.dstl_restart())
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify('AT^SSECUG="Factory/Debug"',
                                                 '\^SSECUG: "Factory/Debug", UNLOCK'))

        test.log.step("5. CFUN:4 -> Repeat step 3 in Airplane mode - should work same as CFUN:1 ")
        test.expect(test.dut.dstl_set_airplane_mode())
        test.expect(test.dut.at1.send_and_verify(f'AT^SSECUG="Factory/Debug","lock",'
                                                 f'"{test.spc_pwd}"', "OK"))
        test.expect(test.dut.at1.send_and_verify('AT^SSECUG="Factory/Debug"',
                                                 '\^SSECUG: "Factory/Debug", LOCK'))
        test.expect(test.dut.at1.send_and_verify(f'AT^SSECUG="Factory/Debug","unlock",'
                                                 f'"{test.spc_pwd}"', "OK"))
        test.expect(test.dut.at1.send_and_verify('AT^SSECUG="Factory/Debug"',
                                                 '\^SSECUG: "Factory/Debug", UNLOCK'))
        
        sub_step = 0
        for cmd, expect in invalid_cmds.items():
            sub_step += 1
            expect = expect[0]
            description = expect[1]
            test.log.h3(f"5.{sub_step} CFUN:4 -> {description}")
            test.expect(test.dut.at1.send_and_verify(cmd, expect))

        
    def cleanup(test):
        test.expect(test.dut.dstl_set_full_functionality_mode())
        test.expect(test.dut.at1.send_and_verify(f'AT^SSECUG="Factory/Debug","lock",'
                                                 f'"{test.spc_pwd}"', "OK"))

if __name__ == "__main__":
    unicorn.main()