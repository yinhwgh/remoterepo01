#responsible: mariusz.wojcik@globallogic.com
#location: Wroclaw
#TC0088331.001

import unicorn
import re
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
    Test the ADC buffering of "^SRADC" URCs.

    1. ## Main scenario ##
    1.1. Start periodic measurement mode on the ADC_1. Samples are taken every 500ms.
    1.2. Type directly on main terminal window any AT command (typing should take 10-30 sec) and send cmd
    1.3. Check if all measurements were buffered during command input and sent after completion
    1.4. Type directly on main terminal window any AT command (typing should take few minutes) and send cmd
        or send AT command, which requires long time to perform
    1.5. Check if 5 first URC's contain 11 measurements and if in 6th URC the last value is 32767
    1.6. Close ADC_1
    2. If module supports ADC_2 repeat point 1 on ADC_2.
    3. If module supports ADC_2 repeat point 1 on ADC_1 and ADC_2 simultaneously.
    4. If module supports ADC_3 repeat point 1 on ADC_3.
    5. If module supports ADC_3 repeat point 1 on ADC_1, ADC_2 and ADC_3 simultaneously.
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.expect(test.dut.dstl_enter_pin(test.dut.sim))

    def run(test):
        test.log.step("1.1. Start periodic measurement mode on the ADC_1. Samples are taken every 500ms.")
        test.expect(test.dut.at1.send_and_verify("AT^SRADC=0,1,500", ".*OK.*"))

        test.log.step("1.2. Type directly on main terminal window any AT command (typing should take 10-30 sec) and send cmd")
        type_command_on_terminal(test, "AT")
        precise_measurements = remove_old_measurements_from_buffer(test.dut.at1.last_response)

        test.log.step("1.3. Check if all measurements were buffered during command input and sent after completion")
        result = re.findall("\\^SRADC: \\d,(\\d+),(.*)", precise_measurements)
        check_short_buffer(test, result)

        test.log.step("1.4. Type directly on main terminal window any AT command (typing should take few minutes) "
                      "and send cmd or send AT command, which requires long time to perform")
        test.expect(test.dut.at1.send_and_verify("AT+COPS=?", "OK|ERROR", timeout=900))
        precise_measurements = remove_old_measurements_from_buffer(test.dut.at1.last_response)

        test.log.step("1.5. Check if 5 first URC's contain 11 measurements and if in 6th URC the last value is 32767")
        result = re.findall("\\^SRADC: \\d,(\\d+),(.*)", precise_measurements)
        check_long_buffer(test, result)

        test.log.step("1.6. Close ADC_1")
        test.expect(test.dut.at1.send_and_verify("AT^SRADC=0,0", ".*OK.*"))

        test.log.step("2. If module supports ADC_2 repeat point 1 on ADC_2.")
        if test.dut.project.upper() == "SERVAL":
            test.log.info("Product {} doesn't support ADC 2 channel".format(test.dut.project))
        else:
            test.log.error("Step is not implemented for product {}".format(test.dut.project))
            test.fail()

        test.log.step("3. If module supports ADC_2 repeat point 1 on ADC_1 and ADC_2 simultaneously.")
        if test.dut.project.upper() == "SERVAL":
            test.log.info("Product {} doesn't support ADC 2 channel".format(test.dut.project))
        else:
            test.log.error("Step is not implemented for product {}".format(test.dut.project))
            test.fail()

        test.log.step("4. If module supports ADC_3 repeat point 1 on ADC_3.")
        if test.dut.project.upper() == "SERVAL":
            test.log.info("Product {} doesn't support ADC 3 channel".format(test.dut.project))
        else:
            test.log.error("Step is not implemented for product {}".format(test.dut.project))
            test.fail()

        test.log.step("5. If module supports ADC_3 repeat point 1 on ADC_1, ADC_2 and ADC_3 simultaneously.")
        if test.dut.project.upper() == "SERVAL":
            test.log.info("Product {} doesn't support ADC 3 channel".format(test.dut.project))
        else:
            test.log.error("Step is not implemented for product {}".format(test.dut.project))
            test.fail()

    def cleanup(test):
        test.dut.at1.send_and_verify("AT", ".*OK.*")
        test.dut.at1.send_and_verify("AT^SRADC=0,0", ".*OK.*")
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))


def check_short_buffer(test, result):
    """
    This method checks, if ADC measurements lines have correct values after 10 seconds buffering.

    Args:
        test: test object
        result: regex object from AT^SRADC measurement lines

    For example, if result is:
    ^SRADC: 0,11,100,98,98,98,99,99,99,99,99,99,99
    ^SRADC: 0,9,99,99,99,99,100,99,99,99,99

    then result[i] means given line of measurements: f.e. ^SRADC: 0,11,100,98,98,98,99,99,99,99,99,99,99
    and result[i][j] means given group of elements in line. There are two significant groups:
    First group: number of measurements: 11
    Second group: list of measurements: 100,98,98,98,99,99,99,99,99,99,99
    """

    test.expect(result[0][0] == "11")
    measurements_in_group = result[0][1].split(",")
    test.expect(len(measurements_in_group) == 11)
    test.expect(result[1][0] == "11")
    measurements_in_group = result[1][1].split(",")
    test.expect(len(measurements_in_group) == 11)


def check_long_buffer(test, result_regex):
    for sradc_line in range(5):
        test.expect(result_regex[sradc_line][0] == "11")
        measurements_in_group = result_regex[sradc_line][1].split(",")
        test.expect(len(measurements_in_group) == 11)
    test.expect("32767" in result_regex[5][1])


def remove_old_measurements_from_buffer(buffer):
    if "OK" in buffer:
        return buffer[buffer.find("OK"):]
    elif "ERROR" in buffer:
        return buffer[buffer.find("ERROR"):]
    else:
        return buffer


def type_command_on_terminal(test, command):
    test.dut.at1.send(command, end="")
    test.sleep(11)
    test.dut.at1.send("")
    test.dut.at1.wait_for("OK")


if "__main__" == __name__:
    unicorn.main()
