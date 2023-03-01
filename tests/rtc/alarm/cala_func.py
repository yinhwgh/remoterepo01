# responsible: michal.jastrzebski@globallogic.com
# location: Wroclaw
# TC0010688.001

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
    Verify alarm functionality in different cases.

    1. Set alarm time with chosen text and wait for all alarm URCs.
    For each alarm triggers use random time, as reference time use current module time.
    2. Set alarm time without text and wait for all alarm URCs.
    For each alarm triggers use random times, as reference time use current module time.
    Previously entered text should be preserved.
    3. Set alarm time with text. For alarm triggers use random time, as reference time use current module time.
     When all alarms are set shut down module with AT^SMSO.
    a) after module turns on and alarm URC appear turn off module with AT^SMSO
    b) repeat step a) until last alarm URC occurrence
    4. Set alarm time with text. For alarm triggers use random time, as reference time use current module time.
    When all alarms are set restart module with AT+CFUN=1,1.
    a) after module turns on and alarm URC appear restart module with AT+CFUN=1,1
    b) repeat step a) until last alarm URC occurrence
    5. Set all alarms time same and with different text. Wait for all URCs.
    6. Set all alarms with chosen time and text. Set module clock after the latest alarm.
    7. Try to set every alarm time before current module time.
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.dut.dstl_disable_ps_autoattach()
        test.expect(test.dut.dstl_set_real_time_clock(time="21/10/10,00:00:00"))

    def run(test):
        test.log.step("1.Set alarm time with chosen text and wait for all alarm URCs."
                      "For each alarm triggers use random time, as reference time use current module time.")
        test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:01:11",index="0", text="ALARM1"))
        test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:01:34",index="1", text="ALARM2"))
        test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:02:45",index="2", text="ALARM3"))
        test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:03:38",index="3", text="ALARM4"))
        test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:04:27",index="4", text="ALARM5"))
        wait_for_alarms(test)

        test.log.step("2. Set alarm time without text and wait for all alarm URCs. "
                      "For each alarm triggers use random times, as reference time use current module time."
                      "Previously entered text should be preserved.")
        test.expect(test.dut.dstl_clear_alarm())
        test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:04:54", index="0"))
        test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:05:49", index="1"))
        test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:07:10", index="2"))
        test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:08:00", index="3"))
        test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:09:21", index="4"))
        test.expect(test.dut.dstl_read_current_alarm())
        wait_for_alarms(test)

        test.log.step("3. Set alarm time with text. For alarm triggers use random time, "
                      "as reference time use current module time."
                      "When all alarms are set shut down module with AT^SMSO.")

        test.expect(test.dut.dstl_clear_alarm())
        test.expect(test.dut.dstl_set_real_time_clock(time="21/10/10,00:02:50"))
        test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:03:13", index="0", text="ALARM1"))
        test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:03:43", index="1", text="ALARM2"))
        test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:04:07", index="2", text="ALARM3"))
        test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:05:22", index="3", text="ALARM4"))
        test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:06:29", index="4", text="ALARM5"))
        test.expect(test.dut.dstl_read_current_alarm())
        test.expect(test.dut.dstl_shutdown_smso())

        test.log.step("a) after module turns on and alarm URC appear turn off module with AT^SMSO")
        switch_off_alarm(test)

        test.log.step("4. Set alarm time with text. "
                      "For alarm triggers use random time, as reference time use current module time. "
                      "When all alarms are set restart module with AT+CFUN=1,1.")
        test.expect(test.dut.dstl_clear_alarm())
        test.expect(test.dut.dstl_set_real_time_clock(time="21/10/10,00:06:50"))
        test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:07:17", index="0", text="ALARM1"))
        test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:08:54", index="1", text="ALARM2"))
        test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:09:41", index="2", text="ALARM3"))
        test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:10:38", index="3", text="ALARM4"))
        test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:11:20", index="4", text="ALARM5"))
        test.expect(test.dut.dstl_restart())

        test.log.step("a) after module turns on and alarm URC appear restart module with AT+CFUN=1,1")
        restart_alarm(test)

        test.log.step("5. Set all alarms time same and with different text. Wait for all URCs.")
        test.expect(test.dut.dstl_clear_alarm())
        test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:12:12", index="0", text="NEW_ALARM_1"))
        test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:12:12", index="1", text="NEW_ALARM_2"))
        test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:12:12", index="2", text="NEW_ALARM_3"))
        test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:12:12", index="3", text="NEW_ALARM_4"))
        test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:12:12", index="4", text="NEW_ALARM_5"))
        test.sleep(60)
        buffer = test.dut.at1.read()
        test.expect("NEW_ALARM_1" in buffer and "NEW_ALARM_2" in buffer and
                    "NEW_ALARM_3" in buffer and "NEW_ALARM_4" in buffer and "NEW_ALARM_5" in buffer)

        test.log.step("6. Set all alarms with chosen time and text. Set module clock after the latest alarm.")
        test.expect(test.dut.dstl_clear_alarm())
        test.expect(test.dut.dstl_set_real_time_clock(time="21/10/10,00:11:10"))
        test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:11:20", index="0", text="A_ALARM_1"))
        test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:11:30", index="1", text="B_ALARM_2"))
        test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:11:40", index="2", text="C_ALARM_3"))
        test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:11:50", index="3", text="D_ALARM_4"))
        test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:12:00", index="4", text="E_ALARM_5"))
        test.expect(test.dut.dstl_set_real_time_clock(time="21/10/10,00:12:10"))
        test.sleep(15)
        buffer = test.dut.at1.read()
        test.expect("A_ALARM_1" in buffer and "B_ALARM_2" in buffer and
                    "C_ALARM_3" in buffer and "D_ALARM_4" in buffer and "E_ALARM_5" in buffer)

        test.log.step("7. Try to set every alarm time before current module time.")
        test.log.step("This step isn't perform on QCT products")

    def cleanup(test):
        test.expect(test.dut.dstl_set_real_time_clock())
        test.dut.dstl_enable_ps_autoattach()

