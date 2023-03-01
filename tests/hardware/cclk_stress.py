#responsible: mariusz.wojcik@globallogic.com
#location: Wroclaw
#TC0102564.001

import unicorn
import datetime
import random
from time import time
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from dstl.identification import get_imei


class Test(BaseTest):
    """
    Check functionality of AT+CCLK command in stress scenario.

    1. Send AT+CCLK=time. As time use random correct time in "yy/mm/dd,hh:mm:ss". For available range of correct time check AT spec.
    2. Send AT+CCLK? and check if set time is same as set in step 1. (Difference between set time and current shouldn't be too big)
    Perform steps 1-2 for 1 hour.
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()

    def run(test):
        start_time = time()
        end_time = start_time + 3600

        start_date = datetime.datetime(2018, 1, 1)
        end_date = datetime.datetime(2022, 12, 31)
        date_format = "%y/%m/%d,%H:%M:%S"

        test.log.step("Perform steps 1-2 for 1 hour.")
        while time() < end_time:
            new_date = random_date(start_date, end_date)
            one_second_margin = new_date + datetime.timedelta(seconds=1)
            two_second_margin = new_date + datetime.timedelta(seconds=2)
            formatted_date = new_date.strftime(date_format)
            formatted_one_second_margin = one_second_margin.strftime(date_format)
            formatted_two_second_margin = two_second_margin.strftime(date_format)

            test.log.step("1. Send AT+CCLK=time. As time use random correct time in \"yy/mm/dd,hh:mm:ss\". For available range of correct time check AT spec.")
            test.expect(test.dut.dstl_set_real_time_clock(time=formatted_date))

            test.log.step("2. Send AT+CCLK? and check if set time is same as set in step 1. (Difference between set time and current shouldn't be too big)")
            test.expect(test.dut.at1.send_and_verify("AT+CCLK?", ".*OK.*"))
            current_date = test.dut.at1.last_response
            expected_date = formatted_date in current_date \
                            or formatted_one_second_margin in current_date \
                            or formatted_two_second_margin in current_date
            test.expect(expected_date)

    def cleanup(test):
        test.dut.dstl_set_real_time_clock()


def random_date(start, end):
    """Generate a random datetime between 'start' and 'end'"""

    return start + datetime.timedelta(seconds=random.randint(0, int((end - start).total_seconds())),)


if "__main__" == __name__:
    unicorn.main()
