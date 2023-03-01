#responsible: mariusz.wojcik@globallogic.com
#location: Wroclaw
#TC0102563.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from dstl.identification import get_imei


class Test(BaseTest):
    """
    TC0102563.001	CclkBasic
    Basic test checking if at command AT+CCLK is implemented.
    responsible: mariusz.wojcik@globallogic.com
    location: Wroclaw
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()

    def run(test):
        test.log.step("1. Send AT+CCLK=?")
        test.expect(test.dut.at1.send_and_verify("AT+CCLK=?", ".*OK.*"))

        test.log.step("2. Send AT+CCLK?")
        test.expect(test.dut.at1.send_and_verify("AT+CCLK?", ".*OK.*"))

        test.log.step("3. Send AT+CCLK=time. As time use current time in format \"yy/mm/dd,hh:mm:ss\"")
        test.expect(test.dut.dstl_set_real_time_clock())

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
