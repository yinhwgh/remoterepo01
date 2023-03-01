#responsible: fang.liu@thalesgroup.com
#location: Berlin

#!/usr/bin/env unicorn
"""
Unicorn tests.scrum.DualModemSwitch.py module;

Please be awarded, some values in "local.cfg" have to be changed according to the OS that you perfom the TC:
[Windows]
dut_at1 = dut_usb_m
dut_sim = LTExxx
dut_usb_m = COMxx

[Linux]
dut_at1 = dut_usb_m
dut_sim = LTExxx
dut_usb_m = /dev/ttyACM0
"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import *
from dstl.security.lock_unlock_sim import *
from dstl.network_service.register_to_network import *
from dstl.auxiliary import init
"""
Here we need the dstl module, which will provide some basic operation for the module such as:
"restart", "Lock and unlock pin code", "register to network".

Check that a system with dual modem properly switches between them:

        (1) Verizon provider configurations should use the verizon modem image, the HW model should be -US variant.
        (2) All other provider configurations should use the default modem image.
        (3) If the module starts with a modem image that does not correspond to the active profile, it must change it automatically to the target image (via automatic configuration and restart)
The test script is designed to retest a defect of "Bobcat_PLPS9-X_230", please refer to IPIS100295245 for details.

"""


class Test(BaseTest):

    def setup(test):
        test.log.info("***********The general information of the module**************")
        test.dut.at1.send_and_verify("at^cicret=swn", ".*OK.*")
        test.dut.at1.send_and_verify("at^sinfo?", ".*OK.*")
        test.dut.at1.send_and_verify("at^sos=bootloader/info", ".*OK.*")

        test.dut.dstl_detect()


    def run(test):
        test.log.info("---------1. Set \"AutoSelection\" to off, and set default provider to \"verizonus\"----------")
        test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/AutoSelect,off", ".*OK.*")
        test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/Cfg,\"verizonus\"", ".*OK.*")

        test.log.info("---------2. Restart the module at first;----------")
        test.dut.dstl_restart()
        test.dut.at1.send_and_verify("at+cfun=1", ".*SYSSTART.*")

        test.dut.at1.wait_for("+CIEV: prov,1,\"verizonus\"", timeout=90)

        test.log.info(
            "---------3. Check the last two lines in the response of \"ati61\"----------"
            "The following two lines should be inclued: "
            "(1)S30960 - S5070 - A100.VERIZONUS"
            "(2)MIMG VERIZON")
        test.dut.at1.send_and_verify("ati61", ".*OK.*")
        print(test.dut.at1.last_response)
        test.expect("A100.VERIZONUS" in test.dut.at1.last_response)
        test.expect("MIMG VERIZON" in test.dut.at1.last_response)

        test.log.info(
            "----------4. Set it back to the default values:"
            "(1)S30960-S5070-A100.FALLBUS"
            "(2)MIMG DEFAULT")
        test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/Cfg,\"fallbus\"", ".*OK.*")
        test.dut.dstl_restart()

        test.dut.at1.send_and_verify("at+cfun=1", ".*SYSSTART.*")

        test.dut.at1.wait_for("+CIEV: prov,1,\"fallbus*\"", timeout=90)
        test.dut.at1.send_and_verify("ati61", ".*OK.*")
        print(test.dut.at1.last_response)
        test.expect("A100.FALLBUS" in test.dut.at1.last_response)
        test.expect("MIMG DEFAULT" in test.dut.at1.last_response)

    def cleanup(test):
        test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/AutoSelect,on", ".*OK.*")


if "__main__" == __name__:
    unicorn.main()
	