#responsible: mariusz.wojcik@globallogic.com
#location: Wroclaw
#TC0095831.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.devboard import devboard


class Test(BaseTest):
    """
    Check functionality of AT^SCFG="MEShutdown/sVsup"

    1. Send AT^SCFG?
    2. Send AT^SCFG=?
    3. Check default setting AT^SCFG="MEShutdown/sVsup"
    4. Set AT^SCFG="MEShutdown/sVsup","on"
    5. Check current "MEShutdown/sVsup" setting.
    6. Decrease module voltage below minimum value which is described in HID.
    7. Set module voltage to 3.8V
    8. Set AT^SCFG="MEShutdown/sVsup","off"
    9. Check current "MEShutdown/sVsup" setting.
    10. Decrease module voltage below minimum value which is described in HID.
    11. Wait until module will shudown
    12. Set module voltage to 3.8V
    13. Turn on module
    14. Check current "MEShutdown/sVsup" setting.
    15. Restart module AT+CFUN=1,1
    16. Check current "MEShutdown/sVsup" setting.
    """

    MIN_VOLTAGE = 2500
    NORMAL_VOLTAGE = 3800

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()

    def run(test):
        test.log.step("1. Send AT^SCFG?")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG?", ".*OK.*"))
        test.expect("\"MEShutdown/sVsup\"" not in test.dut.at1.last_response)

        test.log.step("2. Send AT^SCFG=?")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=?", ".*OK.*"))
        test.expect("\"MEShutdown/sVsup\"" not in test.dut.at1.last_response)

        test.log.step("3. Check default setting AT^SCFG=\"MEShutdown/sVsup\"")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"MEShutdown/sVsup\"", ".*off.*", wait_for="OK"))

        test.log.step("4. Set AT^SCFG=\"MEShutdown/sVsup\",\"on\"")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"MEShutdown/sVsup\",\"on\"", ".*OK.*"))

        test.log.step("5. Check current \"MEShutdown/sVsup\" setting.")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"MEShutdown/sVsup\"", ".*on.*", wait_for="OK"))

        test.log.step("6. Decrease module voltage below minimum value which is described in HID.")
        test.expect(test.dut.devboard.send_and_verify("MC:VBATT={}mV".format(test.MIN_VOLTAGE), ".*OK.*"))
        test.expect(test.dut.at1.wait_for(".*SBC: Undervoltage.*", timeout=60))
        test.sleep(5)
        test.expect(test.dut.dstl_check_if_module_is_on_via_dev_board())

        test.log.step("7. Set module voltage to 3.8V")
        test.expect(test.dut.devboard.send_and_verify("MC:VBATT={}mV".format(test.NORMAL_VOLTAGE), ".*OK.*"))

        test.log.step("8. Set AT^SCFG=\"MEShutdown/sVsup\",\"off\"")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"MEShutdown/sVsup\",\"off\"", ".*OK.*"))

        test.log.step("9. Check current \"MEShutdown/sVsup\" setting.")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"MEShutdown/sVsup\"", ".*off.*", wait_for="OK"))

        test.log.step("10. Decrease module voltage below minimum value which is described in HID.")
        test.expect(test.dut.devboard.send_and_verify("MC:VBATT={}mV".format(test.MIN_VOLTAGE), ".*OK.*"))
        test.expect(test.dut.at1.wait_for(".*SBC: Undervoltage.*", timeout=60))

        test.log.step("11. Wait until module will shudown")
        test.expect(wait_for_shutdown(test))

        test.log.step("12. Set module voltage to 3.8V")
        test.expect(test.dut.devboard.send_and_verify("MC:VBATT={}mV".format(test.NORMAL_VOLTAGE), ".*OK.*"))

        test.log.step("13. Turn on module")
        test.expect(test.dut.dstl_turn_on_igt_via_dev_board(time_to_sleep=30))

        test.log.step("14. Check current \"MEShutdown/sVsup\" setting.")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"MEShutdown/sVsup\"", ".*off.*", wait_for="OK"))

        test.log.step("15. Restart module AT+CFUN=1,1")
        test.expect(test.dut.dstl_restart())

        test.log.step("16. Check current \"MEShutdown/sVsup\" setting.")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"MEShutdown/sVsup\"", ".*off.*", wait_for="OK"))

    def cleanup(test):
        test.dut.devboard.send_and_verify("MC:VBATT={}mV".format(test.NORMAL_VOLTAGE), ".*OK.*")
        test.dut.dstl_turn_on_igt_via_dev_board(time_to_sleep=30)
        test.dut.at1.send_and_verify("AT^SCFG=\"MEShutdown/sVsup\",\"off\"", ".*OK.*")


def wait_for_shutdown(test):
    for attempt in range(10):
        test.log.info("Checking, if module is turned off. Loop {}/10".format(attempt + 1))
        test.sleep(5)
        is_module_on = test.dut.dstl_check_if_module_is_on_via_dev_board()
        if not is_module_on:
            return True
    return False


if "__main__" == __name__:
    unicorn.main()
