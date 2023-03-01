#responsible: michal.jastrzebski@globallogic.com. mariusz.wojcik@globallogic.com
#location: Wroclaw
#TC0010689.001

import unicorn
import datetime
import random
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from dstl.auxiliary.devboard import devboard
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
    Verify basic functionality of RTC (real time clock).

    --- getting time from network is disabled ---
    1. Set random valid date and time.
    2. Check time.
    3. Wait 30 s.
    4. Check time.
    5. Restart module.
    6. Check time.
    7. Cut off power for 1 minute.
    8. Switch on.
    9. Check time.
    10. Set actual time.
    11. Wait 3 minutes.
    12. Check time.
    13. Set random valid date and time.
    14. (if available) Disable automatic time update via NITZ.
    15. (if available) Try to get time from network- enter pin and wait 2 min.
    16. Check time.
    Repeat steps 1 to 16 10 times.

    --- getting time from network is enabled ---
    17. Set random valid date and time.
    18. Check time.
    19. Wait 30 s.
    20. Check time.
    21. Restart module.
    22. Check time.
    23. Cut off power for 1 minute.
    24. Switch on.
    25. Check time.
    26. Set actual time.
    27. Wait 3 minutes.
    28. Check time.
    29. Set random valid date and time.
    30. (if available) Enable automatic time update via NITZ.
    31. (if available) Try to get time from network- enter pin and wait 2 min.
    32. Check time.
    Repeat steps 17 to 32 10 times.
    33. Set cross year date and time , ex: at+cclk="17/12/31,23:59:50"
    """

    def setup(test):
        test.TIME_TO_TURN_MODULE_ON = 30
        test.FACTORY_DATE = datetime.datetime(1980, 1, 6)
        test.NUMBER_OF_LOOPS = 10
        test.DATE_MARGIN_IN_SECONDS = 10
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()

    def run(test):
        test.log.step("REPEAT STEPS 1 TO 16 10 TIMES.")
        for steps_1_to_16_loop in range(test.NUMBER_OF_LOOPS):
            test.log.step("1. Set random valid date and time.")
            test.log.info("LOOP {0}/{1} FOR STEPS 1-16".format(steps_1_to_16_loop + 1, test.NUMBER_OF_LOOPS))
            random_date = prepare_random_date()
            test.expect(test.dut.dstl_set_real_time_clock(time=format_date(random_date)))

            test.log.step("2. Check time.")
            test.log.info("LOOP {0}/{1} FOR STEPS 1-16".format(steps_1_to_16_loop + 1, test.NUMBER_OF_LOOPS))
            check_time(test, random_date)

            test.log.step("3. Wait 30 s.")
            test.log.info("LOOP {0}/{1} FOR STEPS 1-16".format(steps_1_to_16_loop + 1, test.NUMBER_OF_LOOPS))
            test.sleep(30)

            test.log.step("4. Check time.")
            test.log.info("LOOP {0}/{1} FOR STEPS 1-16".format(steps_1_to_16_loop + 1, test.NUMBER_OF_LOOPS))
            date_after_wait = add_time_to_date(random_date, 30)
            check_time(test, date_after_wait)

            test.log.step("5. Restart module.")
            test.log.info("LOOP {0}/{1} FOR STEPS 1-16".format(steps_1_to_16_loop + 1, test.NUMBER_OF_LOOPS))
            # Restart this way is required to check time in step 6
            test.expect(test.dut.at1.send_and_verify("AT+CFUN=1,1", ".*OK.*"))
            test.sleep(test.TIME_TO_TURN_MODULE_ON)

            test.log.step("6. Check time.")
            test.log.info("LOOP {0}/{1} FOR STEPS 1-16".format(steps_1_to_16_loop + 1, test.NUMBER_OF_LOOPS))
            date_after_wait = add_time_to_date(date_after_wait, test.TIME_TO_TURN_MODULE_ON)
            check_time(test, date_after_wait)

            test.log.step("7. Cut off power for 1 minute.")
            test.log.info("LOOP {0}/{1} FOR STEPS 1-16".format(steps_1_to_16_loop + 1, test.NUMBER_OF_LOOPS))
            test.expect(test.dut.dstl_turn_off_vbatt_via_dev_board())
            test.sleep(60)

            test.log.step("8. Switch on.")
            test.log.info("LOOP {0}/{1} FOR STEPS 1-16".format(steps_1_to_16_loop + 1, test.NUMBER_OF_LOOPS))
            test.expect(test.dut.dstl_turn_on_vbatt_via_dev_board())
            test.expect(test.dut.dstl_turn_on_igt_via_dev_board())
            test.sleep(test.TIME_TO_TURN_MODULE_ON)

            test.log.step("9. Check time.")
            test.log.info("LOOP {0}/{1} FOR STEPS 1-16".format(steps_1_to_16_loop + 1, test.NUMBER_OF_LOOPS))
            date_after_wait = add_time_to_date(test.FACTORY_DATE, test.TIME_TO_TURN_MODULE_ON)
            check_time(test, date_after_wait)

            test.log.step("10. Set actual time.")
            test.log.info("LOOP {0}/{1} FOR STEPS 1-16".format(steps_1_to_16_loop + 1, test.NUMBER_OF_LOOPS))
            actual_date = datetime.datetime.now()
            test.expect(test.dut.dstl_set_real_time_clock(time=format_date(actual_date)))

            test.log.step("11. Wait 3 minutes.")
            test.log.info("LOOP {0}/{1} FOR STEPS 1-16".format(steps_1_to_16_loop + 1, test.NUMBER_OF_LOOPS))
            test.sleep(180)

            test.log.step("12. Check time.")
            test.log.info("LOOP {0}/{1} FOR STEPS 1-16".format(steps_1_to_16_loop + 1, test.NUMBER_OF_LOOPS))
            date_after_wait = add_time_to_date(actual_date, 180)
            check_time(test, date_after_wait)

            test.log.step("13. Set random valid date and time.")
            test.log.info("LOOP {0}/{1} FOR STEPS 1-16".format(steps_1_to_16_loop + 1, test.NUMBER_OF_LOOPS))
            random_date = prepare_random_date()
            test.expect(test.dut.dstl_set_real_time_clock(time=format_date(random_date)))

            test.log.step("14. (if available) Disable automatic time update via NITZ.")
            test.log.info("LOOP {0}/{1} FOR STEPS 1-16".format(steps_1_to_16_loop + 1, test.NUMBER_OF_LOOPS))
            test.expect(test.dut.at1.send_and_verify('AT+CTZU=0', '.*OK.*'))

            test.log.step("15. (if available) Try to get time from network- enter pin and wait 2 min.")
            test.log.info("LOOP {0}/{1} FOR STEPS 1-16".format(steps_1_to_16_loop + 1, test.NUMBER_OF_LOOPS))
            test.expect(test.dut.dstl_enter_pin(test.dut.sim))
            test.sleep(120)

            test.log.step("16. Check time.")
            test.log.info("LOOP {0}/{1} FOR STEPS 1-16".format(steps_1_to_16_loop + 1, test.NUMBER_OF_LOOPS))
            date_after_wait = add_time_to_date(random_date, 120)
            check_time(test, date_after_wait)

        test.log.step("REPEAT STEPS 17 TO 32 10 TIMES.")
        for steps_17_to_32_loop in range(test.NUMBER_OF_LOOPS):
            test.log.step("17. Set random valid date and time.")
            test.log.info("LOOP {0}/{1} FOR STEPS 17-32".format(steps_17_to_32_loop + 1, test.NUMBER_OF_LOOPS))
            random_date = prepare_random_date()
            test.expect(test.dut.dstl_set_real_time_clock(time=format_date(random_date)))

            test.log.step("18. Check time.")
            test.log.info("LOOP {0}/{1} FOR STEPS 17-32".format(steps_17_to_32_loop + 1, test.NUMBER_OF_LOOPS))
            check_time(test, random_date)

            test.log.step("19. Wait 30 s.")
            test.log.info("LOOP {0}/{1} FOR STEPS 17-32".format(steps_17_to_32_loop + 1, test.NUMBER_OF_LOOPS))
            test.sleep(30)

            test.log.step("20. Check time.")
            test.log.info("LOOP {0}/{1} FOR STEPS 17-32".format(steps_17_to_32_loop + 1, test.NUMBER_OF_LOOPS))
            date_after_wait = add_time_to_date(random_date, 30)
            check_time(test, date_after_wait)

            test.log.step("21. Restart module.")
            test.log.info("LOOP {0}/{1} FOR STEPS 17-32".format(steps_17_to_32_loop + 1, test.NUMBER_OF_LOOPS))
            # Restart this way is required to check time in step 22
            test.expect(test.dut.at1.send_and_verify("AT+CFUN=1,1", ".*OK.*"))
            test.sleep(test.TIME_TO_TURN_MODULE_ON)

            test.log.step("22. Check time.")
            test.log.info("LOOP {0}/{1} FOR STEPS 17-32".format(steps_17_to_32_loop + 1, test.NUMBER_OF_LOOPS))
            date_after_wait = add_time_to_date(date_after_wait, test.TIME_TO_TURN_MODULE_ON)
            check_time(test, date_after_wait)

            test.log.step("23. Cut off power for 1 minute.")
            test.log.info("LOOP {0}/{1} FOR STEPS 17-32".format(steps_17_to_32_loop + 1, test.NUMBER_OF_LOOPS))
            test.expect(test.dut.dstl_turn_off_vbatt_via_dev_board())
            test.sleep(60)

            test.log.step("24. Switch on.")
            test.log.info("LOOP {0}/{1} FOR STEPS 17-32".format(steps_17_to_32_loop + 1, test.NUMBER_OF_LOOPS))
            test.expect(test.dut.dstl_turn_on_vbatt_via_dev_board())
            test.expect(test.dut.dstl_turn_on_igt_via_dev_board())
            test.sleep(test.TIME_TO_TURN_MODULE_ON)

            test.log.step("25. Check time.")
            test.log.info("LOOP {0}/{1} FOR STEPS 17-32".format(steps_17_to_32_loop + 1, test.NUMBER_OF_LOOPS))
            date_after_wait = add_time_to_date(test.FACTORY_DATE, test.TIME_TO_TURN_MODULE_ON)
            check_time(test, date_after_wait)

            test.log.step("26. Set actual time.")
            test.log.info("LOOP {0}/{1} FOR STEPS 17-32".format(steps_17_to_32_loop + 1, test.NUMBER_OF_LOOPS))
            actual_date = datetime.datetime.now()
            test.expect(test.dut.dstl_set_real_time_clock(time=format_date(actual_date)))

            test.log.step("27. Wait 3 minutes.")
            test.log.info("LOOP {0}/{1} FOR STEPS 17-32".format(steps_17_to_32_loop + 1, test.NUMBER_OF_LOOPS))
            test.sleep(180)

            test.log.step("28. Check time.")
            test.log.info("LOOP {0}/{1} FOR STEPS 17-32".format(steps_17_to_32_loop + 1, test.NUMBER_OF_LOOPS))
            date_after_wait = add_time_to_date(actual_date, 180)
            check_time(test, date_after_wait)

            test.log.step("29. Set random valid date and time.")
            test.log.info("LOOP {0}/{1} FOR STEPS 17-32".format(steps_17_to_32_loop + 1, test.NUMBER_OF_LOOPS))
            random_date = prepare_random_date()
            test.expect(test.dut.dstl_set_real_time_clock(time=format_date(random_date)))

            test.log.step("30. (if available) Enable automatic time update via NITZ.")
            test.log.info("LOOP {0}/{1} FOR STEPS 17-32".format(steps_17_to_32_loop + 1, test.NUMBER_OF_LOOPS))
            test.expect(test.dut.at1.send_and_verify('AT+CTZU=1', '.*OK.*'))

            test.log.step("31. (if available) Try to get time from network- enter pin and wait 2 min.")
            test.log.info("LOOP {0}/{1} FOR STEPS 17-32".format(steps_17_to_32_loop + 1, test.NUMBER_OF_LOOPS))
            test.expect(test.dut.dstl_enter_pin(test.dut.sim))
            test.sleep(120)

            test.log.step("32. Check time.")
            test.log.info("LOOP {0}/{1} FOR STEPS 17-32".format(steps_17_to_32_loop + 1, test.NUMBER_OF_LOOPS))
            actual_date = datetime.datetime.now()
            test.expect(check_time_from_network(test, actual_date))

        test.log.step("33. Set cross year date and time , ex: at+cclk=\"17/12/31,23:59:50\"")
        cross_time = datetime.datetime(2019, 12, 31, 23, 59, 50)
        test.expect(test.dut.dstl_set_real_time_clock(time=format_date(cross_time)))
        test.sleep(10)
        date_after_wait = add_time_to_date(cross_time, 10)
        check_time(test, date_after_wait)

    def cleanup(test):
        test.dut.dstl_set_real_time_clock()
        test.expect(test.dut.at1.send_and_verify('AT&F', ".*OK.*"))


def check_time(test, date):
    test.expect(test.dut.at1.send_and_verify("AT+CCLK?", ".*OK.*"))
    current_date = test.dut.at1.last_response
    expected_date = False
    test.log.info("Compare cclk output with actual time >" + str(date) +"<")
    for second in range(test.DATE_MARGIN_IN_SECONDS):
        if format_date(add_time_to_date(date, second)) in current_date:
            expected_date = True
            break
    test.expect(expected_date)


def check_time_from_network(test, date):
    test.expect(test.dut.at1.send_and_verify("AT+CCLK?", ".*OK.*"))
    test.log.info("Compare cclk output with actual time >" + str(date) +"<")
    return date.strftime("%y/%m/%d") in test.dut.at1.last_response


def prepare_random_date():
    start_date = datetime.datetime(2018, 1, 1)
    end_date = datetime.datetime(2022, 12, 31)
    return start_date + datetime.timedelta(seconds=random.randint(0, int((end_date - start_date).total_seconds())), )


def format_date(date):
    return date.strftime("%y/%m/%d,%H:%M:%S")


def add_time_to_date(date, seconds_to_add):
    return date + datetime.timedelta(seconds=seconds_to_add)


if "__main__" == __name__:
    unicorn.main()
