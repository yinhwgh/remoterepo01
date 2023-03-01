#responsible: baris.kildi@thalesgroup.com
#location: Berlin

import unicorn
import subprocess
import os
from core.basetest import BaseTest
from dstl.auxiliary import init

class Test(BaseTest):
    """ Call within test case any other test case by using the non
    default local*.cfg file
    """

    def setup(test):
        pass

    def run(test):
        test.log.info("Creating local config file for testing framework start parameter")
        test.sleep(1)
        test.dut.dstl_detect()
        test.sleep(1)
        test.dut.at1.send_and_verify("at")
        test.expect("OK" in test.dut.at1.last_response)
        test.sleep(1)
        test.dut.at1.close()
        os.getcwd()
        #os.chdir("..\..\..")
        dirpath = os.getcwd()

        test.log.info("Your current directory is : " + dirpath)

        # copy local.cfg to cougar_local.cfg
        test.log.info("Copy local config.cfg to local_Cougar.cfg")
        local_fd = open(os.path.join('config', 'local.cfg'), 'r')
        local_cougar_fd = open(os.path.join('config', 'local_Cougar.cfg'), 'w')
        local_val = local_fd.read()

        local_cougar_fd.write(local_val)
        local_cougar_fd.write("\n\nfoo_start_framework=bar\n")
        local_fd.close()
        local_cougar_fd.close()

        local_fd = open(os.path.join('config', 'local_Cougar.cfg'), 'r')
        local_val = local_fd.readlines()
        for line in local_val:
            if ("foo_start_framework" in line):
                test.log.info("found foo in local config file: " + line)
                test.expect(True)
        local_fd.close()

        #test.log.info("Exec: python\\python.exe unicorn.py tests\\sanity_check\\framework_start\\test_start_framework_2.py -l config\\local_Cougar.cfg")
        #myCmd = ('python\\python.exe unicorn.py tests\\sanity_check\\framework_start\\test_start_framework_2.py -l config\\local_Cougar.cfg')
        #ret = subprocess.call(myCmd, shell='TRUE')
        #test.log.info("Ret val subprocess: " + str(ret))

    def cleanup(test):
         pass


if "__main__" == __name__:
    unicorn.main()
