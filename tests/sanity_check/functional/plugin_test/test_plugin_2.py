#responsible: baris.kildi@thalesgroup.com
#location: Berlin

import unicorn
from core.basetest import BaseTest
import os

class Test(BaseTest):
    """simdata.cfg file will be modified by used sim_ID"""


    def setup(test):
        pass

    def run(test):
        test.log.info("Check if empty simdata.cfg file is properly filled by used sim_ID")
        test.dut.at1.send_and_verify("at")
        test.expect("OK" in test.dut.at1.last_response)

        current_dir = os.getcwd()
        test.log.info("Here we are " + current_dir)
        os.chdir(os.path.join("config"))
        file = open("simdata.cfg", 'r')
        contents = file.readlines()
        found_pin1 = 0
        for line in contents:
            if ("pin1" in line):
                test.log.info("config/simdata.cfg file is automatically filled based on entries from WebImacs")
                test.log.info("Found pin1 in simdata file: " + line)
                test.expect("pin1" in line)
                found_pin1 = 1
        if (found_pin1 == 0):
            raise Exception("Something went wrong please check your WebImacs plugin")
        file.close()

        os.getcwd()
        current_dir = os.getcwd()
        test.log.info("Go back to unicorn home directory ")
        os.chdir("..")
        test.log.info(current_dir)

    def cleanup(test):
         pass


if "__main__" == __name__:
    unicorn.main()
