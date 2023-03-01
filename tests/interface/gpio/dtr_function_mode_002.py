#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0010205.002

import unicorn
from core.basetest import BaseTest
import random
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.network_service import register_to_network
from dstl.call import switch_to_command_mode


class Test(BaseTest):
    """
        TC0010205.002 - DTRFunctionMode
        The module shall be able to either ignore the DTR line of the RS232 interface or switch to command mode during
        a data call or release the data call, depending on the DTR value.
        Subscribers: dut
        Debugged: Boxwood step 8
        duration: 3 min
        Author: lei.chen@thalesgroup.com
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_enter_pin()
        test.dut.at1.send_and_verify("AT&F", "OK")
        test.dut.at1.send("AT^SCFG?")
        response = test.dut.at1.read()
        if "GPIO/mode/DTR0" in response:
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"GPIO/mode/DTR0\",\"std\"", "OK"))
        test.valid_atd_modes = [0, 1, 2, ""]
        test.test_atd_modes = [0, 1, 2, "", "AT&F"]
        test.default_atd = 2
        test.new_atd = 2

    def run(test):
        test_step = 1
        for atd_mode in test.test_atd_modes:
            test.log.step("{}. Test send and config AT&D mode {}".format(test_step, atd_mode))
            test.send_and_config(test_step, atd_mode)
            test.log.info("{}.12 Toogle DTR line, should be ignored".format(test_step))
            if atd_mode == 0 or atd_mode == "":
                test.expect(test.dut.at1.send_and_verify("ATD*99#", expect="CONNECT", wait_for="CONNECT"))
                test.dut.at1.connection.setDTR(False)
                test.sleep(1)
                test.dut.at1.connection.setDTR(True)
                test.expect(test.dut.at1.send_and_verify("AT", expect="^((?!OK).)*$", wait_for=".*", wait_after_send=5))
                test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
                test.expect("NO CARRIER" in test.dut.at1.last_response or test.dut.at1.wait_for("NO CARRIER"))
            elif atd_mode == 1:
                test.log.info("{}.12 Toogle DTR line, ME should switch to command mode".format(test_step))
                test.expect(test.dut.at1.send_and_verify("ATD*99#", expect="CONNECT", wait_for="CONNECT"))
                test.expect(test.dut.dstl_switch_to_command_mode_by_dtr())
                test.sleep(5)  # wait for GPRS ready
                test.expect(test.dut.at1.send_and_verify("ATD*99#", expect="CONNECT", wait_for="CONNECT"))
                test.sleep(1)
                test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
                test.expect("NO CARRIER" in test.dut.at1.last_response or test.dut.at1.wait_for("NO CARRIER"))
            else:  # atd_mode == 2 or atd_mode = "AT&F"
                test.log.info("{}.12 Toogle DTR line, (check if NO CARRIER appears)".format(test_step))
                test.expect(test.dut.at1.send_and_verify("ATD*99#", expect="CONNECT", wait_for="CONNECT"))
                test.expect(test.dut.dstl_switch_to_command_mode_by_dtr())
                test.expect('NO CARRIER' in test.dut.at1.last_response)
            test_step += 1

    def cleanup(test):
        test.dut.at1.send("AT", wait_after_send=1)
        last_response = test.dut.at1.read()
        if 'OK' not in last_response:
            test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())

    def send_and_config(test, step_number, atd_mode):
        test.generate_new_atd(atd_mode)
        if atd_mode == "AT&F":
            atd_command = "AT&F"
            atd_mode = "2"
        else:
            atd_command = "AT&D{}".format(atd_mode)
        test.log.step(" new mode is {}".format(step_number, atd_mode, test.new_atd))

        test.log.info("{}.1. Set specified AT&D parameter by AT&D".format(step_number))
        test.expect(test.dut.at1.send_and_verify(atd_command, expect="OK"))

        test.log.info("{}.2. Query the current value of AT&D by AT&V".format(step_number))
        test.expect(test.dut.at1.send_and_verify("AT&V", expect="&D{}".format(atd_mode)))

        test.log.info("{}.3.  Store AT&D to user profile by AT&W".format(step_number))
        test.expect(test.dut.at1.send_and_verify("AT&W", expect="OK"))

        test.log.info("{}.4. Set other value by AT&D command".format(step_number))
        test.expect(test.dut.at1.send_and_verify("AT&D{}".format(test.new_atd), expect="OK"))

        test.log.info("{}.5. Query the current value of AT&D by AT&V".format(step_number))
        test.expect(test.dut.at1.send_and_verify("AT&V", expect="&D{}".format(test.new_atd)))

        test.log.info("{}.6. Restore AT&D value from profile by ATZ".format(step_number))
        test.expect(test.dut.at1.send_and_verify("ATZ", expect="OK"))

        test.log.info("{}.7. Query the current value of AT&D by AT&V".format(step_number))
        test.expect(test.dut.at1.send_and_verify("AT&V", expect="&D{}".format(atd_mode)))

        test.log.info("{}.8. Set other value by AT&D command".format(step_number))
        test.expect(test.dut.at1.send_and_verify("AT&D{}".format(test.new_atd), expect="OK"))

        test.log.info("{}.9. Query the current value of AT&D by AT&V".format(step_number))
        test.expect(test.dut.at1.send_and_verify("AT&V", expect="&D{}".format(test.new_atd)))

        test.log.info("{}.10. Restart module".format(step_number))
        test.expect(test.dut.dstl_restart())
        test.sleep(3)  # wait for pin card being recognized
        test.expect(test.dut.dstl_register_to_network())

        test.log.info("{}.11. Query the current value of AT&D by AT&V".format(step_number))
        test.expect(test.dut.at1.send_and_verify("AT&V", expect="&D{}".format(atd_mode)))

    def generate_new_atd(test, current_atd):
        while test.new_atd == current_atd:
            test.new_atd = random.choice(test.valid_atd_modes)


if "__main__" == __name__:
    unicorn.main()
