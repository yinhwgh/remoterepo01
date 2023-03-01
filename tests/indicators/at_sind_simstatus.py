#responsible: yunhui.zhang@thalesgroup.com
#location: Beijing
#TC0093090.001 - TpSindSimStatus

"""
Check ^SIND: simstatus-URC inserted/removed, pin required/enabled sim card.

"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.security import lock_unlock_sim
from dstl.auxiliary import restart_module
from dstl.auxiliary.devboard import devboard
from dstl.status_control import extended_indicator_control
from dstl.auxiliary import check_urc
from dstl.status_control import sind_parameters


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_lock_sim()
        test.dut.dstl_restart()
        test.sleep(5)

    def run(test):
        test.log.step("1. Test,read,exec and write command without PIN **")
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*SIM PIN.*OK"))
        test.expect(test.dut.dstl_get_all_indicators())
        test.expect(test.dut.dstl_get_sind_read_response_dict())

        test.log.step("2. Activate URC simstatus **")
        test.expect(test.dut.dstl_enable_one_indicator("simstatus"))
        test.log.step("3. Check the setting **")
        test.expect(test.dut.dstl_check_indicator_value("simstatus", 1))
        test.log.step("4. Remove SIM Card **")
        test.dut.dstl_remove_sim()
        test.sleep(2)
        test.expect(test.dut.dstl_check_urc("+CIEV: simstatus,0"))
        test.log.step("5. Check the setting **")
        test.expect(test.dut.dstl_check_indicator_value("simstatus", 1, 0))
        test.log.step("6. Insert SIM Card **")
        test.dut.dstl_insert_sim()
        test.sleep(2)
        test.expect(test.dut.dstl_check_urc("+CIEV: simstatus,1"))
        test.expect(test.dut.dstl_check_urc("+CIEV: simstatus,3"))
        test.log.step("7. Check the setting **")
        test.expect(test.dut.dstl_check_indicator_value("simstatus", 1, 3))

        test.log.step("8. Restart the Module **")
        test.dut.dstl_restart()
        test.log.step("9. Activate URC simstatus **")
        test.expect(test.dut.dstl_enable_one_indicator("simstatus"))
        test.log.step("10. Enter PIN **")
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(2)
        test.expect(test.dut.dstl_check_urc("+CIEV: simstatus,4"))
        test.expect(test.dut.dstl_check_urc("+CIEV: simstatus,5"))
        test.log.step("11. Deactivate URC simstatus **")
        test.expect(test.dut.dstl_disable_one_indicator("simstatus"))
        test.log.step("12. Remove SIM Card **")
        test.dut.dstl_remove_sim()
        test.sleep(5)
        if test.dut.at1.verify("+CIEV: simstatus,0", test.dut.at1.last_response):
            test.log.error("URC should not pop up")
        test.log.step("13. Insert SIM Card **")
        test.dut.dstl_insert_sim()
        test.sleep(5)
        if test.dut.at1.verify("+CIEV: simstatus,1", test.dut.at1.last_response):
            test.log.error("URC should not pop up")
        if test.dut.at1.verify("+CIEV: simstatus,4", test.dut.at1.last_response):
            test.log.info("Expected-URC does not pop up")
        if test.dut.at1.verify("+CIEV: simstatus,5", test.dut.at1.last_response):
            test.log.error("URC should not be pop up")
        test.log.step("14. Activate URC simstatus **")
        test.expect(test.dut.dstl_enable_one_indicator("simstatus"))
        test.log.step("15. Check the setting **")
        test.expect(test.dut.dstl_check_indicator_value("simstatus", 1))
        test.log.step("16. Enter PIN **")
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(2)
        test.expect(test.dut.dstl_check_urc("+CIEV: simstatus,4"))
        test.expect(test.dut.dstl_check_urc("+CIEV: simstatus,5"))
        test.log.step("17. Check the setting **")
        test.expect(test.dut.dstl_check_indicator_value("simstatus", 1, 5))
        test.log.step("18. Unlock SIM Card **")
        test.dut.dstl_unlock_sim()
        test.log.step("19. Remove SIM Card **")
        test.dut.dstl_remove_sim()
        test.sleep(2)
        test.expect(test.dut.dstl_check_urc("+CIEV: simstatus,0"))
        test.log.step("20. Insert SIM Card **")
        test.dut.dstl_insert_sim()
        test.sleep(2)
        test.expect(test.dut.dstl_check_urc("+CIEV: simstatus,1"))
        test.expect(test.dut.dstl_check_urc("+CIEV: simstatus,4"))
        test.expect(test.dut.dstl_check_urc("+CIEV: simstatus,5"))

    def cleanup(test):
        test.dut.dstl_lock_sim()
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK*."))


if (__name__ == "__main__"):
    unicorn.main()
