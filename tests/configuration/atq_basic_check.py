#responsible: yi.guo@thalesgroup.com
#location: Beijing
#TC0010291.001 - TpAtq
#TC0091674.001 - TpAtqBasic

import unicorn
import random

from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.security import lock_unlock_sim
from dstl.auxiliary.init import *
from dstl.auxiliary.restart_module import dstl_restart


class TpATQBasic(BaseTest):

    def setup(test):
        test.log.info("*******************************************************************")
        test.log.info("SetUp_1: Initiate moudle and restore to default configurations")
        test.log.info("*******************************************************************")
        test.dut.dstl_detect()
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*"))

        test.log.info("*******************************************************************")
        test.log.info("SetUp_2: Enable SIM PIN lock before testing  ")
        test.log.info("*******************************************************************")
        test.dut.dstl_lock_sim()
        test.dut.dstl_restart()

    def run(test):
        simPINLOCKstatus = ["before","after"]
        step = 1

        for simPINLOCK in simPINLOCKstatus:
            test.log.info("*******************************************************************")
            test.log.info("RunTest_{}: Check default value of ATQ {} input SIM PIN".format(step,simPINLOCK))
            test.log.info("*******************************************************************")
            test.expect(test.dut.at1.send_and_verify('AT&V', '.* Q0[\s\S]*OK.*'))
            step += 1

            test.log.info("*******************************************************************")
            test.log.info("RunTest_{}: Change ATQ value to ATQ1 {} input SIM PIN".format(step, simPINLOCK))
            test.log.info("*******************************************************************")
            test.expect(test.dut.at1.send_and_verify('ATQ1', '^((?!OK).)*$',wait_for='.*', wait_after_send=1))
            test.expect(test.dut.at1.send_and_verify('AT&V', '.* Q1.*\s+',wait_for='.* Q1.*\s+'))
            test.expect("OK" not in test.dut.at1.last_response, msg="OK should not display in response when ATQ1 is coufigured.")
            test.expect(test.dut.at1.send_and_verify('AT', '^((?!OK).)*$',wait_for='.*', wait_after_send=1))
            step += 1

            test.log.info("*******************************************************************")
            test.log.info("RunTest_{}: Restart Module and check value of ATQ {} input SIM PIN ".format(step,simPINLOCK))
            test.log.info("*******************************************************************")

            test.expect(test.dut.at1.send_and_verify('AT+CFUN=1,1', '',wait_for=''))
            if ("usb" in test.dut.at1.name and test.dut.project == 'VIPER'):
                # no SYSSTART for VIPER over USB
                test.sleep(30)
            else:
                test.expect(test.dut.at1.wait_for("\^SYSSTART"))
            test.sleep(2)
            test.expect(test.dut.at1.send_and_verify('AT&V', '.* Q0[\s\S]*OK\s+$'))
            test.expect(test.dut.at1.send_and_verify('AT', '.*OK\s+$'))
            step += 1

            test.log.info("*******************************************************************")
            test.log.info("RunTest_{}: Change ATQ value to ATQ1 {} input SIM PIN and AT&W".format(step,simPINLOCK))
            test.log.info("*******************************************************************")
            test.expect(test.dut.at1.send_and_verify('ATQ1', '^((?!OK).)*$', wait_for='.*', wait_after_send=1))
            test.expect(test.dut.at1.send_and_verify('AT&V', '.* Q1.*\s+',wait_for='.* Q1.*\s+'))
            test.expect(test.dut.at1.send_and_verify('AT&W', '^((?!OK).)*$',wait_for='.*', wait_after_send=1))
            step += 1

            test.log.info("*******************************************************************")
            test.log.info("RunTest_{}: Restart Module and check value of ATQ {} input SIM PIN ".format(step,simPINLOCK))
            test.log.info("*******************************************************************")
            test.expect(test.dut.at1.send_and_verify('AT+CFUN=1,1', '',wait_for=''))
            if ("usb" in test.dut.at1.name and test.dut.project == 'VIPE'):
                # no SYSSTART for VIPER over USB
                test.sleep(30)
            else:
                test.expect(test.dut.at1.wait_for("\^SYSSTART"))
            test.sleep(5)
            test.expect(test.dut.at1.send_and_verify('AT&V', '.* Q1.*\s+',wait_for='.* Q1.*\s+'))
            test.expect('OK' not in test.dut.at1.last_response)
            test.expect(test.dut.at1.send_and_verify('AT', '^((?!OK).)*$',wait_for='.*', wait_after_send=1))
            step += 1

            test.log.info("*******************************************************************")
            test.log.info("RunTest_{}: Restore Module with AT&F and check value of ATQ {} input SIM PIN ".format(step,simPINLOCK))
            test.log.info("*******************************************************************")
            # wait_after_send = 2: for some product(e.g. Viper), a little more time is needed for AT&F than other products(e.g. Serval)
            test.expect(test.dut.at1.send_and_verify('AT&F', '(^((?!OK).)*$|OK)',wait_for='.*', wait_after_send=2))
            test.expect(test.dut.at1.send_and_verify('AT&V', '.* Q0[\S\s]'))
            test.expect(test.dut.at1.send_and_verify('AT', '.*OK'))
            test.expect(test.dut.at1.send_and_verify('AT&W', '.*OK'))
            step += 1

            test.log.info("*******************************************************************")
            test.log.info("RunTest_{}: Set incorret value of ATQ {} input SIM PIN ".format(step, simPINLOCK))
            test.log.info("*******************************************************************")
            test.expect(test.dut.at1.send_and_verify('ATQ2', '.*ERROR.*'))
            test.expect(test.dut.at1.send_and_verify('ATQ3', '.*ERROR.*'))
            test.expect(test.dut.at1.send_and_verify('ATQB', '.*ERROR.*'))
            test.expect(test.dut.at1.send_and_verify('ATQ-1', '.*ERROR.*'))
            step += 1

            if simPINLOCK == "before":
                test.expect(test.dut.dstl_enter_pin())
                test.log.info("Wait a while after input PIN code")

    def cleanup(test):
        test.log.info("*******************************************************************")
        test.log.info("CleanUp_1: Restore to default configurations")
        test.log.info("*******************************************************************")
        test.dut.at1.send_and_verify("AT&F", ".*")
        test.dut.at1.send_and_verify("at&F")
        test.sleep(5)
        test.dut.at1.send_and_verify("atv1",".*OK.*")
        test.dut.at1.send_and_verify("ate1", ".*OK.*")
        test.dut.at1.send_and_verify("atq0", ".*OK.*")
        test.dut.at1.send_and_verify("AT&W", ".*")

if (__name__ == "__main__"):
    unicorn.main()