# responsible: michal.jastrzebski@globallogic.com
# location: Wroclaw
# TC0095295.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from dstl.configuration.set_autoattach import dstl_disable_ps_autoattach
from dstl.configuration.set_autoattach import dstl_enable_ps_autoattach
from dstl.configuration.set_alarm import dstl_set_alarm_time
from dstl.configuration.set_alarm import dstl_clear_alarm
from dstl.hardware.set_real_time_clock import check_cclk_type
from dstl.auxiliary.restart_module import dstl_restart
from dstl.configuration.shutdown_smso import dstl_shutdown_smso


class Test(BaseTest):
    """
    Verify alarm functionality in long time with different cases..

    1. Set all alarms time with text. For alarm triggers use random time.
    When all alarms are set restart module with AT+CFUN=1,1.
    a) after module turns on and alarm URC appear restart module with AT+CFUN=1,1
    b) repeat step a) until last alarm URC occurrence
    2. Set all alarms time with text. For alarm triggers use random time.
    When all alarms are set shut down module with AT^SMSO.
    a) after module turns on and alarm URC appear turn off module with AT^SMSO
    b) repeat step a) until last alarm URC occurrence
    3. Repeat above described steps for 2 hours ( ~ 16 repetitions).
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.dut.dstl_disable_ps_autoattach()

    def run(test):
        test.log.info("Repeat above described steps for 2 hours ( ~ 16 repetitions).")
        for iteration in range(16):
            test.log.info(" ITERATION {}/16".format(iteration + 1))
            test.log.step("1.Set all alarms time with text. For alarm triggers use random time."
                      "When all alarms are set restart module with AT+CFUN=1,1.")
            test.expect(test.dut.dstl_set_real_time_clock(time="22/08/10,10:00:00"))
            test.expect(test.dut.dstl_set_alarm_time(time="22/08/10,10:01:11",index="0", text="ALARM1"))
            test.expect(test.dut.dstl_set_alarm_time(time="22/08/10,10:01:34",index="1", text="ALARM2"))
            test.expect(test.dut.dstl_set_alarm_time(time="22/08/10,10:02:45",index="2", text="ALARM3"))
            test.expect(test.dut.dstl_set_alarm_time(time="22/08/10,10:03:38",index="3", text="ALARM4"))
            test.expect(test.dut.dstl_set_alarm_time(time="22/08/10,10:04:27",index="4", text="ALARM5"))
            test.expect(test.dut.dstl_read_current_alarm())
            test.expect(test.dut.dstl_restart())

            test.log.step("a) after module turns on and alarm URC appear turn off module with AT+CFUN=1,1")
            restart_alarm(test)

            test.log.step("2. Set all alarms time with text. For alarm triggers use random time."
                            "When all alarms are set shut down module with AT^SMSO.")

            test.expect(test.dut.dstl_clear_alarm())
            test.expect(test.dut.dstl_set_real_time_clock(time="21/09/01,08:02:50"))
            test.expect(test.dut.dstl_set_alarm_time(time="21/09/01,08:03:13", index="0", text="NEW_ALARM_1"))
            test.expect(test.dut.dstl_set_alarm_time(time="21/09/01,08:03:43", index="1", text="NEW_ALARM_2"))
            test.expect(test.dut.dstl_set_alarm_time(time="21/09/01,08:04:07", index="2", text="NEW_ALARM_3"))
            test.expect(test.dut.dstl_set_alarm_time(time="21/09/01,08:05:22", index="3", text="NEW_ALARM_4"))
            test.expect(test.dut.dstl_set_alarm_time(time="21/09/01,08:06:29", index="4", text="NEW_ALARM_5"))
            test.expect(test.dut.dstl_read_current_alarm())
            test.expect(test.dut.dstl_shutdown_smso())

            test.log.step("a) after module turns on and alarm URC appear turn off module with AT^SMSO")
            switch_off_alarm(test)

            test.log.step("3. Repeat above described steps for 2 hours ( ~ 15 repetitions).")

    def cleanup(test):
        test.expect(test.dut.dstl_set_real_time_clock())
        test.dut.dstl_enable_ps_autoattach()

def restart_alarm(test):
        test.expect(test.dut.dstl_wait_for_alarm(text="ALARM1", wait_time=600))
        test.log.step("b) repeat step a) until last alarm URC occurrence")
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_wait_for_alarm(text="ALARM2", wait_time=600))
        test.log.step("b) repeat step a) until last alarm URC occurrence")
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_wait_for_alarm(text="ALARM3", wait_time=600))
        test.log.step("b) repeat step a) until last alarm URC occurrence")
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_wait_for_alarm(text="ALARM4", wait_time=600))
        test.log.step("b) repeat step a) until last alarm URC occurrence")
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_wait_for_alarm(text="ALARM5", wait_time=600))

def switch_off_alarm(test):
        test.expect(test.dut.dstl_wait_for_alarm(text="NEW_ALARM_1",wait_time=600))
        test.log.step("b) repeat step a) until last alarm URC occurrence")
        test.expect(test.dut.dstl_shutdown_smso())
        test.expect(test.dut.dstl_wait_for_alarm(text="NEW_ALARM_2",wait_time=600))
        test.log.step("b) repeat step a) until last alarm URC occurrence")
        test.expect(test.dut.dstl_shutdown_smso())
        test.expect(test.dut.dstl_wait_for_alarm(text="NEW_ALARM_3",wait_time=600))
        test.log.step("b) repeat step a) until last alarm URC occurrence")
        test.expect(test.dut.dstl_shutdown_smso())
        test.expect(test.dut.dstl_wait_for_alarm(text="NEW_ALARM_4",wait_time=600))
        test.log.step("b) repeat step a) until last alarm URC occurrence")
        test.expect(test.dut.dstl_shutdown_smso())
        test.expect(test.dut.dstl_wait_for_alarm(text="NEW_ALARM_5",wait_time=600))


if "__main__" == __name__:
    unicorn.main()
