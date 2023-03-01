#responsible: yanen.wang@thalesgroup.com
#location: Beijing
#TC0104290.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.call.switch_to_command_mode import *
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_network
from dstl.security.lock_unlock_sim import *

class Test(BaseTest):
    """
    TC0104290.001 -  Atd99BasicDtr
    Basic ATD*99# test and DTR line functionalities checks for different AT&D settings

    """
    def setup(test):
        dstl_detect(test.dut)
        if test.dut.platform is 'INTEL':
            test.dut.at1.send_and_verify('AT^SCFG= "Gpio/mode/DTR0","std"', '.*OK.*')
            test.dut.dstl_lock_sim()
            test.log.step("**1.Check command without PIN ")
            test.expect(dstl_restart(test.dut))
            test.expect(test.dut.at1.send_and_verify('AT&D', '.*OK|.*ERROR'))
            test.log.step("**2.Check command AT&D with PIN")
            test.expect(dstl_enter_pin(test.dut))
            test.expect(test.dut.at1.send_and_verify('AT&D', '.*OK.*'))
            test.dut.dstl_unlock_sim()
        else:
            test.dut.dstl_unlock_sim()

    def run(test):
        project = test.dut.project.upper()
        if project == "SERVAL":
            test.expect(dstl_register_to_network(test.dut))
            test.log.step("**3.AT&D2**")
            test.expect(test.dut.at1.send_and_verify(r'AT&D2', '.*OK.*'))
            test.log.step("*3.1 Check ATD*99# - wait for connect - disconnect PPP connection via DTR line")
            test.expect(test.dut.at1.send_and_verify(r'ATD*99#','.*CONNECT.*', wait_for="CONNECT", timeout=60))
            test.expect(test.dut.dstl_switch_to_command_mode_by_dtr())
            test.log.step("*3.2 Check ATD*99***<cid># - wait for connect - disconnect PPP connection via DTR line")
            test.expect(test.dut.at1.send_and_verify(r'ATD*99***1#','.*CONNECT.*', wait_for="CONNECT", timeout=60))
            test.expect(dstl_switch_to_command_mode_by_dtr(test.dut))
            test.log.step("*3.3 Check ATD*99**<L2P>*<cid># - wait for connect - disconnect PPP connection via DTR line")
            test.expect(test.dut.at1.send_and_verify(r'ATD*99**PPP*1#','.*CONNECT.*', wait_for="CONNECT", timeout=60))
            test.expect(dstl_switch_to_command_mode_by_dtr(test.dut))
            test.log.step("*3.4 Check ATD*99# - wait for connect - switch from PPP online mode to command mode "
                          "- disconnect PPP connection via DTR line")
            test.expect(test.dut.at1.send_and_verify(r'ATD*99#', '.*CONNECT.*', wait_for="CONNECT", timeout=60))
            test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
            test.expect(test.dut.at1.send_and_verify(r'ATO', 'CONNECT', wait_for="CONNECT", timeout=60))
            test.expect(test.dut.dstl_switch_to_command_mode_by_dtr())
            test.log.step("*3.5 Check ATD*99***<cid># - wait for connect - switch from PPP online mode to command mode "
                          "- disconnect PPP connection via DTR line")
            test.expect(test.dut.at1.send_and_verify(r'ATD*99***1#', '.*CONNECT.*', wait_for="CONNECT", timeout=60))
            test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
            test.expect(test.dut.at1.send_and_verify(r'ATO', 'CONNECT', wait_for="CONNECT", timeout=60))
            test.expect(test.dut.dstl_switch_to_command_mode_by_dtr())
            test.log.step("*3.6 Check ATD*99**<L2P>*<cid># - wait for connect - switch from PPP online mode to "
                          "command mode - disconnect PPP connection via DTR line")
            test.expect(test.dut.at1.send_and_verify(r'ATD*99**PPP*1#', '.*CONNECT.*', wait_for="CONNECT", timeout=60))
            test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
            test.expect(test.dut.at1.send_and_verify(r'ATO', 'CONNECT', wait_for="CONNECT", timeout=60))
            test.expect(test.dut.dstl_switch_to_command_mode_by_dtr())

            test.log.step("**4.AT&D1**")
            test.expect(dstl_restart(test.dut))
            test.expect(dstl_register_to_network(test.dut))
            test.log.step("*4.1 Send ATD*99# - wait for connect – enter command mode via DTR line - set AT&D2 command "
                          "- return  to command mode via ATO")
            test.dut.at1.send_and_verify(r'AT&D1', '.*OK.*')
            test.expect(test.dut.at1.send_and_verify(r'ATD*99#', '.*CONNECT.*', wait_for="CONNECT", timeout=60))
            test.dut.dstl_switch_to_command_mode_by_dtr()
            test.dut.at1.send_and_verify(r'AT&D2', '.*OK.*')
            test.dut.at1.send_and_verify(r'ATO', '.*CONNECT.*', wait_for="CONNECT", timeout=60)
            test.expect(test.dut.dstl_switch_to_command_mode_by_dtr())
            test.expect(dstl_restart(test.dut))
            test.expect(dstl_register_to_network(test.dut))
            test.log.step("*4.2  Set AT&D1 - send ATD*99***<cid># - wait for connect – enter command mode via DTR line "
                          "- set AT&D2 command - return  to command mode via ATO")
            test.dut.at1.send_and_verify(r'AT&D1', '.*OK.*')
            test.expect(test.dut.at1.send_and_verify(r'ATD*99***1#', '.*CONNECT.*', wait_for="CONNECT", timeout=60))
            test.expect(test.dut.dstl_switch_to_command_mode_by_dtr())
            test.expect(test.dut.at1.send_and_verify(r'AT&D2', '.*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'ATO', '.*CONNECT.*', wait_for="CONNECT", timeout=60))
            test.expect(test.dut.dstl_switch_to_command_mode_by_dtr())
            test.dut.dstl_restart()
            test.expect(dstl_register_to_network(test.dut))
            test.log.step("*4.3  Set AT&D1 - send ATD*99**<L2P>*<cid># - wait for connect – enter command mode via "
                          "DTR line - set AT&D2 command - return  to command mode via ATO")
            test.dut.at1.send_and_verify(r'AT&D1', '.*OK.*')
            test.expect(test.dut.at1.send_and_verify(r'ATD*99**PPP*1#', '.*CONNECT.*', wait_for="CONNECT", timeout=60))
            test.expect(test.dut.dstl_switch_to_command_mode_by_dtr())
            test.expect(test.dut.at1.send_and_verify(r'AT&D2', '.*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'ATO', '.*CONNECT.*', wait_for="CONNECT", timeout=60))
            test.expect(test.dut.dstl_switch_to_command_mode_by_dtr())

            test.log.step("**5.AT&D0 ** ")
            test.dut.dstl_restart()
            test.expect(dstl_register_to_network(test.dut))
            test.dut.at1.send_and_verify(r'AT&D0', '.*OK.*')
            test.log.step("*5.1.Send ATD*99# - wait for connect – check behavior after DTR line – "
                          "enter command mode via +++ check behavior after DTR line - set AT&D2 command - "
                          "return  to data mode via ATO")
            test.expect(test.dut.at1.send_and_verify(r'ATD*99#', '.*CONNECT.*', wait_for="CONNECT", timeout=60))
            test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
            test.dut.at1.send_and_verify(r'AT&D2', '.*OK.*')
            test.expect(test.dut.at1.send_and_verify(r'ATO', '.*CONNECT.*', wait_for="CONNECT", timeout=60))
            test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())

            test.log.step("**6. Check ATD*99# with invalid parameters ")
            test.expect(dstl_restart(test.dut))
            test.expect(dstl_register_to_network(test.dut))
            test.expect(test.dut.at1.send_and_verify(r'ATD*99**APN*55#', '.*ERROR: invalid index'))
            test.expect(test.dut.at1.send_and_verify('AT&F', 'OK'))
            test.expect(test.dut.at1.send_and_verify('AT&W', 'OK'))
        if project == "VIPER":
            test.expect(dstl_register_to_network(test.dut))
            test.log.step("**3.AT&D2**")
            test.expect(test.dut.at1.send_and_verify(r'at^spow=1,0,0', '.*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT&D2', '.*OK.*'))
            test.log.step("*3.1 Check ATD*99# - wait for connect - disconnect PPP connection via DTR line")
            test.expect(test.dut.at1.send_and_verify(r'ATD*99#', '.*CONNECT.*', wait_for="CONNECT", timeout=60))
            test.expect(test.dut.dstl_switch_to_command_mode_by_dtr())
            test.log.step(
                "*3.4 Check ATD*99# - wait for connect - switch from PPP online mode to command mode - "
                "disconnect PPP connection via DTR line")
            test.expect(test.dut.at1.send_and_verify(r'ATD*99#', '.*CONNECT.*', wait_for="CONNECT", timeout=60))
            test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
            test.expect(test.dut.at1.send_and_verify(r'ATO', 'CONNECT', wait_for="CONNECT", timeout=60))
            test.expect(test.dut.dstl_switch_to_command_mode_by_dtr())
            test.log.step(
                "*3.5 Check ATD*99***<cid># - wait for connect - switch from PPP online mode to command mode - "
                "disconnect PPP connection via DTR line")
            test.expect(test.dut.at1.send_and_verify(r'ATD*99***1#', '.*CONNECT.*', wait_for="CONNECT", timeout=60))
            test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
            test.expect(test.dut.at1.send_and_verify(r'ATO', 'CONNECT', wait_for="CONNECT", timeout=60))
            test.expect(test.dut.dstl_switch_to_command_mode_by_dtr())
            test.log.step("**4.AT&D1**")
            # test.expect(dstl_restart(test.dut))
            # test.expect(dstl_register_to_network(test.dut))
            test.log.step(
                "*4.1 Send ATD*99# - wait for connect - "
                "enter command mode via DTR line - set AT&D2 command - return  to command mode via ATO")
            test.dut.at1.send_and_verify(r'AT&D1', '.*OK.*')
            test.expect(test.dut.at1.send_and_verify(r'ATD*99#', '.*CONNECT.*', wait_for="CONNECT", timeout=60))
            test.dut.dstl_switch_to_command_mode_by_dtr()
            test.dut.at1.send_and_verify(r'AT&D2', '.*OK.*')
            test.dut.at1.send_and_verify(r'ATO', '.*CONNECT.*', wait_for="CONNECT", timeout=60)
            test.expect(test.dut.dstl_switch_to_command_mode_by_dtr())
            # test.expect(dstl_restart(test.dut))
            # test.expect(dstl_register_to_network(test.dut))
            test.log.step(
                "*4.2  Set AT&D1 - send ATD*99***<cid># - wait for connect – "
                "enter command mode via DTR line - set AT&D2 command - return  to command mode via ATO")
            test.dut.at1.send_and_verify(r'AT&D1', '.*OK.*')
            test.expect(test.dut.at1.send_and_verify(r'ATD*99***1#', '.*CONNECT.*', wait_for="CONNECT", timeout=60))
            test.expect(test.dut.dstl_switch_to_command_mode_by_dtr())
            test.expect(test.dut.at1.send_and_verify(r'AT&D2', '.*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'ATO', '.*CONNECT.*', wait_for="CONNECT", timeout=60))
            test.expect(test.dut.dstl_switch_to_command_mode_by_dtr())
            test.dut.dstl_restart()
            test.expect(dstl_register_to_network(test.dut))
            test.log.step("**5.AT&D0 ** ")
            # test.dut.dstl_restart()
            # test.expect(dstl_register_to_network(test.dut))
            test.dut.at1.send_and_verify(r'AT&D0', '.*OK.*')
            test.log.step(
                "*5.1.Send ATD*99# - wait for connect – check behavior after DTR line – enter command mode "
                "via +++ check behavior after DTR line - set AT&D2 command - return  to data mode via ATO")
            test.expect(test.dut.at1.send_and_verify(r'ATD*99#', '.*CONNECT.*', wait_for="CONNECT", timeout=60))
            test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
            test.dut.at1.send_and_verify(r'AT&D2', '.*OK.*')
            test.expect(test.dut.at1.send_and_verify(r'ATO', '.*CONNECT.*', wait_for="CONNECT", timeout=60))
            test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())

            test.log.step("**6. Check ATD*99# with invalid parameters ")
            # test.expect(dstl_restart(test.dut))
            # test.expect(dstl_register_to_network(test.dut))
            test.expect(test.dut.at1.send_and_verify(r'ATD*99**APN*55#', '.*ERROR: invalid index'))
            test.expect(test.dut.at1.send_and_verify('AT&F', 'OK'))
            test.expect(test.dut.at1.send_and_verify('AT&W', 'OK'))

    def cleanup(test):
        pass


if __name__ == "__main__":
    unicorn.main()
