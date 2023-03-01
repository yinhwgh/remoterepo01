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


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        test.log.info("*** 1. Test, read, exec and write command without PIN ***")
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*SIM PIN.*OK"))
        test.dut.dstl_lock_sim()
        test.log.info("*** 2. Restart the Module ***")
        test.dut.dstl_restart()
        test.log.info("*** 3. Activate URC simstatus ***")
        test.expect(test.dut.dstl_enable_one_indicator("simstatus"))
        test.log.info("*** 4. Check the setting ***")
        test.expect(test.dut.dstl_check_indicator_value("simstatus", 1))
        test.log.info("*** 5. Remove SIM Card ***")
        test.dut.dstl_remove_sim()
        test.expect(test.dut.dstl_check_urc("+CIEV: simstatus,0"))
        test.sleep(2)
        test.log.info("*** 6. Insert SIM Card ***")
        test.dut.dstl_insert_sim()
        test.expect(test.dut.dstl_check_urc("+CIEV: simstatus,1"))
        test.expect(test.dut.dstl_check_urc("+CIEV: simstatus,3"))
        test.log.info("*** 7. Enter PIN ***")
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.dstl_check_urc("+CIEV: simstatus,4"))
        test.expect(test.dut.dstl_check_urc("+CIEV: simstatus,5"))
        test.log.info("*** 8. Unlock SIM Card ***")
        test.dut.dstl_unlock_sim()
        test.log.info("*** 9. Remove SIM Card ***")
        test.dut.dstl_remove_sim()
        test.expect(test.dut.dstl_check_urc("+CIEV: simstatus,0"))
        test.sleep(2)
        test.log.info("*** 10. Insert SIM Card ***")
        test.dut.dstl_insert_sim()
        test.expect(test.dut.dstl_check_urc("+CIEV: simstatus,1"))
        test.expect(test.dut.dstl_check_urc("+CIEV: simstatus,4"))
        test.expect(test.dut.dstl_check_urc("+CIEV: simstatus,5"))

    def cleanup(test):
        test.dut.dstl_unlock_sim()
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK*."))


if (__name__ == "__main__"):
    unicorn.main()
