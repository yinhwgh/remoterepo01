# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0000001.001 template_wait_for

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei


class Test(BaseTest):

    def setup(test):
        pass

    def run(test):

        """Send the command and then start waiting for specific URC
        """

        test.dut.at1.send_and_verify("at+creg=2")
        test.dut.at1.send_and_verify("at+cereg=2")
        test.dut.at1.send_and_verify("at+cgreg=2")

        test.dut.at1.send("at+cfun=4")
        test.dut.at1.wait_for("\+C[EG]?REG: 0")
        test.expect("REG: 0" in test.dut.at1.last_response)

        test.sleep(5)

        test.dut.at1.send("at+cfun=1")
        test.dut.at1.wait_for("\+C[EG]?REG: 1")

        test.expect("REG: 1" in test.dut.at1.last_response)


    def cleanup(test):
        pass

if "__main__" == __name__:
    unicorn.main()