def wait_for_alarms(test):
    test.expect(test.dut.dstl_wait_for_alarm(text="ALARM1",wait_time=600))
    test.expect(test.dut.dstl_wait_for_alarm(text="ALARM2",wait_time=600))
    test.expect(test.dut.dstl_wait_for_alarm(text="ALARM3",wait_time=600))
    test.expect(test.dut.dstl_wait_for_alarm(text="ALARM4",wait_time=600))
    test.expect(test.dut.dstl_wait_for_alarm(text="ALARM5",wait_time=600))

def switch_off_alarm(test):
        test.expect(test.dut.dstl_wait_for_alarm(text="ALARM1",wait_time=600))
        test.log.step("b) repeat step a) until last alarm URC occurrence")
        test.expect(test.dut.dstl_shutdown_smso())
        test.expect(test.dut.dstl_wait_for_alarm(text="ALARM2",wait_time=600))
        test.log.step("b) repeat step a) until last alarm URC occurrence")
        test.expect(test.dut.dstl_shutdown_smso())
        test.expect(test.dut.dstl_wait_for_alarm(text="ALARM3",wait_time=600))
        test.log.step("b) repeat step a) until last alarm URC occurrence")
        test.expect(test.dut.dstl_shutdown_smso())
        test.expect(test.dut.dstl_wait_for_alarm(text="ALARM4",wait_time=600))
        test.log.step("b) repeat step a) until last alarm URC occurrence")
        test.expect(test.dut.dstl_shutdown_smso())
        test.expect(test.dut.dstl_wait_for_alarm(text="ALARM5",wait_time=600))

def restart_alarm(test):
        test.expect(test.dut.dstl_wait_for_alarm(text="ALARM1",wait_time=600))
        test.log.step("b) repeat step a) until last alarm URC occurrence")
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_wait_for_alarm(text="ALARM2",wait_time=600))
        test.log.step("b) repeat step a) until last alarm URC occurrence")
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_wait_for_alarm(text="ALARM3",wait_time=600))
        test.log.step("b) repeat step a) until last alarm URC occurrence")
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_wait_for_alarm(text="ALARM4",wait_time=600))
        test.log.step("b) repeat step a) until last alarm URC occurrence")
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_wait_for_alarm(text="ALARM5",wait_time=600))


if "__main__" == __name__:
    unicorn.main()
