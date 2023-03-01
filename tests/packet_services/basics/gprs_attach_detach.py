#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0102254.001

import unicorn
from core.basetest import BaseTest
import re
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network


class Test(BaseTest):
    """
    TC0102254.001 - TpGprsAttachDetach
    Test the stability of module during the status changing between attach and detach.
    Subscribers: dut, MCTest
    """
    def setup(test):
        # Specify how many times will module attach/detach GPRS
        test.loop = 20

        # Setup for test run
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_restart())
        test.sleep(2)

    def run(test):
        test.log.step("1. Register module to network")
        test.expect(test.dut.dstl_register_to_network())

        test.log.step("2. Get module attached status")
        test.expect(test.dut.at1.send_and_verify("AT+CGATT?", "OK"))
        response = test.dut.at1.last_response
        result = re.findall("\+CGATT:\s*(1|0)\s*", response)
        is_attached = False
        if not result:
            test.expect(False, msg="Cannot get GPRS attached status, stop run")
            exit()
        elif result[0] == '1':
            is_attached = True
        else:
            is_attached = False

        test.log.step("3. Start duration test, loop times: ".format(test.loop))
        for i in range(test.loop):
            test.log.info("********** Loop {} of {} **********".format(i+1, test.loop))
            action = "attach" if not is_attached else "detach"
            test.log.info("Action: {}".format(action))
            result = test.attach_or_detach(is_attached)
            is_attached = not is_attached
            action = "detach" if result and action == "attach" else "attach"
            test.log.info("Action: {}".format(action))
            result &= test.attach_or_detach(is_attached)
            if result:
                test.log.info("Loop {} is executed successfully".format(i))
            else:
                test.expect(False, msg="Loop {} is executed with failures".format(i))

    def cleanup(test):
        pass

    def attach_or_detach(test, is_attached=False):
        """
        Method for changing GPRS attached status
        If module is attached, detach it from GPRS network
        Or if module is detached, attach it to GPRS network
        """
        if is_attached:
            test.attempt(test.dut.at1.send_and_verify, "AT+CGATT=0", expect="OK", timeout=10, retry=3)
            result = test.dut.at1.send_and_verify("AT+CGATT?", "\+CGATT:\s*0\s*")
        else:
            test.attempt(test.dut.at1.send_and_verify, "AT+CGATT=1", expect="OK", timeout=10, retry=3)
            result = test.dut.at1.send_and_verify("AT+CGATT?", "\+CGATT:\s*1\s*")
        return result




if (__name__ == "__main__"):
    unicorn.main()
