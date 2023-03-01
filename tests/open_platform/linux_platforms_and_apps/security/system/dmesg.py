# responsible: lukasz.bednarz@globallogic.com
# location: Wroclaw
# TC0000001.001 template_os

import unicorn
from core.basetest import BaseTest



class Test(BaseTest):

    def setup(test):
        pass

    def run(test):
        STR="test_dmesg"
        
        test.log.info("Check dmesg with logwrapper -k tool")
        
        ret1 = test.dut.adb.send_and_receive("dmesg -c")
        if( test.dut.adb.last_retcode == 0):
            test.expect(True)
        else:
            test.log.error("last_retcode unequal 0")
            test.expect(False)
        ret1 = test.dut.adb.send_and_receive(f"echo {STR} > /dev/kmsg")
        if( test.dut.adb.last_retcode == 0):
            test.expect(True)
        else:
            test.log.error("last_retcode unequal 0")
            test.expect(False)
        ret1 = test.dut.adb.send_and_receive(f"dmesg | grep -q {STR}")
        if( test.dut.adb.last_retcode == 0):
            test.expect(True)
        else:
            test.log.error("last_retcode unequal 0")
            test.expect(False)



    def cleanup(test):
        pass