#responsible: yunhui.zhang@thalesgroup.com
#location: Beijing
#TC0092548.001 - TpAtSset

"""
This procedure provides automatic tests for the AT^SSET.

"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.security import lock_unlock_sim
from dstl.auxiliary import restart_module
from dstl.auxiliary import check_urc
from dstl.configuration import network_registration_status
from dstl.usim import get_imsi
from dstl.usim import sset_mode_control


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_lock_sim()
        test.dut.dstl_restart()
        test.sleep(5)

    def run(test):
        test.log.step("1. Test configuration commands **")
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*SIM PIN.*OK"))
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(5)
        test.expect(test.dut.dstl_get_imsi())
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK*."))
        test.expect(test.dut.at1.send_and_verify("at^sset=?", ".*OK*."))
        test.expect(test.dut.dstl_check_sset_mode("disable"))
        test.set_check_disable_enalbe_mode("enable")
        test.expect(test.dut.at1.send_and_verify('at+cmee=1', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at^sset=", ".*\+CME ERROR: 21.*"))
        test.expect(test.dut.at1.send_and_verify("at&w", ".*OK*."))
        test.set_check_disable_enalbe_mode("disable")
        test.dut.dstl_restart()
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*SIM PIN.*OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"{}\"".format(test.dut_sim.pin1), ".*OK.*"))
        test.sleep(5)
        test.expect(test.dut.dstl_check_urc("^SSIM READY"))
        test.expect(test.dut.dstl_get_imsi())
        test.expect(test.dut.dstl_check_sset_mode("enable"))
        test.expect(test.dut.at1.send_and_verify("at&f", ".*OK*."))
        test.expect(test.dut.dstl_check_sset_mode("disable"))
        test.expect(test.dut.at1.send_and_verify("atz", ".*OK*."))
        test.expect(test.dut.dstl_check_sset_mode("enable"))
        test.expect(test.dut.at1.send_and_verify("at&f", ".*OK*."))
        test.dut.dstl_restart()
        test.sleep(5)

        test.log.step("2. URC :SIM READY appearing after entering SIM PIN1 **")
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*SIM PIN.*OK"))
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(5)
        test.expect(test.dut.dstl_get_imsi())
        test.dut.dstl_restart()
        test.sleep(5)
        test.set_check_disable_enalbe_mode("enable")
        test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"{}\"".format(test.dut_sim.pin1), ".*OK.*"))
        test.sleep(5)
        test.expect(test.dut.dstl_check_urc("^SSIM READY"))

        test.log.step("3. URC :SIM READY not appearing after entering SIM PIN1 **")
        test.dut.dstl_restart()
        test.sleep(10)
        test.set_check_disable_enalbe_mode("disable")
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(5)
        if test.dut.at1.verify("^SSIM READY", test.dut.at1.last_response):
            test.log.error("URC should not pop up")
        test.expect(test.dut.dstl_get_imsi())

        test.log.step("4. URC :SIM READY appearing after restart **")
        test.dut.dstl_unlock_sim()
        test.set_check_disable_enalbe_mode("enable")
        test.expect(test.dut.at1.send_and_verify("at&w", ".*OK*."))
        test.dut.dstl_restart()
        test.sleep(5)
        test.expect(test.dut.dstl_check_urc("^SSIM READY"))

        test.log.step("5. URC :SIM READY not appearing after restart **")
        test.set_check_disable_enalbe_mode("disable")
        test.expect(test.dut.at1.send_and_verify("at&w", ".*OK*."))
        test.dut.dstl_restart()
        test.sleep(5)
        if test.dut.at1.verify("^SSIM READY", test.dut.at1.last_response):
            test.log.error("URC should not pop up")
        test.expect(test.dut.dstl_get_imsi())


    def cleanup(test):
        test.dut.dstl_lock_sim()
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK*."))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK*."))


    def set_check_disable_enalbe_mode(test,expect_mode):

        test.expect(test.dut.dstl_set_sset_mode(expect_mode))
        test.expect(test.dut.dstl_check_sset_mode(expect_mode))
        return True


if (__name__ == "__main__"):
    unicorn.main()
