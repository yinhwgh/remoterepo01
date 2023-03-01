#responsible: lijuan.li@thalesgroup.com
#location: Beijing
#TC

import unicorn

from core.basetest import BaseTest

from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network


class TpUndervoltageSurveillance(BaseTest):
    def setup(test):
        #        test.dut.dstl_restart()
        #        test.sleep(5)
        pass

    def run(test):
        test.log.info("1. test: check current voltage ")
        test.expect(test.dut.devboard.send_and_verify("mc:vbatt", ".*OK.*"))
        voltage= 3500
        while(test.dut.at1.wait_for(".*Undervoltage.*")== False):
          test.expect(test.dut.devboard.send_and_verify("mc:vbatt", ".*OK.*"))
          test.expect(test.dut.devboard.send_and_verify("mc:vbatt="+str(voltage), ".*OK.*"))
          test.expect(test.dut.at1.send_and_verify("at", ".*OK.*"))
          voltage= voltage-100

        test.expect(test.dut.devboard.send_and_verify("mc:vbatt=3500", ".*OK.*"))

    def cleanup(test):
        pass

if (__name__ == "__main__"):
    unicorn.main()
