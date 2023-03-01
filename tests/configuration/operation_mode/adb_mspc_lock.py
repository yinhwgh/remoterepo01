#responsible: fang.liu@thalesgroup.com
#location: Berlin
#TC

import unicorn
import os
import time
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import *

class Test(BaseTest):
    """
        Basic automatic test script for ADB security.
    """

    def __init__(self):
        super().__init__()
        self.dut = None

    def setup(test):
        # query product version with ati""
        test.dut.at1.send_and_verify("ati", ".*")

        # log the message that module returned (last_response) as info
        test.log.info(test.dut.at1.last_response)

        # query product version with at^cicret
        test.dut.at1.send_and_verify("at^cicret=\"swn\"")

        # log the message that module returned (last_response) as info
        test.log.info(test.dut.at1.last_response)

        # query product version with at^cicret, append response to current last_response value
        # last_response should contain now output from both recently run commands
        test.dut.at1.send_and_verify("at^cicret=\"swn\"", append=True)
        test.log.info(test.dut.at1.last_response)

        # Query the identification  of the current module with "at^sinfo?"
        test.dut.at1.send_and_verify("at^sinfo?")
        test.log.info(test.dut.at1.last_response)

    def run(test):
        """

        :return:
        """
        #Enable ADB device
        test.dut.at1.send_and_verify("At^scfg=\"serial/interface/adb\",enabled", ".*OK.*")

        # This is another way to lock MSPC by giving an incorrect password.
        test.dut.at1.send_and_verify("AT^SCFG=\"security/passwd\",\"MSPC\",\"123456\"", ".*ERROR.*")
        time.sleep(300)

        # Check if MSPC  is locked  or  not, and then restart the mode and check ADB mode.
        test.dut.at1.send_and_verify("at^SCFG=\"security/passwd\",\"MSPC\"", ".*\"0\",\"0\".*")
        test.log.info(test.dut.at1.last_response)

        test.dut.at1.send_and_verify("at+cfun=1,1")
        test.log.info(test.dut.at1.last_response)
        time.sleep(180)

        test.dut.at1.send_and_verify("at+cfun=1,1")
        test.log.info(test.dut.at1.last_response)
        time.sleep(180)


        # ADB device shoule be in secure mode after the first restart.
        test.dut.at1.send_and_verify("At^scfg=\"serial/interface/adb\"",  "enabled")
        test.log.info(test.dut.at1.last_response)

        test.dut.at1.send_and_verify("AT^SCFG=\"Serial/Interface/Adb/Mode\"", ".*secure.*")
        test.log.info(test.dut.at1.last_response)
        time.sleep(20)
        # Then unlock the MSPC  and  enable ADB device (root mode).
        test.dut.at1.send_and_verify("AT^SCFG=\"security/passwd\",\"MSPC\",975004", ".*OK.*")
        test.dut.at1.send_and_verify("AT^SCFG=\"Serial/Interface/Adb/Mode\", \"root\"", ".*OK.*")
        test.dut.at1.send_and_verify("AT^SCFG=\"MEopmode/coredump\",1,1,\"PowerOff\"", ".*OK.*")

        countnum = 16
        for i in range(16):
            # Unlock the MSPC
            test.dut.at1.send_and_verify("AT^SCFG=\"security/passwd\"", ".*OK.*")
            checkres = test.dut.at1.last_response
            if str(countnum) in checkres:
                countnum = countnum - 1
            else:
                test.log.error('The result is not expected, please check if the parameter "mspcttl" is not correct one.')
                test.log.info(checkres)

            # Enable the ADB mode on the module, and check if it has the  root permisstion.
            test.dut.at1.send_and_verify("AT^SCFG=\"Serial/Interface/Adb/Mode\"", ".*root.*")
            # Enable coredump
            test.dut.at1.send_and_verify("AT^SCFG=\"MEopmode/coredump\"", ".*OK.*")
            test.dut.dstl_restart()

        # Make sure  MSPC is locked  after 16 times' restart.
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Serial/Interface/Adb/Mode\"", ".*secure.*"))

    def cleanup(test):
        """Cleanup method.

        Steps to be executed after test run steps.
        """
        test.dut.dstl_restart()

if "__main__" == __name__:
    unicorn.main()
