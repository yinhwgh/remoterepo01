# responsible: mariusz.wojcik@globallogic.com
# location: Wroclaw
# TC0095123.001

import unicorn
from threading import Thread
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei


class Test(BaseTest):
    """
    Check behavior of MUX channels after multiple open and close of them.

    1. Open 2 MUX channels (which supports sending AT commands).
    2. Send few random commands via every opened channel.
    3. Close previously opened MUX channels.
    Repeat steps 1-3 100 times.
    4. Open and close both (previously chosen) MUX channels 100 times.
    5. Repeat steps 1-3.
    6. If possible at the same time open and close each MUX channel 100 times.
    7. Repeat steps 1-3.
    """

    STEP_ITERATIONS = 100

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()

    def run(test):
        test.dut.at1.close()
        test.sleep(5)
        test.log.info("REPEAT STEPS 1-3 {} TIMES.".format(test.STEP_ITERATIONS))
        for loop in range(test.STEP_ITERATIONS):
            info = "ITERATION: {0}/{1}".format(loop + 1, test.STEP_ITERATIONS)
            execute_steps_1_3(test, info)

        test.log.step("4. Open and close both (previously chosen) MUX channels {} times.".format(test.STEP_ITERATIONS))
        for loop in range(test.STEP_ITERATIONS):
            test.log.info("STEP 4 ITERATION: {0}/{1}".format(loop + 1, test.STEP_ITERATIONS))
            open_channels(test)
            close_channels(test)

        test.log.step("5. Repeat steps 1-3.")
        execute_steps_1_3(test, "REPEATING STEPS 1-3 FOR STEP 5")

        test.log.step("6. If possible at the same time open and close each MUX channel {} times.".format(test.STEP_ITERATIONS))
        open_and_close_channels_simultaneously(test)

        test.log.step("7. Repeat steps 1-3.")
        execute_steps_1_3(test, "REPEATING STEPS 1-3 FOR STEP 7")

    def cleanup(test):
        close_channels(test)


def execute_steps_1_3(test, info):
    test.log.info(info)
    test.log.step("1. Open 2 MUX channels (which supports sending AT commands).")
    open_channels(test)

    test.log.info(info)
    test.log.step("2. Send few random commands via every opened channel.")
    send_commands(test, test.dut.mux_1)
    send_commands(test, test.dut.mux_2)

    test.log.info(info)
    test.log.step("3. Close previously opened MUX channels.")
    close_channels(test)


def open_channels(test):
    test.dut.mux_1.open()
    test.dut.mux_2.open()
    test.sleep(5)


def close_channels(test):
    test.dut.mux_1.close()
    test.dut.mux_2.close()
    test.sleep(5)


def open_and_close_channel_for_thread(test, device):
    for loop in range(test.STEP_ITERATIONS):
        test.log.info("ITERATION {0}/{1} FOR {2}".format(loop + 1, test.STEP_ITERATIONS, device.name))
        device.open()
        test.sleep(5)
        device.close()
        test.sleep(5)


def send_commands(test, device):
    test.expect(device.send_and_verify("AT", ".*OK.*"))
    test.expect(device.send_and_verify("ATI", ".*OK.*"))
    test.expect(device.send_and_verify("AT^SCFG?", ".*OK.*"))


def open_and_close_channels_simultaneously(test):
    thread_mux_1 = test.thread(open_and_close_channel_for_thread, test, test.dut.mux_1)
    thread_mux_2 = test.thread(open_and_close_channel_for_thread, test, test.dut.mux_2)
    thread_mux_1.join()
    thread_mux_2.join()


if "__main__" == __name__:
    unicorn.main()
