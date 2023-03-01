# responsible: michal.jastrzebski@globallogic.com
# location: Wroclaw
# TC0095296.003

import unicorn
import re
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei
from dstl.configuration import shutdown_smso
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from dstl.configuration.set_alarm import dstl_set_alarm_time
from dstl.configuration.set_alarm import dstl_clear_alarm



class Test(BaseTest):
    """
    Check configuration possibilites of AT+CALA command.

    1. Set alarm time with chosen text and wait for all alarm URCs.
    For each alarm triggers use random
	time, as reference time use current module time.
    2. Set alarm time with text. For alarm triggers use random time,
    as reference time use current module time.
    3. When all alarms are set shut down module with AT^SMSO.
    4. After module turns on and alarm URC appear turn off module with AT^SMSO.
    Repeat step 4 until last alarm URC occurrence
    5. Repeat above described steps 10 times.
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()

    def run(test):
        test.log.info("Repeat above described steps 10 times.")
        for iteration in range(10):
            test.log.info(" ITERATION {}/10".format(iteration + 1))
            test.log.step("1. Set alarm time with chosen text and wait for all alarm URCs. "
                    "For each alarm trigge use random time, as reference time use current module time.")
            test.expect(test.dut.dstl_set_real_time_clock(time="21/10/10,00:00:00"))
            set_time_n_text_and_wait(test)
            test.expect(test.dut.dstl_clear_alarm())

            test.log.step("2. Set alarm time with text. "
                "For alarm triggers use random time, as reference time use current module time.")
            test.expect(test.dut.dstl_set_real_time_clock(time="21/11/11,00:06:00"))
            set_alarms(test)

            test.log.step("3. When all alarms are set shut down module with AT^SMSO.")
            test.expect(test.dut.dstl_shutdown_smso())

            test.log.step("4. After module turns on and alarm URC appear turn off module with AT^SMSO."
                          "Repeat step 4 until last alarm URC occurrence")
            test.expect(test.dut.dstl_wait_for_alarm(text="NEW_ALARM1",wait_time=610))
            test.expect(test.dut.dstl_shutdown_smso())
            test.expect(test.dut.dstl_wait_for_alarm(text="NEW_ALARM2",wait_time=610))
            test.expect(test.dut.dstl_shutdown_smso())
            test.expect(test.dut.dstl_wait_for_alarm(text="NEW_ALARM3",wait_time=610))
            test.expect(test.dut.dstl_shutdown_smso())
            test.expect(test.dut.dstl_wait_for_alarm(text="NEW_ALARM4",wait_time=610))
            test.expect(test.dut.dstl_shutdown_smso())
            test.expect(test.dut.dstl_wait_for_alarm(text="NEW_ALARM5",wait_time=610))

            test.log.step("5. Repeat above described steps 10 times.")


def cleanup(test):
    clear_all_alarms(test)

def set_time_n_text_and_wait(test):
    test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:01:47", index="0", text="ALARM1"))
    test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:03:21", index="1", text="ALARM2"))
    test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:04:56", index="2", text="ALARM3"))
    test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:05:19", index="3", text="ALARM4"))
    test.expect(test.dut.dstl_set_alarm_time(time="21/10/10,00:06:31", index="4", text="ALARM5"))
    test.expect(test.dut.dstl_read_current_alarm())
    test.expect(test.dut.dstl_wait_for_alarm(text="ALARM1",wait_time=360))
    test.expect(test.dut.dstl_wait_for_alarm(text="ALARM2",wait_time=360))
    test.expect(test.dut.dstl_wait_for_alarm(text="ALARM3",wait_time=360))
    test.expect(test.dut.dstl_wait_for_alarm(text="ALARM4",wait_time=360))
    test.expect(test.dut.dstl_wait_for_alarm(text="ALARM5",wait_time=360))


def set_alarms(test):
    test.expect(test.dut.dstl_set_alarm_time(time="21/11/11,00:06:29", index="0", text="NEW_ALARM1"))
    test.expect(test.dut.dstl_set_alarm_time(time="21/11/11,00:07:34", index="1", text="NEW_ALARM2"))
    test.expect(test.dut.dstl_set_alarm_time(time="21/11/11,00:08:50", index="2", text="NEW_ALARM3"))
    test.expect(test.dut.dstl_set_alarm_time(time="21/11/11,00:09:21", index="3", text="NEW_ALARM4"))
    test.expect(test.dut.dstl_set_alarm_time(time="21/11/11,00:10:01", index="4", text="NEW_ALARM5"))


if "__main__" == __name__:
    unicorn.main()
