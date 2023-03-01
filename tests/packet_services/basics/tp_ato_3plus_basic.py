#responsible: grzegorz.brzyk@globallogic.com
#location: Wroclaw
#TC0091852.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.identification.get_imei import *
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
    TC0091852.001 - TpAto3PlusBasic    test procedure version: 1.5

    INTENTION
    This procedure provides basic tests for the commands of ATO and +++.

    PRECONDITION
    Configuration:
    1. CSD:
    - DUT and REMOTE supporting CSD.
    - 2 SIM Cards supporting CSD.
    2. For PPP:
    - DUT supporting PPP connection.
    - SIM Cards supporting PPP connection.
    """

    def setup(test):
        test.log.step("0. Prepare module")
        dstl_detect(test.dut)
        test.expect(dstl_restart(test.dut))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=1,"IP","{}"'.format(test.dut.sim.apn_v4), ".*OK.*"))
        test.expect(dstl_register_to_network(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT+CGATT=1", ".*OK.*"))
        dstl_get_imei(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT+CIMI", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SMONI", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&D2", ".*OK.*"))

    def run(test):
        project = test.dut.project.upper()
        if project == "BOBCAT":
            test.expect(test.dut.at1.send_and_verify(
                'AT^SCFG="MEopMode/ExpectDTR","current","acm0","acm1","acm2","acm3","mbim","asc0"', ".*OK.*"))
            test.log.h2('CSD connection check omitted, CSD connection not supported on project Bobcat.')
            test.log.h2('Start check with AT+CGDATA command.')
            establish_ppp(test, ppp_type="AT+CGDATA")
            test.log.h2('Start check with ATD*99# command.')
            establish_ppp(test, ppp_type="ATD*99#")
        elif project == "SERVAL":
            test.log.h2('CSD connection check omitted, CSD connection not supported on project Serval.')
            test.log.h2('AT+CGDATA command check omitted, AT+CGDATA command not supported on project Serval.')
            test.log.h2('Start check with ATD*99# command.')
            establish_ppp(test, ppp_type="ATD*99#")
        elif project == "VIPER":
            test.log.h2('CSD connection check omitted, CSD connection not supported on project Viper.')
            test.log.h2('AT+CGDATA command check omitted, AT+CGDATA command not supported on project Viper.')
            test.log.h2('Start check with ATD*99# command.')
            test.expect(test.dut.at1.send_and_verify("ATD*99#", ".*CONNECT.*", wait_for=".*CONNECT.*"))
            test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
            test.expect(test.dut.at1.send_and_verify("ATO", ".*CONNECT.*", wait_for=".*CONNECT.*"))
            test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
        else:
            test.expect(False, critical=True, msg="Test procedure need be implemented for product.")

    def cleanup(test):
        test.dut.at1.send("AT", timeout=10)
        if "OK" not in test.dut.at1.last_response:
            test.expect(test.dut.dstl_switch_to_command_mode_by_dtr())
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))


def establish_ppp(test, ppp_type):
    test.log.step("Step 1.1  Establish PPP Connection using {} command".format(ppp_type))
    test.expect(test.dut.at1.send_and_verify("AT+CGDCONT?", ".*OK.*"))
    if ppp_type == "AT+CGDATA":
        test.expect(
            test.dut.at1.send_and_verify("AT+CGDATA=\"PPP\",1", ".*CONNECT.*", wait_for=".*CONNECT.*"))
    else:
        test.expect(test.dut.at1.send_and_verify("ATD*99#", ".*CONNECT.*", wait_for=".*CONNECT.*"))

    for iteration in range(1, 4):
        test.log.step("Step 1.2  Switch to command mode using +++")
        # test.expect(test.dut.at1.send_and_verify(b"+++", ".*OK.*", wait_for=".*OK.*"))
        test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
        test.log.step("Step 1.3  Switch to data mode using ATO")
        test.expect(test.dut.at1.send_and_verify("ATO", ".*CONNECT.*", wait_for=".*CONNECT.*"))
        test.log.step("Step 1.4  Repeat 2-3 times, iteration {}".format(iteration))
    else:
        test.log.step("Step 1.5  Disconnect PPP Connection")
        # test.expect(test.dut.dstl_switch_to_command_mode_by_dtr())
        test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())


if "__main__" == __name__:
    unicorn.main()
