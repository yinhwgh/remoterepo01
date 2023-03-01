# responsible: michal.jastrzebski@globallogic.com
# location: Wroclaw
# TC0107296.001

import unicorn
from core.basetest import BaseTest
from dstl.identification import check_identification_ati
from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei


class Test(BaseTest):
    """
    Check behavior of MUX channels after multiple open and close of them.

    1. Open 2 MUX channels (which supports sending AT commands).
    2. Send few random commands via every opened channel.
    3. Close previously opened MUX channels.
    4. Repeat steps 1-3 100 times.
    5. Open and close both (previously chosen) MUX channels 100 times.
    6. Repeat steps 1-3.
    7. If possible at the same time open and close each MUX channel 100 times.
    8. Repeat steps 1-3.
    """

    ITERATIONS = 100

    def setup(test):
        test.expect("x86_64" in test.os.execute('lscpu'), critical=True)
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()

    def run(test):
        test.dut.at1.close()
        test.sleep(5)
        test.log.info("Repeat steps 1-3 {} times.".format(test.ITERATIONS))
        for loop in range(test.ITERATIONS):
            info = "ITERATION: {0}/{1}".format(loop + 1, test.ITERATIONS)
            execute_steps_1_3(test, info)

        test.log.step("5. Open and close both (previously chosen) MUX channels {} times.".format(test.ITERATIONS))
        for loop in range(test.ITERATIONS):
            test.log.info("Step 4 iteration: {0}/{1}".format(loop + 1, test.ITERATIONS))
            open_channels(test)
            close_channels(test)

        test.log.step("5. Repeat steps 1-3.")
        execute_steps_1_3(test, "Repeating steps 1-3 for step 5")

        test.log.step("6. If possible at the same time open and close each MUX channel {} times.".format(test.ITERATIONS))
        open_and_close_channels_simultaneously(test)

        test.log.step("7. Repeat steps 1-3.")
        execute_steps_1_3(test, "Repeating steps 1-3 for step 7")

    def cleanup(test):
        close_channels(test)


def execute_steps_1_3(test, info):
    test.log.info(info)
    test.log.step("1. Open 2 MUX channels (which supports sending AT commands).")
    open_channels(test)

    test.log.info(info)
    test.log.step("2. Send few random commands via every opened channel.")
    test.dut.at1 = test.dut.mux_1
    test.expect(test.dut.dstl_detect())
    test.dut.at1 = test.dut.mux_2
    test.expect(test.dut.dstl_detect())

    test.log.info(info)
    test.log.step("3. Close previously opened MUX channels.")
    close_channels(test)

    test.log.step("4. Repeat steps 1-3 100 times.")

def open_channels(test):
    test.dut.mux_1.open()
    test.dut.mux_2.open()
    test.sleep(5)


def close_channels(test):
    test.dut.mux_1.close()
    test.dut.mux_2.close()
    test.sleep(5)


def open_and_close_channel_for_thread(test):
    for loop in range(test.ITERATIONS):
        test.log.info("ITERATION {0}/{1} FOR {2}".format(loop + 1, test.ITERATIONS, device.name))
        device.open()
        test.sleep(5)
        device.close()
        test.sleep(5)

def open_and_close_channels_simultaneously(test):
    thread_mux_1 = test.thread(open_and_close_channel_for_thread, test, test.dut.mux_1)
    thread_mux_2 = test.thread(open_and_close_channel_for_thread, test, test.dut.mux_2)
    thread_mux_1.join()
    thread_mux_2.join()


if "__main__" == __name__:
    unicorn.main()
