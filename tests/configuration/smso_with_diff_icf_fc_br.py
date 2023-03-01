#author: cong.hu@thalesgroup.com
#location: Dalian
#TC0104723.001
import unicorn
from core.basetest import BaseTest
import serial
import re
from random import choice
from dstl.serial_interface import serial_interface_flow_control
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import restart_module
from dstl.auxiliary.devboard import devboard
from dstl.auxiliary import check_urc
from dstl.security import lock_unlock_sim
from dstl.serial_interface import config_baudrate

class Test(BaseTest):
    ICF_RANGE = "\+ICF: \(1-3,5\),\(0-1\)"
    ICF_LIST = {
                 "5,1": [serial.SEVENBITS, serial.PARITY_EVEN, serial.STOPBITS_ONE],  # (5,1), 7E1
                 "5,0": [serial.SEVENBITS, serial.PARITY_ODD, serial.STOPBITS_ONE],  # (5,0), 7O1
                 "2,1": [serial.EIGHTBITS, serial.PARITY_EVEN, serial.STOPBITS_ONE],  # (2,1), 8E1
                 "3": [serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE],  # (3), 8N1, DEFAULT
                 "2,0": [serial.EIGHTBITS, serial.PARITY_ODD, serial.STOPBITS_ONE],  # (2,0), 8O1
                 "1": [serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_TWO]  # (1), 8N2
                }
    original_baudrate_str = ''
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_unlock_sim()
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='.*OK.*'))

    def run(test):
        test.log.info('Part1: ICF testing')
        test.expect(test.dut.at1.send_and_verify('AT+CREG=1', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CREG?', expect='.*\+CREG: 1,1.*'))
        test.expect(test.dut.at1.send_and_verify("at+icf=?", test.ICF_RANGE))
        # Get current icf stored in user profile
        test.expect(test.dut.at1.send_and_verify("at+icf?", timeout=10))
        current_result = re.search("(ICF:)(.*\d\s)", test.dut.at1.last_response)
        current_icf = ""
        if current_result:
            current_icf = current_result.group(2).strip()
        else:
            test.log.error("Incorrect response of AT+ICF?")

        for icf_value in test.ICF_LIST:
            test.expect(test.dut.at1.send_and_verify("at+icf={}".format(icf_value), timeout=10))
            # read command should return the value stored in user profile even icf is changed
            test.expect(test.dut.at1.send_and_verify("at+icf?", ".*\+ICF: {}".format(current_icf), timeout=10))
            # save to user profile and restart module to make value take effect
            test.log.info("** save to user profile and restart module to make value take effect **")
            test.dut.at1.send_and_verify("at&w", "OK")
            test.dut.at1.send_and_verify("at+cfun=1,1", "OK")
            test.sleep(0.2)
            test.dut.at1.reconfigure({"bytesize": test.ICF_LIST[icf_value][0],
                                      "parity": test.ICF_LIST[icf_value][1],
                                      "stopbits": test.ICF_LIST[icf_value][2]})
            test.dut.at1.wait_for("SYSSTART")
            test.sleep(5)
            test.expect(test.dut.at1.send_and_verify("at+icf?", ".*\+ICF: {}".format(icf_value), timeout=10))
            # when baud rate is slow, need wait more time for information output
            test.expect(test.dut.at1.send_and_verify("at&v", ".*\+ICF: {}".format(icf_value), timeout=10))
            current_icf = icf_value
            test.expect(test.dut.dstl_check_urc('.*\+CREG: 1.*'))
            test.expect(test.dut.at1.send_and_verify('AT^SMSO', expect='\s+\^SHUTDOWN.*'))
            test.sleep(5)
            test.expect(test.dut.dstl_turn_on_igt_via_dev_board(1000))
            test.expect(test.dut.dstl_check_urc('.*\^SYSSTART.*'))

        test.expect(test.dut.at1.send_and_verify('AT+ICF=3', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT&W', expect='.*OK.*'))
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify('AT+CREG=1', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CREG?', expect='.*\+CREG: 1,1.*'))


        test.log.info('Part2: Flow Control testing')
        SUPPORTED_ATQ_VALUES = test.dut.dstl_get_supported_flow_control_numbers()
        UNSUPPORTED_ATQ_VALUES = [x for x in (0, 1, 2, 3) if x not in SUPPORTED_ATQ_VALUES]
        unsupported_atq_value = None
        if len(UNSUPPORTED_ATQ_VALUES) > 0:
            unsupported_atq_value = UNSUPPORTED_ATQ_VALUES[0]
        last_atq_set_in_profile = None

        test.log.step("Check SMSO for all available AT\\Q parameters.")
        for atq_value in SUPPORTED_ATQ_VALUES:
            test.log.step("Step for AT\\Q{}. 1. Load manufacturer defaults at ASC0.".format(atq_value))
            test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify('AT+CREG=1', expect='.*OK.*'))

            test.log.step("Step for AT\\Q{}. 2. Query the current profile at ASC0.".format(atq_value))
            test.expect(test.dut.dstl_get_flow_control_number() == 3)

            test.log.step("Step for AT\\Q{}. 3. Set the \\Q to supported value at ASC0.".format(atq_value))
            # This step is executed in step 4 by method: dstl_check_flow_control_number_after_set. This method
            # sets AT\Q value and checks, if has been set correctly.

            test.log.step("Step for AT\\Q{}. 4. Query the current profile at ASC0.".format(atq_value))
            # For Serval products, AT\Q set to 2, returns 3. Expected value must be saved in another variable.
            is_correct, number_in_profile = test.dut.dstl_check_flow_control_number_after_set(atq_value)
            test.expect(is_correct)

            test.log.step("Step for AT\\Q{}. 5. Save to current profile.".format(atq_value))
            test.expect(test.dut.at1.send_and_verify("AT&W", "OK"))

            test.expect(test.dut.dstl_restart())
            test.sleep(10)
            test.expect(test.dut.at1.send_and_verify('AT+CREG?', expect='.*\+CREG: 1,1.*'))
            test.expect(test.dut.at1.send_and_verify('AT^SMSO', expect='\s+\^SHUTDOWN.*'))
            test.sleep(5)
            test.expect(test.dut.dstl_turn_on_igt_via_dev_board(1000))
            test.expect(test.dut.dstl_check_urc('.*\^SYSSTART.*'))
            test.sleep(10)
            test.expect(test.dut.at1.send_and_verify('AT+CREG?', expect='.*\+CREG: 1,1.*'))

        test.expect(test.dut.at1.send_and_verify('AT\Q3', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT&W', expect='.*OK.*'))
        test.expect(test.dut.dstl_restart())
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify('AT+CREG?', expect='.*\+CREG: 1,1.*'))

        test.log.info('Part3: Baudrate testing')

        test.dut.dstl_find_current_baudrate([], test.dut.at1)
        test.original_baudrate_str = test.expect(test.dut.dstl_get_baudrate(test.dut.at1))
        test.log.step("1.Check supported bitrates AT+IPR=?")
        supported_baudrates = test.dut.dstl_get_supported_baudrate_list()
        previous_baudrate = test.original_baudrate_str
        if test.original_baudrate_str not in supported_baudrates:
            test.log.error("##> current baudrate in module is NOT found in supported baudrates list")
            test.expect(False, critical=True)
            return

        for bitrate in supported_baudrates:
            #           IN CASE your place also does not suppot the highest BR, use this:
            #            if bitrate == '921600':
            #                test.log.step("bitrate {} not supported of my test place, we ignore it ".format(bitrate))
            #                continue

            test.log.step("bitrate {} | 2. Set supported bitrate on module. \
                        (starting from the lowest value)".format(bitrate))
            ret = test.dut.dstl_set_baudrate(bitrate, test.dut.at1)
            if not ret:
                test.log.step("failed to set bitrate {}, lets check which one is working now! ".format(bitrate))
                ret = test.expect(test.dut.at1.send_and_verify('AT', 'OK'))
                if not ret:
                    test.log.step("current bitrate {} does not work, lets try previous one! ".format(bitrate))
                    test.dut.at1.reconfigure(settings={"baudrate": previous_baudrate})
                    test.sleep(2)
                    ret = test.expect(test.dut.at1.send_and_verify('AT', 'OK'))
                    if not ret:
                        test.log.step(
                            "previous bitrate {} also does not work, unclear which baudrate may work, let's try all known baudrates:".format(
                                previous_baudrate))
                        ret = test.dut.dstl_find_current_baudrate([], test.dut.at1)
                        if not ret:
                            test.log.step("no legal baudrate is working - check manually - ABORT!")
                            test.expect(False, critical=True)
                            return
                        else:
                            test.log.step("a working baudrate was found, overjumping baudrate under test! ")
                            continue
                    else:
                        test.log.step(
                            "previous bitrate {} works again, overjumping baudrate under test! ".format(
                                previous_baudrate))
                        continue

                else:
                    test.log.step(
                        "current bitrate {} works, instead of problem in dstl_set_baudrate(), let's go on! ".format(
                            bitrate))

            test.log.step("bitrate {} | 3. Send some AT commands e.g. AT, ATI.".format(bitrate))
            test.expect(test.dut.at1.send_and_verify('AT', 'OK'))
            test.expect(test.dut.at1.send_and_verify('ATI', 'OK'))
            test.log.step("bitrate {} | 4. Restart module and check current bitrate.".format(bitrate))
            test.expect(test.dut.dstl_restart())
            test.sleep(10)
            test.expect(test.dut.at1.send_and_verify('AT+CREG?', expect='.*\+CREG: 1,1.*'))
            test.expect(test.dut.dstl_get_baudrate(test.dut.at1) == bitrate)
            test.expect(test.dut.at1.send_and_verify('AT^SMSO', expect='\s+\^SHUTDOWN.*'))
            test.sleep(5)
            test.expect(test.dut.dstl_turn_on_igt_via_dev_board(1000))
            test.expect(test.dut.dstl_check_urc('.*\^SYSSTART.*'))
            test.log.step("bitrate {} | 5. Repeat steps 3-4 increasing bitrate value according \
                         with documentation and finish on the highest value.".format(bitrate))

        test.expect(test.dut.at1.send_and_verify('AT+ipr=115200', expect='.*OK.*'))
        test.dut.at1.reconfigure(settings={"baudrate": 115200})
        test.expect(test.dut.dstl_restart())
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify('AT+CREG?', expect='.*\+CREG: 1,1.*'))

    def cleanup(test):
        pass

def get_random_parameter(parameters_range, parameter_to_exclude):
    random_range = list(parameters_range).copy()
    random_range.remove(parameter_to_exclude)
    return choice(random_range)

if '__main__' == __name__:
    unicorn.main()
