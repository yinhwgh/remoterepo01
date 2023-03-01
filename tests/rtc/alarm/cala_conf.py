# responsible: michal.jastrzebski@globallogic.com
# location: Wroclaw
# TC0095294.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from dstl.configuration.set_autoattach import dstl_disable_ps_autoattach
from dstl.configuration.set_autoattach import dstl_enable_ps_autoattach

class Test(BaseTest):
    """
    Check configuration possibilites of AT+CALA command.

    1. Try to set alarm only with 'time' parameter. Clear alarm.
    2. Try to set alarm with 'time' and 'type' parameters. Clear alarm.
    3. Try to set alarm with 'time' and 'text' parameters. Clear alarm.
    4. Try to set all available alarms with 'time' and 'n' parameters.
    Clear all alarms.
    5. Try to set all available alarms with 'time', 'n' and 'text' parameters.
    Clear all alarms.
    6. Try to set all available alarms with 'time', 'n' and 'type' parameters.
    Clear all alarms.
    7. Try to set all available alarms with 'time', 'n', 'type', 'text' parameters.
    Clear all alarms.
    8. Try to set all available alarms with 16 characters long text.
    Clear all alarms.
    9. Try to set all available alarms with 'time', 'n' and 'text' parameters.
    Wait for all alarms.
    10. Try to set all available alarms with 'time', 'n' and 'text' parameters.
    Try to override all alarms with new data.
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.dut.dstl_disable_ps_autoattach()
        test.expect(test.dut.dstl_set_real_time_clock(time="21/10/10,00:00:00"))

    def run(test):

        test.log.step("1. Try to set alarm only with 'time' parameter. Clear alarm.")
        test.expect(test.dut.at1.send_and_verify('AT+CALA="21/10/10,00:03:00"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CALA=""', 'OK'))

        test.log.step("2. Try to set alarm with 'time' and 'type' parameters. Clear alarm.")
        test.expect(test.dut.at1.send_and_verify('AT+CALA="21/10/10,00:03:00",,0', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CALA="",,0', 'OK'))

        test.log.step("3. Try to set alarm with 'time' and 'text' parameters. Clear alarm.")
        test.expect(test.dut.at1.send_and_verify('AT+CALA="21/10/10,00:03:00",0,,"TEXT1"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CALA="",0,,""', 'OK'))

        test.log.step("4. Try to set all available alarms with 'time' and 'n' parameters."
                      "Clear all alarms.")
        set_time_n(test)
        clear_all_alarms(test)

        test.log.step("5. Try to set all available alarms with 'time', 'n' and 'text' parameters."
                      "Clear all alarms.")
        set_time_n_text(test)
        clear_all_alarms(test)

        test.log.step("6. Try to set all available alarms with 'time', 'n' and 'type' parameters."
                      "Clear all alarms.")
        set_time_n_type(test)
        clear_all_alarms(test)

        test.log.step("7. Try to set all available alarms with 'time', 'n', 'type', 'text' parameters."
                      " Clear all alarms.")
        set_time_n_type_text(test)
        clear_all_alarms(test)

        test.log.step("8. Try to set all available alarms with 16 characters long text."
                      "Clear all alarms.")
        set_max_lenght_text(test)
        clear_all_alarms(test)

        test.log.step("9. Try to set all available alarms with 'time', 'n' and 'text' parameters."
                      "Wait for all alarms.")
        set_time_n_text_and_wait(test)

        test.log.step("10. Try to set all available alarms with 'time','n' and 'text' parameters."
                      "Try to override all alarms with new data.")
        test.expect(test.dut.dstl_set_real_time_clock(time="21/10/10,00:00:00"))
        set_time_n_text(test)
        set_new_time_n_text(test)
        clear_all_alarms(test)

    def cleanup(test):
        clear_all_alarms(test)
        test.expect(test.dut.dstl_set_real_time_clock())
        test.dut.dstl_enable_ps_autoattach()

def set_time_n(test):
    times = ["00:03:00", "00:03:30", "00:04:00", "00:04:30", "00:05:00"]
    for n in range(5):
        test.expect(test.dut.at1.send_and_verify
                    ('AT+CALA="21/10/10,{}",{},,""'.format(times[n], n), 'OK'))
    test.expect(test.dut.at1.send_and_verify('AT+CALA?', 'OK'))
    buffer = test.dut.at1.last_response + test.dut.at1.read()
    for n in range(5):
        test.expect('{}",{}'.format(times[n],n)in buffer)
        

def set_time_n_text(test):
    times = ["00:03:00", "00:03:30", "00:04:00", "00:04:30", "00:05:00"]
    texts = ["TEXT1", "TEXT2", "TEXT3", "TEXT4","TEXT5"]
    for n in range(5):
        test.expect(test.dut.at1.send_and_verify
                    ('AT+CALA="21/10/10,{}",{},,{}'.format(times[n], n, texts[n]), 'OK'))
    test.expect(test.dut.at1.send_and_verify('AT+CALA?', 'OK'))
    buffer = test.dut.at1.last_response + test.dut.at1.read()
    for n in range(5):
        test.expect('{}",{},0,"{}"'.format(times[n],n,texts[n])in buffer)


def set_time_n_text_and_wait(test):
    times = ["00:03:00", "00:03:30", "00:04:00", "00:04:30", "00:05:00"]
    texts = ["TEXT1", "TEXT2", "TEXT3", "TEXT4","TEXT5"]
    for n in range(5):
        test.expect(test.dut.at1.send_and_verify
                    ('AT+CALA="21/10/10,{}",{},,{}'.format(times[n], n, texts[n]), 'OK'))
    test.sleep(360)
    buffer = test.dut.at1.last_response + test.dut.at1.read()
    for n in range(5):
        test.expect('{}'.format(texts[n]) in buffer)

def set_time_n_type(test):
    times = ["00:03:00", "00:03:30", "00:04:00", "00:04:30", "00:05:00"]
    for n in range(5):
        test.expect(test.dut.at1.send_and_verify
                    ('AT+CALA="21/10/10,{}",{},0,""'.format(times[n], n), 'OK'))
    test.expect(test.dut.at1.send_and_verify('AT+CALA?', 'OK'))
    buffer = test.dut.at1.last_response + test.dut.at1.read()
    for n in range(5):
        test.expect('{}",{},0,""'.format(times[n],n) in buffer)


def set_time_n_type_text(test):
    times = ["00:03:00", "00:03:30", "00:04:00", "00:04:30", "00:05:00"]
    texts = ["TEXT1", "TEXT2", "TEXT3", "TEXT4", "TEXT5"]
    for n in range(5):
        test.expect(test.dut.at1.send_and_verify
                    ('AT+CALA="21/10/10,{}",{},0,{}'.format(times[n], n, texts[n]), 'OK'))
    test.expect(test.dut.at1.send_and_verify('AT+CALA?', 'OK'))
    buffer = test.dut.at1.last_response + test.dut.at1.read()
    for n in range(5):
        test.expect('{}",{},0,"{}"'.format(times[n], n, texts[n]) in buffer)


def set_max_lenght_text(test):
    times = ["00:03:00", "00:03:30", "00:04:00", "00:04:30", "00:05:00"]
    for n in range(5):
        test.expect(test.dut.at1.send_and_verify
                    ('AT+CALA="21/10/10,{}",{},0,"0123456789ABCDF"'.format(times[n], n),'OK'))
    test.expect(test.dut.at1.send_and_verify('AT+CALA?', 'OK'))
    buffer = test.dut.at1.last_response + test.dut.at1.read()
    for n in range(5):
        test.expect('{}",{},0,"0123456789ABCDF"'.format(times[n], n) in buffer)


def clear_all_alarms(test):
    for n in range(5):
        test.expect(test.dut.at1.send_and_verify('AT+CALA="",{},0,""'.format(n), 'OK'))

def set_new_time_n_text(test):
    new_times = ["00:04:00", "00:04:30", "00:05:00", "00:05:30", "00:06:00"]
    texts = ["new_TEXT1", "new_TEXT2", "new_TEXT3", "new_TEXT4", "new_TEXT5"]
    for n in range(5):
        test.expect(test.dut.at1.send_and_verify
                    ('AT+CALA="21/10/10,{}",{},,"{}"'.format(new_times[n], n, texts[n]),'OK'))
    test.expect(test.dut.at1.send_and_verify('AT+CALA?', 'OK'))
    buffer = test.dut.at1.last_response + test.dut.at1.read()
    for n in range(5):
        test.expect('{}",{},0,"{}"'.format(new_times[n], n, texts[n]) in buffer)


if "__main__" == __name__:
    unicorn.main()
