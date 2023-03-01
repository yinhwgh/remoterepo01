#responsible: fang.liu@thalesgroup.com
#location: Berlin
#TC0091943.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.network_service import attach_to_network
from dstl.packet_domain.start_public_IPv4_data_connection import *
from dstl.auxiliary import init
import re


class Test(BaseTest):

    def setup(test):
        """Precondition :
        1. The test network or private network must support PAP or CHAP authentication;
        2. Specific APN must be set for the specific PDP context;
        3. If the network is test network in BLN, the APN should be 'ber-auth.ericsson'.
        """
        test.dut.dstl_detect()
        test.dut.dstl_enter_pin()
        #Deregister from network first.
        test.dut.at1.send_and_verify("at+cops=2", ".*OK.*")

    def run(test):

        test.log.info("***********************************************************************************************")
        test.log.step("1. Set the APN for PDP context 1 to \"ber-auth.ericsson\".")
        test.log.info("***********************************************************************************************")
        test.dut.at1.send_and_verify("at+cmee=2;+creg=2", ".*OK.*")
        test.dut.at1.send_and_verify("at+cgdcont=1,\"IPV4V6\",\"ber-auth.ericsson\"", ".*OK.*")

        test.log.info("***********************************************************************************************")
        test.log.step("2. Set the authentication type to CHAP, as well as the username and password.")
        test.log.info("***********************************************************************************************")
        test.dut.at1.send_and_verify("at^sgauth=1,2,\"gemalto\",\"gemalto\"", ".*OK.*")

        test.log.info("***********************************************************************************************")
        test.log.step("3. Register to network and check the URC afterward.")
        test.log.info("***********************************************************************************************")
        test.dut.at1.send_and_verify("at+cops=0")
        test.sleep(10)
        #Waiting for the URC '+CREG: 1' in the response.
        res = re.search(r'\+CREG: 1', test.dut.at1.last_response)
        if res:
            test.expect(True)
        else:
            test.log.error("Module can't register to network currently, pls try again.")


        test.log.info("***********************************************************************************************")
        test.log.step("4. Make sure module can attach to network.")
        test.log.info("***********************************************************************************************")
        test.dut.at1.send_and_verify("at+cgatt?", ".*+CGATT: 1.*")
        #test.dut.dstl_attach_to_network()

        test.dut.at1.send_and_verify("at^sgauth?", ".*^SGAUTH: 1,2.*")

        test.log.info("***********************************************************************************************")
        test.log.step("5. Enable the WWAN data connection on DUT.")
        test.log.info("***********************************************************************************************")
        test.dut.at1.send_and_verify("at^ssrvset=actsrvset,11", ".*OK.*")
        test.expect(test.dut.at1.send_and_verify("at^ssrvset=actsrvset", ".*SSRVSET: 11.*"))

        test.sleep(10)

        test.dut.dstl_start_public_ipv4_data_connection_over_wwan(test, wwan_adapter_1=True, wwan_adapter_2=False)

    def cleanup(test):

        test.dut.at1.send_and_verify("at^swwan=0,1", ".*OK.*")

        test.log.info("Remove the APN for the PDP context.")
        test.dut.at1.send_and_verify("at+cgdcont=1,\"IPV4V6\",\"\"", ".*OK.*")

        pass

if "__main__" == __name__:
    unicorn.main()

