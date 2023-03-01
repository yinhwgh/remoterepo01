#responsible: fang.liu@thalesgroup.com
#location: Berlin
#TC0104833.001

#Precondition:
#1. USB modem driver and Rmnet device driver must be installed perfectly;
#2. No any other error or warning msg in device manager for Viper interfaces.

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
import re

class Test(BaseTest):

    def setup(test):

        test.log.info("Precondition:\n"
                      "**********************************************************************************************\n"
                      "1. USB modem driver and Rmnet device driver must be installed perfectly;\n"
                      "2. No any other error or warning msg in device manager for Viper interfaces.\n"
                      "**********************************************************************************************\n")
        test.dut.dstl_detect()
        test.dut.dstl_enter_pin()

    def run(test):


        test.expect(test.dut.dstl_register_to_network())

        test.log.step("1. Enable the Rmnet function on DUT.")
        test.dut.at1.send_and_verify("at^ssrvset=actsrvset,11", ".*OK.*")
        test.expect(test.dut.at1.send_and_verify("at^ssrvset=actsrvset", ".*SSRVSET: 11.*"))

        test.dut.at1.send_and_verify("at^swwan=1,1", ".*OK.*")
        test.sleep(10)

        test.log.step("2. Try to Ping google.com via Ipv4inIpv6.")
        test.dut.at1.send_and_verify("at+cgpaddr", ".*OK.*")
        res = re.search(r'"(\d{1,3}).(\d{1,3}).(\d{1,3}).(\d{1,3})"', test.dut.at1.last_response)
        if res:
            test.expect(True)
        else:
            test.dut.error("DUT can't attach to network and obtain IP address.")

        ret = test.os.execute_and_verify("ping 0:0:0:0:0:FFFF:8.8.8.8", ".Reply from 8.8.8.8*")
        if ret:
            test.log.info(test.os.last_response)
        else:
            test.log.error("The ip 0:0:0:0:0:FFFF:8.8.8.8 is not accessible.")

    def cleanup(test):

        test.log.step("3. Deactive the PDP context in the end.")
        test.dut.at1.send_and_verify("at^swwan=0,1", ".*OK.*")


if "__main__" == __name__:
    unicorn.main()