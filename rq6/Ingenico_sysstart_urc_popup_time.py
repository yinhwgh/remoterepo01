# responsible hongwei.yin@thalesgroup.com
#location: Dalian
#TC0108061.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
import time

class Test(BaseTest):
    """
     TC0108061.001-Ingenico_SYSSTART_URC_Popup_Time
    """
    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        test.expect(test.dut.at1.send_and_verify("at+cfun=1,1", "OK"))
        starttime = time.time()
        test.dut.at1.wait_for('^SYSSTART', 0.1)
        test.sleep(2)
        test.dut.at1.wait_for('^SYSSTART', 0.1)
        test.sleep(5)
        test.dut.at1.wait_for('^SYSSTART', 0.1)
        result = False
        while not result:
            test.sleep(1)
            test.dut.at1.send("at")
            result = test.dut.at1.wait_for('^SYSSTART', 0.1)
        endtime = time.time()
        test.log.info("module restart uses {:.1f} seconds.".format(endtime-starttime))
        test.expect(test.dut.at1.send_and_verify("at", "OK"))

    def cleanup(test):
        pass

if "__main__" == __name__:
    unicorn.main()