#responsible: yanen.wang@thalesgroup.com
#location: Beijing
#TC0107257.001

import unicorn
import time

from socket import *
from core.basetest import BaseTest
from dstl.packet_domain.start_public_IPv4_data_connection import *
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_network


class Test(BaseTest):
    """
        TC0107257.001 PPPDialUpLogoutTime
    """
    time_rec_disconnect_req = 0
    time_rev_urc = 0
    delta_t = 0
    def __init__(self):
        super().__init__()
        self.dialup_conn_name = None

    def setup(test):
        dstl_detect(test.dut)

    def run(test):
        test.log.step("1. Register on Network")
        test.expect(dstl_register_to_network(test.dut))
        test.log.step("2. Establish dial-up connection ")
        test.dut.dstl_start_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name)
        test.log.step("3. Stop dial up connection ***")
        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name)
        #test.dut.at1.send('AT')
        test.time_rec_disconnect_req = time.time()
        test.dut.at1.wait_for(".*NO CARRIER", timeout=4)
        test.time_rev_urc = time.time()
        test.delta_t = test.time_rev_urc - test.time_rec_disconnect_req
        if test.delta_t < 3:
            test.log.info("Measured time:{:.2f} in line with expectations.".format(test.delta_t))
        else:
            test.log.error("The time of disconnect dialup is Not meet the expectation")

    def cleanup(test):
        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name)
        test.dut.at1.send_and_verify('ATI', 'OK')
        test.dut.at1.send_and_verify('AT&F', 'OK')
        pass

if (__name__ == "__main__"):
    unicorn.main()
