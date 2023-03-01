#responsible: baris.kildi@thalesgroup.com
#location: Berlin

import unicorn
from core.basetest import BaseTest
import os, re
import glob
from pathlib import Path
import subprocess
from dstl.network_service import register_to_network
from dstl.auxiliary import tracing

class Test(BaseTest):
    """ start tracing, call some at-commands
        and disable tracing
    """

    def setup(test):
        pass

    def run(test):        
        
        test.log.step("Start tracing and call some at-commands")
        test.dut.dstl_enter_pin()
        test.expect(test.dut.at1.send_and_verify('AT+CREG=2', expect="OK"))
        test.expect(test.dut.at1.send_and_verify('AT+COPS=2', expect="OK"))
        test.expect(test.dut.at1.send_and_verify('AT+COPS=0', expect="OK"))
        test.sleep(15)
        test.expect(test.dut.at1.send_and_verify('AT^SMONI', expect="OK"))


        test.log.step("Get the path of the log directory.")
        current_dir = os.getcwd()
        test.log.info("Current dir: " + current_dir)
        #log_dir = r'' + current_dir + r"\logs"
        log_dir = os.path.join(current_dir, "logs")
        test.log.info("Log dir: " + log_dir)
        test.log.step("Get the path of the latest qmdl file")

        try:
            latest_file = sorted([filename for filename in Path(log_dir).glob('**/*.qmdl')],
                             key=os.path.getmtime, reverse=True)[0]
            test.log.info("Last dir: " + str(latest_file))
            if latest_file.exists():
                test.log.info("Trace file successfully captured")
        except FileNotFoundError:
                test.log.info("Trace file could not written. Check if tracing is enabled.")
        
        
        os.chdir("plugins")
        test.log.step("Disable tracing")
        dirpath = os.getcwd()
        test.log.info("Your current directory is : " + dirpath)
        file = open("enabled.cfg", "w")
        file.write("## add enabled plugins here - each in separate line\nwebimacs\ntemplate")
        file.close()
        os.chdir("..")

    def cleanup(test):
         pass


if "__main__" == __name__:
    unicorn.main()
