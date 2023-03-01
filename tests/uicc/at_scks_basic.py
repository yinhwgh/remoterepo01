#responsible: yunhui.zhang@thalesgroup.com
#location: Beijing
#TC0088315.001 - TpAtScksBasic


import unicorn
import time
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.security import lock_unlock_sim
from dstl.auxiliary.devboard import *



class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_lock_sim()
        time.sleep(2)
        test.dut.dstl_restart()

    def run(test):
        test.log.info('**** TpAtScksBasic - Start ****')
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*SIM PIN.*OK"))
        for i in range(2):
            test.log.info('****  '+('1st 'if (i == 0) else '2nd ') +'test: Check read/write and exec command with' +('out' if (i==0) else'')+' PIN****')
            test.expect(test.dut.at1.send_and_verify("AT^SCKS=?", ".*SCKS: \(0-1\)\s+OK\s+"))
            test.expect(test.dut.at1.send_and_verify("AT^SCKS?", ".*SCKS: {},1\s+OK\s+".format(i)))
            test.expect(test.dut.at1.send_and_verify("AT^SCKS=1", ".*OK*."))
            test.expect(test.dut.at1.send_and_verify("AT^SCKS?", ".*SCKS: 1,1\s+OK\s+"))
            test.dut.dstl_remove_sim()
            test.log.info('**** Wating for "^SCKS: 0" URC ****')
            test.expect("^SCKS: 0" in test.dut.at1.last_response)
            test.dut.dstl_insert_sim()
            test.log.info('**** Wating for "^SCKS: 1" URC ****')
            test.expect("^SCKS: 1" in test.dut.at1.last_response)
            test.expect(test.dut.dstl_enter_pin())

        test.log.info('**** Test end ***')

    def cleanup(test):
        test.dut.dstl_lock_sim()
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK*."))




if (__name__ == "__main__"):
    unicorn.main()
