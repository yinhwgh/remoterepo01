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

    def setup(test):
        # query product version with ati""
        test.dut.at1.send_and_verify("ati", ".*")
        test.dut.at1.send_and_verify("ate1", ".*")
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
        test.dut.at1.send_and_verify("AT^SCFG=\"security/passwd\",\"MSPC\",975004", ".*OK.*")
        test.dut.at1.send_and_verify("AT^SCFG=\"Serial/Interface/Adb/Mode\", \"root\"", ".*OK.*")
        test.dut.at1.send_and_verify("AT^SCFG=\"MEopmode/coredump\",1,1,\"PowerOff\"", ".*OK.*")
        """
        Restart the module
        """
        #test.dut.at1.send_and_verify("at+cfun=1,1",".*OK.*")
        #time.sleep(180)

        for i in range(2):
            # Unlock the MSPC
            test.dut.at1.send_and_verify("AT^SCFG=\"security/passwd\"", ".*OK.*")
            # Enable the ADB mode on the module, and check if it has the  root permisstion.
            test.dut.at1.send_and_verify("AT^SCFG=\"Serial/Interface/Adb/Mode\"", ".*root.*")
            # Enable coredump
            test.dut.at1.send_and_verify("AT^SCFG=\"MEopmode/coredump\"", ".*OK.*")

            # Enable ADB device via "adb devices" on Ubuntu
            test.log.info('%%%%%Restart ADB device%%%%%')
            os.system('adb kill-server')
            time.sleep(60)
            test.log.info('%%%%%Opening ADB device%%%%%%%')
            tmp = os.popen('adb devices').readlines()

            if len(tmp) > 2:
                test.log.info('%%%%%ADB device is available now%%%%%')
                test.dut.adb.send_and_verify("ls -al", ".*")
                test.log.info(test.dut.adb.last_response)
            # Exit linux on the module
                test.dut.adb.send_and_verify("exit")
            # Disable the ADB device
                os.system('adb kill-server')
            else:
                test.log.error('It\'s failed to open ADB device, please check the device and evironment again.')


    def cleanup(test):
        """Cleanup method.

        Steps to be executed after test run steps.
        """
        # Set the ADB mode back to 'secure'.
        test.dut.at1.send_and_verify("AT^SCFG=\"Serial/Interface/Adb/Mode\", \"secure\"", ".*OK.*")
        # Disable ADB device on the module.
        test.dut.at1.send_and_verify("At^scfg=\"serial/interface/adb\",disabled", ".*OK.*")

        test.dut.dstl_restart()

if "__main__" == __name__:
    unicorn.main()
