#responsible: matthias.reissner@thalesgroup.com
#location: Berlin
#TC0000001.001

import unicorn
from core.basetest import BaseTest

import os
import subprocess
from fcntl import *

#from junit_xml import TestSuite, TestCase

#from dstl.auxiliary.devboard import devboard
from dstl.auxiliary import init
#from dstl.auxiliary import restart_module
#from dstl.network_service import attach_to_network


class Test(BaseTest):
    """ Test example for devboard DSTL methods   """

    def setup(test):
        test.log.step("Stage 1 Module hard reset")

        test.dut.devboard.send_and_verify("mc:vbatt")   # dummy command in case McTest is not responding on first cmd
        test.dut.devboard.send_and_verify("mc:vbatt")
        test.dut.devboard.send_and_verify("mc:vbatt=off")
        test.sleep(10)
        test.dut.devboard.send_and_verify("mc:vbatt=on")
        test.dut.devboard.send_and_verify("mc:igt=555")
        test.sleep(25)

        test.dut.dstl_detect()
        #pass

    def run(test):

        test.log.step("Stage 2 test_swup")
        #test.expect(restart_module.dstl_restart(test.dut))
        test.expect(test.dut.at1.send_and_verify("at"))
        test.dut.at1.send_and_verify("ati")
        test.dut.at1.send_and_verify("ati51")

        test.dut.at1.close()


        #test.test_cases = []
        #tc = TestCase("Test FW seup", "swup", 12, "glinswup -f=exs82.usf -p=/dev/d2Asc0 -b=460800")
        #test.test_cases.append(tc)

        #current_dir = os.getcwd()
        #test.log.info("Current dir: " + current_dir)

        #with open("/root/jenkins/workspace/Serval_3_ST_pipe/unicorn/result_swup_.xml", "w") as f:
        #    ts = TestSuite("ST auto stage 1", test.test_cases)
        #    TestSuite.to_file(f, [ts], prettyprint = True)
            #test.log.info(TestSuite.to_xml_string([ts]))

        test.log.info("dut port: " + test.dut.at1.port)

        glinswup_path = os.path.join(os.getcwd(), "..", "..", "glinswup", "glinswup_exs82", "src")
        test.log.info("Start swup from: " + glinswup_path)

        fw_file_path = os.path.join(os.getcwd(), "..", "fw", "exs82.usf")
        test.log.info("USF file path: " + fw_file_path)

        #proc = subprocess.Popen(["glinswup_EXS82", "/dev/" + cdc_dev, "start"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell = False)
        test.log.info("Running swup cmd: cd " + glinswup_path + " && ./glinswup_EXS82 -p=" + test.dut.at1.port + " -f=" + fw_file_path + " -b=460800")
        ret = os.system("cd " + glinswup_path + " && ./glinswup_EXS82 -p=" + test.dut.at1.port + " -f=" + fw_file_path + " -b=460800")
        #ret = 1
        if (ret == 0):
            test.log.info("FW Swup successful!")
            test.sleep(20)
            test.dut.at1.open()
            test.dut.at1.send_and_verify("at")
            test.expect(test.dut.at1.send_and_verify("ati"))
            test.expect(test.dut.at1.send_and_verify("ati51"))
            test.expect(test.dut.at1.send_and_verify("at^cicret=swn"))
        else:
            test.log.warning("FW Swup not successful! " + str(ret))
            test.expect(False, critical = True)

        pass

    def cleanup(test):
        pass

if "__main__" == __name__:
    unicorn.main()
