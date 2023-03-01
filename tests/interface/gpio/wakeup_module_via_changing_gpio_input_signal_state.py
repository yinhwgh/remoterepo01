#responsible: yi.guo@thalesgroup.com
#location: Beijing
#TC0106003.001 - Wakeup_Module_Via_Changing_GPIO_Input_Signal_State

'''
Test with McTest4 board
'''

import unicorn

from core.basetest import BaseTest

from dstl.auxiliary.devboard.devboard import *
from dstl.auxiliary.restart_module import *
from dstl.network_service.register_to_network import *
from dstl.configuration import suspend_mode_operation
from dstl.auxiliary.init import *
from dstl.security.lock_unlock_sim import *
from dstl.status_control import extended_indicator_control

from dstl.gpio.gpio_on_module.open_gpio_driver import *
from dstl.gpio.gpio_on_module.close_gpio_driver import *
from dstl.gpio.gpio_on_module.get_gpio_pin_state import *
from dstl.gpio.gpio_on_module.close_gpio_pin import *
from dstl.gpio.gpio_on_module.open_gpio_pin_as_input import *
from dstl.gpio.gpio_on_module.get_available_gpio_pins import *



class wakeup_Module_Via_Changing_GPIO_Input_Signal_State(BaseTest):



    def setup(test):
        test.log.info("*******************************************************************")
        test.log.info("SetUp_1: Initiate module and restore to default configurations ")
        test.log.info("*******************************************************************")
        test.dut.detect()
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK",timeout=30))
        test.expect(test.dut.at1.send_and_verify("AT&W", "OK", timeout=30))
        test.log.info("*******************************************************************")
        test.log.info("SetUp_2: Disable SIM PIN lock before testing  ")
        test.log.info("*******************************************************************")
        test.dut.dstl_unlock_sim()
        test.disable_uart_powersaving()
        #test.dut.dstl_register_to_lte()

    def run(test):
        test.log.info("*******************************************************************")
        test.log.info("RunTest_1: Open GPIO")
        test.log.info("*******************************************************************")
        test.dut.dstl_open_gpio_driver()

        test.log.info("*******************************************************************")
        test.log.info("RunTest_2: Open GPIO 21 and 22 as input driver")
        test.log.info("*******************************************************************")
        test.dut.dstl_open_gpio_pin_as_input(21)
        test.dut.dstl_open_gpio_pin_as_input(22)

        test.log.info("*******************************************************************")
        test.log.info("RunTest_3: Enable CTS0/CTS1 URC on MC_Board")
        test.log.info("*******************************************************************")
        test.expect(test.dut.devboard.send_and_verify(r"MC:URC=OFF", 'MC:   OK', timeout = 2, ))
        test.expect(test.dut.devboard.send_and_verify(r"MC:URC=SER", 'MC:   OK', timeout = 2, ))
        test.expect(test.dut.devboard.send_and_verify(r"MC:MODULE=EHS5", r'.*MC:   Module family: EHS5.*', 'MC:   OK', timeout = 2, ))
        test.expect(test.dut.devboard.send_and_verify(r"MC:GPIOcfg=1.8V", r'.*MC:   Module family: EHS5.*', 'MC:   OK',
                                                      timeout=2, ))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_4: Enable UART Power saving mode")
        test.log.info("*******************************************************************")
        test.enable_uart_powersaving()
        test.expect(test.dut.devboard.wait_for("CTS0: 1"))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_5: Change the GPIO21 input signal state to wake up module")
        test.log.info("*******************************************************************")

        test.expect(test.dut.devboard.send_and_verify(r"MC:GPIO20=out",'MC:   OK',timeout=2, ))
        test.expect(test.dut.devboard.send_and_verify(r"MC:GPIO20=1", 'MC:   OK', timeout=2, ))
        test.expect("CTS0: 0" in test.dut.devboard.last_response)
        test.expect("CTS1: 0" in test.dut.devboard.last_response)
        test.expect(test.dut.devboard.wait_for("CTS0: 1" ))
        test.expect("CTS1: 1" in test.dut.devboard.last_response)

        test.expect(test.dut.devboard.send_and_verify(r"MC:GPIO20=0", 'MC:   OK', timeout=2, ))
        test.expect("CTS0: 0" in test.dut.devboard.last_response)
        test.expect("CTS1: 0" in test.dut.devboard.last_response)
        test.expect(test.dut.devboard.wait_for("CTS0: 1" ))
        test.expect("CTS1: 1" in test.dut.devboard.last_response)

        test.log.info("*******************************************************************")
        test.log.info("RunTest_6: Change the GPIO22 input signal state to wake up module")
        test.log.info("*******************************************************************")
        test.expect(test.dut.devboard.send_and_verify(r"MC:GPIO21=out",'MC:   OK',timeout=2, ))
        test.expect(test.dut.devboard.send_and_verify(r"MC:GPIO21=1", 'MC:   OK', timeout=2, ))
        test.expect("CTS0: 0" in test.dut.devboard.last_response)
        test.expect("CTS1: 0" in test.dut.devboard.last_response)
        test.expect(test.dut.devboard.wait_for("CTS0: 1" ))
        test.expect("CTS1: 1" in test.dut.devboard.last_response)

        test.expect(test.dut.devboard.send_and_verify(r"MC:GPIO21=0", 'MC:   OK', timeout=2, ))
        test.expect("CTS0: 0" in test.dut.devboard.last_response)
        test.expect("CTS1: 0" in test.dut.devboard.last_response)
        test.expect(test.dut.devboard.wait_for("CTS0: 1" ))
        test.expect("CTS1: 1" in test.dut.devboard.last_response)

    def cleanup(test):
        test.log.info("*******************************************************************")
        test.log.info("CleanUp_1: Disable UART power saving mode ")
        test.log.info("*******************************************************************")
        test.wakeup_module_via_rts()
        test.disable_uart_powersaving()

        test.log.info("*******************************************************************")
        test.log.info("CleanUp_2: Close GPIO driver")
        test.log.info("*******************************************************************")
        test.dut.dstl_close_gpio_driver()

    def enable_uart_powersaving(test, pwrsave_period=0, pwrsave_wakeup=50):
        test.dut.at1.send_and_verify(
            'AT^SCFG="MEopMode/PwrSave","enabled",{},{}'.format(pwrsave_period, pwrsave_wakeup), "OK", timeout=10)

    def disable_uart_powersaving(test):
        test.wakeup_module_via_rts()
        test.dut.at1.send_and_verify('AT^SCFG="MEopMode/PwrSave","disabled"', "OK", timeout=10)

    def wakeup_module_via_rts(test):
        test.dut.at1.connection.setRTS(False)
        test.sleep(0.1)
        test.dut.at1.connection.setRTS(True)

if (__name__ == "__main__"):
    unicorn.main()