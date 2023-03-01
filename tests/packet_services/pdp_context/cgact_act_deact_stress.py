#responsible: yanen.wang@thalesgroup.com
#location: Beijing
#TC0107275.001

import re
import ipaddress
import subprocess
import sys
import unicorn
from dstl.auxiliary import init
from core.basetest import BaseTest
from dstl.network_service.register_to_network import *
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_enter_pin



class Test(BaseTest):
    """
            TC0107275.001 	CGACTActDeactStress
        """
    numOfLoops = 500
    def setup(test):
        test.dut.detect()

    def run(test):
        # Run test in 2G
        dstl_register_to_gsm(test.dut)
        test.test_cgact()

        # Run test in 4G
        dstl_register_to_lte(test.dut)
        test.test_cgact()

    def test_cgact(test):
        # AT commands
        apn_ipv4 = test.dut.sim.apn_v4
        apn_ipv6 = test.dut.sim.apn_v6
        define_pdp_context_ipv4 = f"AT+CGDCONT=2,\"IP\",\"{apn_ipv4}\""
        define_pdp_context_ipv6 = f"AT+CGDCONT=2,\"IPV6\",\"{apn_ipv6}\""
        show_pdp_address = "AT+CGPADDR"
        loop = 1
        while loop < test.numOfLoops + 1:
            test.log.info('*** Loop: {}'.format(loop))
            test.log.info("** Runnig TC for IPv4")
            test.expect(test.dut.at1.send_and_verify(define_pdp_context_ipv4, ".*OK.*"))
            test.dut.at1.send_and_verify('AT+CGACT=0,2', 'OK')
            test.log.info("Activate defined PDP context using AT+CGACT")
            test.expect(test.dut.at1.send_and_verify('AT+CGACT=1,2', 'OK'))
            test.expect(test.dut.at1.send_and_verify(show_pdp_address))
            test.log.info("Deactivate PDP context using AT+CGACT")
            test.expect(test.dut.at1.send_and_verify('AT+CGACT=0,2', 'OK'))
            test.log.info("** Runnig TC for IPv6")
            test.dut.at1.send_and_verify("AT+CGPIAF=1,0,0", "OK")
            test.expect(test.dut.at1.send_and_verify(define_pdp_context_ipv6, ".*OK.*"))
            test.log.info("Activate defined PDP context")
            test.expect(test.dut.at1.send_and_verify('AT+CGACT=1,2', 'OK'))
            test.expect(test.dut.at1.send_and_verify(show_pdp_address))
            test.log.info("Deactivate PDP context")
            test.expect(test.dut.at1.send_and_verify('AT+CGACT=0,2', 'OK'))
            loop = loop + 1
    def cleanup(test):
        test.dut.at1.send_and_verify('ATI', 'OK')
        test.dut.at1.send_and_verify('AT&F', 'OK')
        pass

if (__name__ == "__main__"):
    unicorn.main()
