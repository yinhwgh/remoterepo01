#responsible: mariusz.wojcik@globallogic.com
#location: Wroclaw
#TC0092774.001

import unicorn
import re
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei


class Test(BaseTest):
    """
    Aim of this test is verification is ADC URC are displayed in correct time intervals.

    10 times set different ADC period of measurement in range:
    1. <100-1000> and check if correct numbers of measurements are displayed in each URC and time of URC displaying is in each case 1s.
    2. <1001-30000> and check if time of URC displaying is is the same as periodic measurement time.
    """

    SHORT_MEASUREMENT_PERIODS = {100: 10, 200: 5, 250: 4, 500: 2, 1000: 1}
    LONG_MEASUREMENT_PERIODS = [2000, 5000, 10000, 15000, 30000]
    SHORT_MEASUREMENT_TIME = 10

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()

    def run(test):
        test.log.info("10 times set different ADC period of measurement in range:")
        test.log.step("1. <100-1000> and check if correct numbers of measurements are displayed in each URC and time of URC displaying is in each case 1s.")
        for iteration in range(10):
            perform_short_measurements(test, iteration)

        test.log.step("2. <1001-30000> and check if time of URC displaying is is the same as periodic measurement time.")
        for iteration in range(10):
            perform_long_measurements(test, iteration)

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT^SRADC=0,0", ".*OK.*"))


def perform_short_measurements(test, iteration):
    for period, expected_number_of_measurements in test.SHORT_MEASUREMENT_PERIODS.items():
        test.log.info("STEP 1, ITERATION {0}/10 for period{1}".format(iteration + 1, period))
        command_measurements_response = match_measurements(test, period, test.SHORT_MEASUREMENT_TIME)
        test.expect(len(command_measurements_response) == test.SHORT_MEASUREMENT_TIME)
        check_measurements(test, command_measurements_response, expected_number_of_measurements)


def perform_long_measurements(test, iteration):
    for period in test.LONG_MEASUREMENT_PERIODS:
        test.log.info("STEP 1, ITERATION {0}/10 for period{1}".format(iteration + 1, period))
        command_measurements_response = match_measurements(test, period, period / 1000)
        test.expect(len(command_measurements_response) == 1)
        check_measurements(test, command_measurements_response, 1)


def match_measurements(test, period, measuring_time):
    test.expect(test.dut.at1.send_and_verify("AT^SRADC=0,1,{}".format(period), ".*OK.*"))
    test.sleep(measuring_time)
    measurements = test.dut.at1.read()
    test.expect(test.dut.at1.send_and_verify("AT^SRADC=0,0", ".*OK.*"))

    return re.findall("\\^SRADC: \\d,(\\d+),(.*)", measurements)


def check_measurements(test, command_measurements_response, expected_number_of_measurements):
    for regex_group in command_measurements_response:
        test.expect(regex_group[0] == str(expected_number_of_measurements))
        measurements_in_group = regex_group[1].split(",")
        test.expect(len(measurements_in_group) == expected_number_of_measurements)


if "__main__" == __name__:
    unicorn.main()
