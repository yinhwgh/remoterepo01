#responsible: fang.liu@thalesgroup.com
#location: Berlin

import unicorn
import os
import time
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import *
from dstl.auxiliary import init

class Test(BaseTest):
    """
        Basic automatic test script for ADB security.

    Feature:    BOB-????
                LM000????  //
    Products:   Bob2xy
    Intention:  Basic automatic test script for ADB security.
    End state:  TC ends without PIN1
    Devices:    DUT_MDM


    """

    def setup(test):

        test.dut.dstl_detect()

        # query product version with ati""
        test.dut.at1.send_and_verify("ati", ".*")

        # query product version with at^cicret
        test.dut.at1.send_and_verify("at^cicret=\"swn\"")

        # Query the identification  of the current module with "at^sinfo?"
        test.dut.at1.send_and_verify("at^sinfo?")

    def run(test):
        """

        :return:
        """
        test.log.info("Step 1: Enable ADB device%%%%%%%%%%%")
        test.dut.at1.send_and_verify("At^scfg=\"serial/interface/adb\",enabled", ".*OK.*")
        test.sleep(5)

        test.log.info("Step 2: This is another way to lock MSPC by giving an incorrect password.")
        test.dut.at1.send_and_verify("AT^SCFG=\"security/passwd\",\"MSPC\",\"123456\"", ".*ERROR.*")
        time.sleep(300)

        test.log.info("Step 3: Check if MSPC is locked or not, and then restart the mode and check ADB mode.")
        test.dut.at1.send_and_verify("at^SCFG=\"security/passwd\",\"MSPC\"", ".*\"0\",\"0\".*")
        test.log.info(test.dut.at1.last_response)

        test.log.info("Step 4: Restart module twice.")
        test.dut.dstl_restart()
        test.log.info(test.dut.at1.last_response)

        test.log.info("ADB device should be in secure mode after the restart.")
        test.dut.at1.send_and_verify("At^scfg=\"serial/interface/adb\"", "enabled")
        test.log.info(test.dut.at1.last_response)
        test.sleep(5)
        test.dut.at1.send_and_verify("AT^SCFG=\"Serial/Interface/Adb/Mode\"", ".*secure.*")
        test.log.info(test.dut.at1.last_response)
        test.sleep(5)

        test.log.info("Step 5: Then unlock the MSPC and enable ADB device (root mode).")
        test.dut.at1.send_and_verify("AT^SCFG=\"security/passwd\",\"MSPC\",975004", ".*OK.*")
        test.dut.dstl_restart()

        test.dut.at1.send_and_verify("AT^SCFG=\"Serial/Interface/Adb/Mode\", \"root\"", ".*OK.*")
        test.sleep(3)
        test.dut.at1.send_and_verify("AT^SCFG=\"MEopmode/coredump\",1,1,\"PowerOff\"", ".*OK.*")
        test.sleep(3)

        test.log.info("Step 6: Check if the value of \"mspcttl\" will minus 1 after each restart, and after 16 times restart, MSPC will be locked.")
        countnum = 15
        for i in range(15):
            # Unlock the MSPC
            test.dut.at1.send_and_verify("AT^SCFG=\"security/passwd\"", ".*OK.*")

            checkres = test.dut.at1.last_response
            if str(countnum) in checkres:
                countnum = countnum - 1
            else:
                test.log.error('The result is not expected, please check if the parameter "mspcttl" is the correct one.')
                test.log.info(checkres)

            # Enable the ADB mode on the module, and check if it has the  root permisstion.
            test.dut.at1.send_and_verify("AT^SCFG=\"Serial/Interface/Adb/Mode\"", ".*root.*")
            test.sleep(5)
            test.dut.dstl_restart()
            time.sleep(20)

        test.log.info("Make sure MSPC is locked after 16 times' restarts.")
        test.dut.at1.send_and_verify("AT^SCFG=\"Serial/Interface/Adb/Mode\"", ".*secure.*")
        test.expect("secure" in test.dut.at1.last_response)

    def cleanup(test):
        """Cleanup method.

        Steps to be executed after test run steps.
        """
        pass


if "__main__" == __name__:
    unicorn.main()
