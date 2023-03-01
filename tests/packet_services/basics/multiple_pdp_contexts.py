#responsible: maik.roge@thalesgroup.com
#location: Berlin
#TC0094096.001

import re
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network, dstl_enter_pin


class Test(BaseTest):
    """TC0094096.001    TpMultiplePDPContexts

    2 PDP context for each serial port (or virtual serial port) can be active by Qos setting

    1. Active GPRS attach
    2. Set default value for Qos Profile minimum acceptable
    3. Set any value for Qos profile requested
    4. Define primary PDP context through ASC0
    5. Define secondary PDP context with different apn through ASC1
    6. Activate the two PDP contexts, check actual address and activation state
    """

    def setup(test):
        dstl_detect(test.dut)
        test.expect(dstl_get_imei(test.dut))
        test.expect(dstl_get_bootloader(test.dut))

    def run(test):
        test.log.step("1. Check registration status.")
        test.log.info("Enter Pin and check registration ")
        test.expect(dstl_register_to_network(test.dut))
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify("AT+COPS?", r".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", r".*OK.*"))
        test.log.info("Check software version")
        test.expect(test.dut.at1.send_and_verify("at^cicret=\"swn\"", r".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at+cgatt?", r".*\+CGATT: 1.*"))
        test.log.info("Set default value for Qos Profile minimum acceptable")
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify("at+cgeqos=2,1,1,1,1,1", r".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at+cgeqos=3,1,64,64,128,128",r".*OK.*"))
        test.log.info("Define primary PDP context through ASC0")
        test.dut.at1.send_and_verify('AT+CGDCONT=2,\"IP\",\"{}\"'.format(test.dut.sim.apn_v4), ".*OK.*")
        test.log.info("Define secondary PDP context with different apn through ASC1")
        test.expect(test.dut.at1.send_and_verify("at+cgdscont=3,1,0,0", r".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CGTFT=3,1,0,\"8.8.8.8.255.255.255.255\"", r".*OK.*"))
        test.log.info("Active the two PDP contexts, check actual address and activation state")
        test.expect(test.dut.at1.send_and_verify("at+cgact=1,2", r".*OK."))
        test.expect(test.dut.at1.send_and_verify("at+cgact=1,3", r".*ERROR."))
        test.expect(test.dut.at1.send_and_verify("at+cgpaddr", r".*OK."))
        test.expect(dstl_restart(test.dut))
        test.expect(dstl_enter_pin(test.dut))

    def cleanup(test):
        
        test.dut.at1.send_and_verify("AT&F", ".*OK.*")
        test.dut.at1.send_and_verify("AT&W", ".*OK.*")


if "__main__" == __name__:
    unicorn.main()
