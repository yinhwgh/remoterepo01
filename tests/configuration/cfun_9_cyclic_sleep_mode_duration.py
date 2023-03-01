#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0011943.001

import unicorn
import re
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.sms import sms_functions
from dstl.sms import sms_configurations


class TpCfun9(BaseTest):
    """
    TC0011943.001 -  TpCfun9
    - functional test of sleepmode 9
    - wake up the module with different scenarios
    - it's a test of 500 loops

    Subscribers: dut, remote module, MCTest
    Default loop: 500
    Unicorn IPIS blocks: IPIS100315246
    """

    def setup(test):
        test.loop = 50
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.r1.dstl_register_to_network())
        # Configure for dut
        test.expect(test.dut.at1.send_and_verify("AT+CMGF=1","OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CSCA=\"{}\"".format(test.dut.sim.sca),"OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CPMS=\"SM\",\"SM\",\"SM\"", "OK"))
        test.expect(test.dut.dstl_enable_sms_urc())
        test.expect(test.dut.dstl_delete_all_sms_messages())
        test.memory_capacity = test.dut.dstl_get_sms_memory_capacity(3)
        # Configure for remote module
        test.expect(test.r1.at1.send_and_verify("AT+CMGF=1", "OK"))
        test.expect(test.r1.at1.send_and_verify("AT+CSCA=\"{}\"".format(test.dut.sim.sca),"OK"))
        test.expect(test.r1.at1.send_and_verify("AT+CPMS=\"SM\",\"SM\",\"SM\"","OK"))

    def run(test):
        # Set hardware flow control
        test.expect(test.dut.at1.send_and_verify("AT\Q3", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT&V", "\Q3"))
        # Set module to CFUN: 9
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"PowerSaver/Mode9/Timeout\",\"25\"", "OK"))
        test.expect(test.dut.devboard.send_and_verify("MC:ASC0?", "CTS0: 0"))
        test.expect(test.dut.at1.send_and_verify("AT+CFUN=9", "OK"))
        test.sleep(5)
        test.expect(test.dut.devboard.send_and_verify("MC:ASC0?", "CTS0: 1"))

        for i in range(1, test.loop + 1):
            test.log.info("Loop {} of {}: Wake up module temporarily by SMS".format(i, test.loop))
            test.expect(test.r1.at1.send_and_verify("AT+CMGS=\"{}\"".format(test.dut.sim.int_voice_nr), ".*>.*", wait_for=".*>.*"))
            test.expect(test.r1.at1.send_and_verify("Cfun9 Test, wakeup module by SMS, loop {}".format(i), end="\u001A"))
            test.expect(test.dut.at1.wait_for("\+CMTI:"))
            test.sleep(0.5)
            test.log.info("Loop {} of {}: module is still in cyclic sleep mode after SMS".format(i, test.loop))
            test.attempt_send_and_verify("AT+CFUN?", "\+CFUN: 9", retry=5)
            test.expect(test.dut.devboard.send_and_verify("MC:ASC0?", "CTS0: 0"))
            test.log.info(test.dut.devboard.last_response)
            test.sleep(5)
            test.expect(test.dut.devboard.send_and_verify("MC:ASC0?", "CTS0: 1"))
            test.attempt_send_and_verify("AT+CFUN?", "\+CFUN: 9", retry=5)

            test.log.info("Loop {} of {}: Wake up module temporarily by voice call".format(i, test.loop))
            test.r1.at1.send("ATD{};".format(test.dut.sim.int_voice_nr))
            test.expect(test.dut.at1.wait_for("RING"))
            test.dut.at1.send("ATA")
            test.expect(test.r1.at1.wait_for("OK"))
            test.r1.at1.send("ATH")
            test.expect(test.dut.at1.wait_for("NO CARRIER"))
            test.log.info("Loop {} of {}: module is still in cyclic sleep mode after voice call".format(i, test.loop))
            test.attempt_send_and_verify("AT+CFUN?", "\+CFUN: 9", retry=5)
            test.dut.devboard.send_and_verify("MC:ASC0?", "CTS0: 0")
            test.sleep(5)
            test.dut.devboard.send_and_verify("MC:ASC0?", "CTS0: 1")
            test.attempt_send_and_verify("AT+CFUN?", "\+CFUN: 9", retry=5)

            if i % int(test.memory_capacity) == 0:
                test.log.info("SMS Memory is full, delete all messages")
                test.expect(test.dut.dstl_delete_all_sms_messages())
                test.log.info("Finish deleting all messages")


    def cleanup(test):
        # Set module back to normal mode
        test.attempt_send_and_verify("AT+CFUN=1", "OK", retry=5)
        test.expect(test.dut.at1.send_and_verify("AT+CFUN?", "+CFUN: 1"))
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"PowerSaver/Mode9/Timeout\",\"20\"", "OK"))

    # Workaround for Dingo IPIS100282886
    def attempt_send_and_verify(test, command, *args, retry=0, **kwargs):
        for i in range(retry+1):
            test.dut.at1.send(command, wait_after_send=1)
        test.dut.at1.read()
        return test.dut.at1.send_and_verify(command, *args, **kwargs)
        # return True


if __name__ == "__main__":
    unicorn.main()
