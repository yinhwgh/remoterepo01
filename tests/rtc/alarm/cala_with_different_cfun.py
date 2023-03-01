# responsible: michal.jastrzebski@globallogic.com
# location: Wroclaw
# TC0095294.001

import unicorn
from core.basetest import BaseTest
from dstl.configuration.set_alarm import dstl_set_alarm_time
from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from dstl.configuration.set_autoattach import dstl_disable_ps_autoattach
from dstl.configuration.set_autoattach import dstl_enable_ps_autoattach
from dstl.configuration import shutdown_smso
from dstl.configuration.functionality_modes import dstl_set_minimum_functionality_mode
from dstl.configuration.functionality_modes import dstl_set_airplane_mode
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode


class Test(BaseTest):
    """Check configuration possibilites of AT+CALA command.

    1. Set time via eg. AT+CLCK=""70/01/01,00:36:14+00"
    2. Set alarm time with chosen text. For alarm trigger use future time, as reference time use current module time.
    3. Set cfun on minimum functionality mode via AT+CFUN=0
    4. Switch off module via AT^SMSO and wait when module turns on and alarm URC appear.
    5. Check cfun status via AT+CFUN?
    6. Set alarm time with chosen text. For alarm trigger use future time, as reference time use current module time.
    7. Switch off module via AT^SMSO and wait when module turns on and alarm URC appear.
    8. Check cfun status via AT+CFUN?
    9. Set alarm time with chosen text. For alarm trigger use future time, as reference time use current module time.
    10. Set cfun on airplane mode via AT+CFUN=4
    11. Switch off module via AT^SMSO and wait when module turns on and alarm URC appear.
    12. Check cfun status via AT+CFUN?
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.dut.dstl_disable_ps_autoattach()

    def run(test):
       test.log.step("1. Set time via eg. AT+CLCK='70/01/01,00:36:14+00'.")
       test.expect(test.dut.dstl_set_real_time_clock(time="21/05/05,00:00:00"))

       test.log.step("2. Set alarm time with chosen text."
                     "For alarm trigger use future time, as reference time use current module time.")
       test.expect(test.dut.dstl_set_alarm_time(time="21/05/05,00:00:59",text="ALARM1"))

       test.log.step("3. Set cfun on minimum functionality mode via AT+CFUN=0")
       test.expect(test.dut.dstl_set_minimum_functionality_mode())

       test.log.step("4. Switch off module via AT^SMSO and wait when module turns on and alarm URC appear.")
       test.expect(test.dut.dstl_shutdown_smso())
       test.expect(test.dut.dstl_wait_for_alarm(text="ALARM1",wait_time=120))

       test.log.step("5. Check cfun status via AT+CFUN?")
       test.expect(test.dut.dstl_is_device_in_full_functionality_mode())

       test.log.step("6. Set alarm time with chosen text. "
                     "For alarm trigger use future time, as reference time use current module time.")
       test.expect(test.dut.dstl_set_alarm_time(time="21/05/05,00:02:39", text="ALARM2"))

       test.log.step("7. Switch off module via AT^SMSO and wait when module turns on and alarm URC appear.")
       test.expect(test.dut.dstl_shutdown_smso())
       test.expect(test.dut.dstl_wait_for_alarm(text="ALARM2",wait_time=120))

       test.log.step("8. Check cfun status via AT+CFUN?")
       test.expect(test.dut.dstl_is_device_in_full_functionality_mode())

       test.log.step("9. Set alarm time with chosen text. "
                     "For alarm trigger use future time, as reference time use current module time.")
       test.expect(test.dut.dstl_set_alarm_time(time="21/05/05,00:03:51", text="ALARM3"))

       test.log.step("10. Set cfun on airplane mode via AT+CFUN=4")
       test.expect(test.dut.dstl_set_airplane_mode())

       test.log.step("11. Switch off module via AT^SMSO and wait when module turns on and alarm URC appear.")
       test.expect(test.dut.dstl_shutdown_smso())
       test.expect(test.dut.dstl_wait_for_alarm(text="ALARM3",wait_time=120))

       test.log.step("12. Check cfun status via AT+CFUN?")
       test.expect(test.dut.dstl_is_device_in_full_functionality_mode())

    def cleanup(test):
       test.expect(test.dut.dstl_set_real_time_clock())
       test.dut.dstl_enable_ps_autoattach()

if "__main__" == __name__:
    unicorn.main()





