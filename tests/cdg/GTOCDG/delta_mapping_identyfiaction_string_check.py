#responsible agata.mastalska@globallogic.com
#Wroclaw

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service import register_to_network, attach_to_network
import re

class Test(BaseTest):
    """
    Main goal is check if ati281 command returns 
    correct delta mapping identification string.

    1. restart module (shouldn't be registered to the network)
    2. check part number using ati281 command and compere it with set one in test campagne
    3. register module to the network
    4. check part number using ati281 command and compere it with set one in test campagne
    5. enable air plane mode 
    6.  check part number using ati281 command and compere it with set one in test campagne
    7. disable air plane mode

    author: agata.mastalska@globallogic.com
    """

    def setup(test):
        pass

    def run(test):
        module_without_pbready = ["MIAMI", "BOBCAT", "KINGSTON", "ODESSA"]
        module_without_airplane_mode = ["KINGSTON"]

        test.log.step("1. restart module (shouldn't be registered to the network)")
        test.dut.dstl_detect()
        test.dut.dstl_restart(test.dut.at1)

        if not test.pattern_part_number:
            test.log.error("part number was not given!")
            test.expect(False, critical=True)
        else:
            test.log.info("part number was given as: " + test.pattern_part_number)
            test.expect(True)

        test.expect(test.dut.at1.send_and_verify('AT+CMEE=2', '.*OK.*'))
        test.log.info("Checking PIN")
        test.expect(test.dut.at1.send_and_verify('at+cpin?', '.*OK.*'))

        if "READY" in test.dut.at1.last_response:
            test.log.info("PIN is already entered. Setting pin to module to '9999'")
            test.expect(test.dut.at1.send_and_verify("AT+CLCK=\"SC\",2", '.*OK.*'))
            if "+CLCK: 0" in test.dut.at1.last_response:
                test.expect(test.dut.at1.send_and_verify("AT+CLCK=\"SC\",1,\"{}\"".format(test.dut_sim.pin1), '.*OK.*'))
            test.dut.dstl_restart(test.dut.at1)
        
        elif "SIM not inserted" in test.dut.at1.last_response:
            test.log.error("Missing SIM card!")
            test.expect(False)

        test.log.step("2. checking if ati281 command works without entered pin")
        part_number = check_part_number(test)
        if part_number is False:
            test.log.error("FAILED")
            test.expect(False)
            test.dut.dstl_restart(test.dut.at1)
        else:
            test.log.info("part number matches to the pattern -> " + part_number)
            test.expect(True)

        test.log.step("3. register module to the network")
        test.expect(test.dut.dstl_enter_pin())
        if test.dut.project not in module_without_pbready:
            test.expect(test.dut.at1.wait_for('PBREADY',90))
        else:
            test.log.info("Module without pbready.")
        test.expect(test.dut.attach_to_network())

        test.log.step("4. checking if ati281 command works with entered pin")
        part_number = check_part_number(test)
        if part_number is False:
            test.log.error("FAILED")
            test.expect(False)
            test.dut.dstl_restart(test.dut.at1)
        else:
            test.log.info("part number matches to the pattern -> " + part_number)
            test.expect(True)

        test.log.step("5. enable air plane mode.")
        if test.dut.project not in module_without_airplane_mode:
            test.expect(test.dut.at1.send_and_verify("at+cfun=4", "OK"))
        else:
            test.log.info("Module without airplane mode.")

        test.log.step("6. checking if ati281 command works in airplane mode")
        if test.dut.project not in module_without_airplane_mode:
            part_number = check_part_number(test)
            if part_number is False:
                test.log.error("FAILED")
                test.expect(False)
                test.dut.dstl_restart(test.dut.at1)
            else:
                test.log.info("part number matches to the pattern -> " + part_number)

        test.log.step("6. checking if part number given with the campagne is equal to reading from module")
        if compare_pattern_part_number_vs_current_part_number(test, part_number, test.pattern_part_number) is False:
            test.expect(False, critical=True)

    def cleanup(test):
        test.log.step("7. disable air plane mode")
        test.expect(test.dut.at1.send_and_verify("at+cfun=1,1", "SYSSTART", 180))
        test.dut.at1.close()

if "__main__" == __name__:
    unicorn.main()

def check_part_number(test):
    test.expect(test.dut.at1.send_and_verify("ATI281", '.*OK.*'))
    if test.dut.at1.last_response is None:
        test.log.error("There is no ATI command")
        return False
    pattern = re.compile(r"[A-Z]\d\d\d\d\d-[A-Z]\d\d\d\d-[A-Z]\d\d\d")
    part_number = pattern.search(test.dut.at1.last_response)
    if part_number is not None:
        return part_number.group()
    else:
        test.log.error("Part number doesn't match to pattern")
        return False

def compare_pattern_part_number_vs_current_part_number(test, response, pattern_part_number):
    pattern = re.compile(r"[A-Z]\d\d\d\d\d-[A-Z]\d\d\d\d-[A-Z]\d\d\d")
    mo = pattern.search(pattern_part_number)

    if mo is not None:
        if pattern_part_number == response:
            test.log.info("part number given with the campagne: " + pattern_part_number + " is equal to reading from module:" + response)
        else:
            test.log.error("MISMATCH!! part number given with the campagne is NOT equal to reading from module")
            return False
    else:
        test.log.error("part number given with the campagne has wrong format")
        return False