#responsible: jing-j.wang@thalesgroup.com
#location: Beijing
#TC0106039.002

import unicorn
import re
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
    TC0106039.002 - TpDataModeandCommandModeSwitch

    INTENTION
    duration tests for the data mode and command mode switch test.
    """
    global time_value
    time_value = 10

    def setup(test):
        test.log.step("0. Prepare module")
        test.dut.at1.send_and_verify("ATE1", ".*OK.*", timeout=time_value)
        dstl_detect(test.dut)
        test.expect(dstl_restart(test.dut))
        test.expect(dstl_register_to_network(test.dut))
        dstl_get_imei(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT+CIMI", ".*OK.*", timeout=time_value))
        test.expect(test.dut.at1.send_and_verify("AT^SMONI", ".*OK.*", timeout=time_value))
        test.expect(test.dut.at1.send_and_verify("AT&D2", ".*OK.*", timeout=time_value))

    def run(test):
        test.log.step("*1.1 Check ATD*99# - wait for connect ")
        test.expect(test.dut.at1.send_and_verify(r'ATD*99#', '.*CONNECT.*', wait_for="CONNECT", timeout=60))

        for iteration in range(1, 2000):
            test.log.step("*2.1 Switch to command mode using +++ ")
            test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
            test.attempt(test.dut.at1.send_and_verify, "AT^SMONI", ".*SMONI:.*,.*,.*,.*", retry=10)
            test.expect(test.dut.at1.send_and_verify("AT^SMONI", ".*OK.*"))
            test.sleep(0.1)
            test.log.step("*2.2 switch back to data mode using ATO")
            test.expect(test.dut.at1.send_and_verify("ATO", ".*CONNECT.*", wait_for=".*CONNECT.*"))
            test.sleep(30)
            test.log.step("Repeat step2.1-2.2, iteration {}".format(iteration))

        test.log.step("Disconnect PPP connection")
        test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())

    def cleanup(test):
        pass


if (__name__ == "__main__"):
    unicorn.main()