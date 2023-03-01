# author: christoph.dehm@thalesgroup.com
# responsible: christoph.dehm@thalesgroup.com
# location: Berlin
# TC00000.000
# jira: BOB-4676
# feature: LM0003694.005, (LM0000380.001)

import unicorn
from core.basetest import BaseTest

#!/usr/bin/env unicorn
from dstl.auxiliary.init import dstl_detect
from dstl.miscellaneous.exit_history import dstl_read_latest_exit, dstl_clear_exit_history, dstl_read_specific_exit

class Test(BaseTest):



    '''
    The module Bobcat200_116 shows following different EXITs:
    AT^SEXIT=1	^EXIT:MPSS FATAL: qmi_dms_ext_svc.c:4007:AT^SEXIT = 0 MPSS FATAL: unknown reason (empty string found) panic in subsys modem:BYE
    AT^SEXIT=2	^EXIT:MPSS FATAL: qmi_dms_ext_svc.c:4007:AT^SEXIT = 1 MPSS FATAL: unknown reason (empty string found) panic in subsys modem:BYE
    AT^SEXIT=3	^EXIT:MPSS FATAL: qmi_dms_ext_svc.c:4007:AT^SEXIT = 2 panic in subsys modem:BYE
    AT^SEXIT=10	^EXIT:SYS_oem_panic called!:BYE
    AT^SEXIT=11	^EXIT:SYS_oem_panic called!:BYE
    AT^SEXIT=12	^EXIT:Fatal exception:BYE
    AT^SEXIT=13	^EXIT:user_fault: grcd, pid 1201, pc b6e3a8dc, lr b6e3a660, addr 00000004, fsr 0x05, code 0x30001:BYE
    AT^SEXIT=14	^EXIT:user_fault: grcd, pid 1203, pc b6e58900, lr b6e58660, addr 00000001, fsr 0x05, code 0x30001:BYE
    AT^SEXIT=15	^EXIT:user_fault: grcd, pid 1205, pc 00000000, lr b6e53928, addr 00000000, fsr 0x80000005, code 0x30001:BYE
    '''




    def CheckForSpecificExitText(test, num_exit, text_of_exit):
        """
        check if a given EXIT-text is on the given index in the EXIT list
        :return: true/false
        """
        test.log.info("\n --- check if EXIT with msg '{}' exists on pos {} ----".format(text_of_exit, num_exit))
        idx, latest, text = dstl_read_latest_exit(test.dut, num_exit)
        if text_of_exit in text:
            test.expect(True)
            return True
        else:
            test.log.error("##> msg '{}' NOT found on pos {}.".format(num_exit, text_of_exit))
            test.log.error("    instead found: {}".format(text))
            test.expect(False, critical=True)
            return False


    def CheckForExit(test, num_of_expected_exits):
        """
        check if given number of EXITs are shown listed
        :return: true/false
        """
        test.log.info("\n --- check if EXIT exists: ----")
        exits_in_list, latest, text = dstl_read_latest_exit(test.dut)
        if num_of_expected_exits == exits_in_list:
            test.expect(True)
            return True
        else:
            test.log.error("##> EXIT history should show {} instead of {} EXITs in list.".format(1, sum))
            test.expect(False, critical=True)
            return False


    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - START *****')
        dstl_detect(test.dut)
        pass

    def run(test):
        test.log.com('*** 0. set some prerequisite  ***')
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=MEopMode/CoreDump,0,1,Restart", ".*OK.*"))

        test.log.com('*** 1. clear EXIT History and check for number of entries  ***')
        dstl_clear_exit_history(test.dut)
        sum, ret, text = dstl_read_latest_exit(test.dut)
        if sum > 0:
            test.log.error("##> EXIT history should be empty.")
            test.expect(False, critical=True)
        else:
            test.expect(True)
            test.log.info("##> EXIT history is empty, fine.")


        test.log.com('*** 2. create some EXITs and check for latest one  ***')
        test.expect(test.dut.at1.send_and_verify("AT^SEXIT=0", "^.*ERROR.*$"))
        test.expect(test.dut.at1.send_and_verify("AT^SEXIT=1", wait_for=".*SYSSTART.*", expect="", timeout=75))
        test.CheckForExit(1)

        test.expect(test.dut.at1.send_and_verify("AT^SEXIT=2", wait_for=".*SYSSTART.*", expect="", timeout=75))
        test.CheckForExit(2)

        test.expect(test.dut.at1.send_and_verify("AT^SEXIT=3", wait_for=".*SYSSTART.*", expect="", timeout=75))
        test.CheckForExit(3)


        test.log.com('*** read EH and check for latest entry  ***')

        sum, ret, text = dstl_read_latest_exit(test.dut)
        if "SEXIT = 2" in text:
            test.expect(True)
            test.log.info("last entry shows correct EXIT text.")
        else:
            test.log.error("last entry does not show correct EXIT text - 'SEXIT = 2' was expected!")
            test.expect(False, critical=True)


        test.log.com('*** 3. fill up the list to the maximum number of entries  ***')
        test.expect(test.dut.at1.send_and_verify("AT^SEXIT=10", wait_for=".*SYSSTART.*", expect="", timeout=75))
        test.expect(test.dut.at1.send_and_verify("AT^SEXIT=11", wait_for=".*SYSSTART.*", expect="", timeout=75))
        test.expect(test.dut.at1.send_and_verify("AT^SEXIT=12", wait_for=".*SYSSTART.*", expect="", timeout=75))
        test.expect(test.dut.at1.send_and_verify("AT^SEXIT=13", wait_for=".*SYSSTART.*", expect="", timeout=75))
        test.expect(test.dut.at1.send_and_verify("AT^SEXIT=14", wait_for=".*SYSSTART.*", expect="", timeout=75))
        test.expect(test.dut.at1.send_and_verify("AT^SEXIT=15", wait_for=".*SYSSTART.*", expect="", timeout=75))
        test.expect(test.dut.at1.send_and_verify("AT^SEXIT=16", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SEXIT=20", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SEXIT=21", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SEXIT=1", wait_for=".*SYSSTART.*", expect="", timeout=75))
        test.expect(test.dut.at1.send_and_verify("AT^SEXIT=2", wait_for=".*SYSSTART.*", expect="", timeout=75))
        test.expect(test.dut.at1.send_and_verify("AT^SEXIT=3", wait_for=".*SYSSTART.*", expect="", timeout=75))
        test.CheckForSpecificExitText(7, "Fatal exception")

        test.expect(test.dut.at1.send_and_verify("AT^SEXIT=1", wait_for=".*SYSSTART.*", expect="", timeout=75))
        test.expect(test.dut.at1.send_and_verify("AT^SEXIT=2", wait_for=".*SYSSTART.*", expect="", timeout=75))
        test.expect(test.dut.at1.send_and_verify("AT^SEXIT=3", wait_for=".*SYSSTART.*", expect="", timeout=75))
        test.CheckForSpecificExitText(10, "Fatal exception")

        test.log.info("\n --- EXIT HISTORY filled up with 15 entries, now do two more --- ")
        test.expect(test.dut.at1.send_and_verify("AT^SEXIT=13", wait_for=".*SYSSTART.*", expect="", timeout=75))
        test.CheckForSpecificExitText(11, "Fatal exception")

        test.expect(test.dut.at1.send_and_verify("AT^SEXIT=14", wait_for=".*SYSSTART.*", expect="", timeout=75))
        test.CheckForSpecificExitText(12, "Fatal exception")

        sum, ret, text = dstl_read_latest_exit(test.dut, 11)
        if sum < 15:
            test.log.error(" found less than maximum possible entries, at least 15 or 16 are expected for a full list!")
            test.expect(False, critical=True)


        test.log.com('*** 4. clear EH-list and check  ***')
        dstl_clear_exit_history(test.dut)
        sum, ret, text = dstl_read_latest_exit(test.dut)
        if sum > 0:
            test.log.error("##> EXIT history should be empty.")
            test.expect(False, critical=True)
        else:
            test.expect(True)
            test.log.info("##> EXIT history is empty, fine.")

        pass


    def cleanup(test):
        test.log.com('*** 9. set back important settings  ***')
        # set back to default setting for automatic tests:
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=MEopMode/CoreDump,1,1,PowerOff", ".*OK.*"))
        test.log.com('***** Testcase: ' + test.test_file + ' - END *****')
        pass

if "__main__" == __name__:
    unicorn.main()

