#responsible: baris.kildi@thalesgroup.com
#location: Berlin

import unicorn
import os
from core.basetest import BaseTest
from dstl.auxiliary import init


class Test(BaseTest):
    """ Test will be triggered by other test case called
    test_start_framework.py
    """

    def setup(test):
        pass

    def run(test):
        test.dut.dstl_detect()
        test.log.info("If this test starts, test_start_logging was successful!")
        test.dut.at1.send_and_verify("at")
        test.expect("OK" in test.dut.at1.last_response)
        test.sleep(1)
        test.dut.at1.send("at+cimi")
        test.sleep(1)
        dirpath = os.getcwd()
        test.log.info("Your current directory is : " + dirpath)

        val = test.foo_start_framework
        test.log.info("Reading parameter from local config file: foo_start_framework=" + val)
        test.expect("bar" in val)

        local_fd = open(os.path.join('config', 'local_Cougar.cfg'), 'r')
        local_val = local_fd.readlines()
        for line in local_val:
            if ("foo_start_framework" in line):
                test.log.info("found foo in local config file: " + line)
                test.expect(True)
        local_fd.close()

    def cleanup(test):
         pass


if "__main__" == __name__:
    unicorn.main()
