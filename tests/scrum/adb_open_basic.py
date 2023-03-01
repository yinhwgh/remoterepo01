#responsible: fang.liu@thalesgroup.com
#location: Berlin

import unicorn
import os
import re
from dstl.auxiliary.restart_module import *
from core.basetest import BaseTest
from dstl.auxiliary import init

class Test(BaseTest):
    """
        Basic automatic test script for ADB security.
    """

    def setup(test):

        test.dut.dstl_detect()
        test.dut.at1.send_and_verify("ate1", ".*")

        # query product version with at^cicret, append response to current last_response value
        # last_response should contain now output from both recently run commands
        test.dut.at1.send_and_verify("at^cicret=\"swn\"", ".*OK.*")
        test.log.info(test.dut.at1.last_response)

        # Query the identification  of the current module with "at^sinfo?"
        test.dut.at1.send_and_verify("at^sinfo?", ".*OK.*")
        test.log.info(test.dut.at1.last_response)

    def run(test):
        """

        :return:
        """
        test.log.info("Configure the ATC on the module to enable adb device.")
        test.dut.at1.send_and_verify("At^scfg=\"serial/interface/adb\",enabled", ".*OK.*")
        test.sleep(5)
        test.dut.at1.send_and_verify("AT^SCFG=\"security/passwd\",\"MSPC\",975004", ".*OK.*")
        test.sleep(5)
        test.dut.at1.send_and_verify("AT^SCFG=\"Serial/Interface/Adb/Mode\", \"root\"", ".*OK.*")
        test.sleep(5)
        test.dut.at1.send_and_verify("AT^SCFG=\"MEopmode/coredump\",1,1,\"PowerOff\"", ".*OK.*")
        test.sleep(5)
        """
        Restart the module
        """
        test.dut.dstl_restart()

        # Check the status of the MSPC
        test.dut.at1.send_and_verify("AT^SCFG=\"security/passwd\"", ".*OK.*")
        test.dut.at1.send_and_verify("AT^SCFG=\"Serial/Interface/Adb/Mode\"", ".*root.*")

        # Enable ADB device via "adb devices" on Ubuntu
        test.log.info('%%%%%Restart ADB device%%%%%')
        os.system('adb kill-server')
        test.sleep(5)
        test.log.info('%%%%%List all opening ADB device%%%%%%%\n')
        tmp = os.popen('adb devices -l').readlines()
        test.sleep(5)

        "#Filter all the devices' ID and then store in a list."
        pattern = '([a-zA-Z0-9]+)  +device'
        devices = []
        for line in tmp:
            searchObj = re.search(pattern, line)
            if searchObj:
                devices.append(searchObj.group(1))

        print("All the ADB devices are as follows:\n{}".format(devices))

        if len(devices) >= 1:
            test.log.info("%%%%%%Send a shell command to the module.%%%%%%")
            test.dut.adb.send_and_receive("hostname")
            test.expect("mdm" in test.dut.adb.last_response)

            # Disable the ADB device
            test.log.info("%%%%Kill the adb device%%%%")
            os.system('adb kill-server')
        else:
            test.log.error('It\'s failed to open ADB device, please check the device and environment again.')

        test.dut.dstl_restart()

    def cleanup(test):
        """Cleanup method.

        Steps to be executed after test run steps.
        """
        # Set the ADB mode back to 'secure'.
        test.dut.at1.send_and_verify("AT^SCFG=\"Serial/Interface/Adb/Mode\", \"secure\"", ".*OK.*")
        # Disable ADB device on the module.
        test.dut.at1.send_and_verify("At^scfg=\"serial/interface/adb\",disabled", ".*OK.*")


if "__main__" == __name__:
    unicorn.main()
