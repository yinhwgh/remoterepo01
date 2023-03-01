# responsible: duangkeo.krueger@thalesgroup.com
# author: duangkeo.krueger@thalesgroup.com
# location: Berlin
# TC0000000.001
# JIRA: KRAKEN-362
# LM0008013.001

import unicorn
import re
from core.basetest import BaseTest
from dstl.embedded_system.linux.application import dstl_embedded_linux_upload_script
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_script

from dstl.auxiliary.init import dstl_detect
class Test(BaseTest):
    
    def setup(test):
        test.require_plugin('adb')
        test.dut.dstl_detect()

    def run(test):
        file = ['/usr/bin/pulseaudio',
                '/usr/bin/pacat',
                '/usr/bin/pacmd',
                '/usr/bin/pactl',
                'usr/bin/padsp']
        expected_permission = '-rwxr-xr-x'
        for i in range(len(file)) :
            res = test.dut.adb.send_and_receive("find "+ file[i])
            test.log.info("Result: " + res)
            if (test.dut.adb.last_retcode == 0):
                res = test.dut.adb.send_and_receive("ls -l " + file[i])
                data = res[0:10]
                test.log.info("Current File Permission : " + data)
                test.log.info("Expected Permission: " + expected_permission)
                if data == expected_permission :
                    test.expect(True)
                else :
                    test.expect(False)
            else :
                test.expect(False)




    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
