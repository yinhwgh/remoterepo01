# responsible: marek.mlodzianowski@globallogic.com
# location: Wroclaw
# TC0000001.001

import unicorn
from core.basetest import BaseTest


class Test(BaseTest):
    def setup(test):
        pass


    def run(test):
        if not test.dut.adb.send_and_verify("ls -la /home/", "testfile"):
            test.dut.adb.send_and_receive("touch /home/testfile")
            test.log.info("touch rc: {}".format(test.dut.adb.last_retcode))
            if test.dut.adb.last_retcode is not 0:
                test.expect(True)
            else:
                test.dut.adb.send_and_receive("rm /home/testfile")
                test.expect(False)
        else:
            test.expect(False)
        pass


    def cleanup(test):
        pass

