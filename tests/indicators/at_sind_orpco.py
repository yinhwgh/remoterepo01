#author: christian.gosslar@thalesgroup.com
#location: Berlin
#LM0004044.001 - TC0094485.001

testcase_id = "LM0004044.001 - TC0094485.001"

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module

class Test(BaseTest):
    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.log.com("***** " + testcase_id + " *****")
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.dut.dstl_get_bootloader()
        test.dut.dstl_check_c_revision_number()
        test.dut.dstl_collect_module_info()
        test.dut.devboard.send_and_verify("mc:asc0cfg=off", ".*O.*")
        pass

    def run(test):
        test.log.step('Step 1.0: read write command without PIN')
        # ==============================================================

        test.log.step('Step 1.1: check is restart is needed?')
        test.dut.at1.send_and_verify("at+CPIN?",".*O.*")
        if ("REDAY" in test.dut.at1.last_response):
             test.log.info("restart needed, PIN was enter before")
             test.expect(test.dut.dstl_restart())
        # SIM PIN must be active
        test.dut.at1.send_and_verify("AT+CPIN?", "OK")
        res = test.dut.at1.last_response
        if "READY" in res:
            # check if SIM PIN is active
            test.dut.dstl_lock_sim()
        else:
            test.log.info("SIM PIN is active")


        test.log.step('Step 1.2: check command without PIN')
        # ==============================================================

        test.expect(test.dut.at1.send_and_verify('at+CMEE=2'))
        test.expect(test.dut.at1.send_and_verify('at^SIND=?', '.*,\\(orpco,\\)(0-1\\)\\),.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^SIND?', '.*,\\SIND: orpco,0.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^SIND=orpco,2', '.*,\\SIND: orpco,0.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^SIND=orpco', '.*,CME ERROR: invalid index.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^SIND=orpco,1', '.*,\\SIND: orpco,1.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^SIND=orpco,2', '.*,\\SIND: orpco,1.*OK.*'))

        test.log.step('Step 2.0: read write command with PIN')
        # ==============================================================
        test.expect(test.dut.dstl_enter_pin())

        test.expect(test.dut.at1.send_and_verify('at^SIND=?', '.*,\\(orpco,\\)(0-1\\)\\),.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^SIND?', '.*,\\SIND: orpco,1.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^SIND=orpco,2', '.*,\\SIND: orpco,1.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^SIND=orpco', '.*,CME ERROR: invalid index.*OK.*'))

        test.log.step('Step 3.0: check setting after restart')
        # ==============================================================
        test.expect(test.dut.dstl_restart())

        test.expect(test.dut.at1.send_and_verify('at+CMEE=2'))
        test.expect(test.dut.at1.send_and_verify('at^SIND=?', '.*,\\(orpco,\\)(0-1\\)\\),.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^SIND?', '.*,\\SIND: orpco,0.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^SIND=orpco,2', '.*,\\SIND: orpco,0.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^SIND=orpco', '.*,CME ERROR: invalid index.*OK.*'))

        test.log.step('Step 4.0: check setting after restart and SIM PIN was entered')
        # ==============================================================
        test.expect(test.dut.dstl_enter_pin())

        test.expect(test.dut.at1.send_and_verify('at^SIND=?', '.*,\\(orpco,\\)(0-1\\)\\),.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^SIND?', '.*,\\SIND: orpco,1.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^SIND=orpco,2', '.*,\\SIND: orpco,0.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^SIND=orpco', '.*,CME ERROR: invalid index.*OK.*'))

    def cleanup(test):

        test.log.com(' ')
        test.log.com('****  log dir: ' + test.workspace + ' ****')

        test.log.com(' ')
        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')
        pass

if '__main__' == __name__:
    unicorn.main()
