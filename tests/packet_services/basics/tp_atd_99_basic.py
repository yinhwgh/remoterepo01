#responsible: grzegorz.brzyk@globallogic.com
#location: Wroclaw
#TC0092085.001

import unicorn
import re
import time
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart 
from dstl.network_service.attach_to_network import enter_pin
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.call.switch_to_command_mode import *
from dstl.identification.get_imei import *

class Test(BaseTest):
    """
    TC0092085.001 - Atd99Basic    #test procedure version: 0.1.5

    INTENTION
    Basic ATD*99# test.
    """

    def setup(test):
        global project
        test.log.step("0. Prepare module")
        test.time_value = 10
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_restart(test.dut)
        project = test.dut.project.upper()

    def run(test):
        sim_provider = test.dut.sim.provider.upper()
        if sim_provider == "VERIZON":
            dialup_numbers = ['*99#', '*99**1*3#', '*99***3#']
            invalid_numbers = ['*99', '*99***********#', '*99#abc', '*99***a#', '*99**a*3#']
        else:
            dialup_numbers = ['*99#', '*99**1*1#', '*99***1#']
            invalid_numbers = ['*99', '*99***********#', '*99#abc', '*99***a#', '*99**a*1#']
        if test.dut.project.upper() == "VIPER":
            test.expect(test.dut.at1.send_and_verify(
                'AT^SCFG="MEopMode/ExpectDTR","current","acm0","acm1","acm2","acm3","asc0"', ".*OK.*",
                timeout=test.time_value))
        else:
            test.expect(test.dut.at1.send_and_verify(
                'AT^SCFG="MEopMode/ExpectDTR","current","acm0","acm1","acm2","acm3","mbim","asc0"', ".*OK.*",
                timeout=test.time_value))
        time.sleep(5)
        tc_steps_without_pin(test, dialup_numbers)
        tc_steps_with_pin(test, sim_provider, invalid_numbers)

    def cleanup(test):
        test.log.info("Check if module escape to command mode")
        test.dut.at1.send("AT", timeout=test.time_value)
        if "OK" not in test.dut.at1.last_response:
            test.log.info("Switch to command mode")
            test.expect(test.dut.dstl_switch_to_command_mode_by_dtr())
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*", timeout=test.time_value))

def tc_steps_without_pin(test, dialup_numbers):
    test.log.step("Step 1: Check command without and with PIN")
    test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*", timeout=test.time_value))

    test.log.step("Check command without PIN authentication")
    test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "+CPIN: SIM PIN", timeout=test.time_value))
    for number in dialup_numbers:
        check_invalid_connection(test, number)

def tc_steps_with_pin(test, sim_provider, invalid_numbers):
    test.log.step("Check command with PIN authentication")
    test.expect(dstl_register_to_network(test.dut))
    test.expect(test.dut.at1.send_and_verify("AT^SMONI", ".*OK.*", timeout=test.time_value))
    test.expect(test.dut.at1.send_and_verify("AT+CIMI", ".*OK.*"))
    test.expect(test.dut.at1.send_and_verify("AT&D2", ".*OK.*"))
    dut_connection = dstl_get_connection_setup_object(test.dut, device_interface="at1")
    test.expect(dut_connection.dstl_define_pdp_context())
    if test.dut.project.upper() != ("VIPER" or "BOBCAT" or "SERVAL"):
        test.expect(dut_connection.dstl_attach_to_packet_domain())
    else:
        test.expect(dstl_register_to_network(test.dut))
    test.expect(test.dut.at1.send_and_verify("AT+CGDCONT?", ".*OK.*", timeout=test.time_value))
    check_valid_connection(test, '*99#')

    test.log.step("Step 2: Check ATD*99# and ATH commands.")
    check_valid_connection(test, '*99#')

    test.log.step("Step 3: Check ATD*99***1# (or ATD*99***3# if Verizon) and ATH commands.")
    if sim_provider == 'VERIZON':
        check_valid_connection(test, '*99***3#')
    else:
        check_valid_connection(test, '*99***1#')

    test.log.step("Step 4: Check ATD*99# with invalid parameters.")
    for number in invalid_numbers:
        check_invalid_connection(test, number)


def check_invalid_connection(test, number):
    test.log.info("Establish PPP Connection")
    test.expect(test.dut.at1.send_and_verify(
        "ATD{}".format(number), ".*CME ERROR:.*|.*ERROR.*", wait_for=".*CME ERROR:.*|.*ERROR.*"))

def check_valid_connection(test, number):
    test.log.info("Establish PPP Connection")
    test.expect(test.dut.at1.send_and_verify("ATD{}".format(number), ".*CONNECT.*", wait_for=".*CONNECT.*"))
    test.log.info("Switch to command mode using +++")
    test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
    test.log.info("Disconnect PPP Connection")
    test.expect(test.dut.at1.send_and_verify("ATH", ".*OK.*", wait_for=".*OK.*"))


if  "__main__" == __name__:
    unicorn.main()