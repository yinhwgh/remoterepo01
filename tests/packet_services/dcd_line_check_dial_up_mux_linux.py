#responsible: yanen.wang@thalesgroup.com
#location: Beijing
#TC0107276.001

import unicorn

from core.basetest import BaseTest
from os.path import dirname, realpath
from dstl.packet_domain.start_public_IPv4_data_connection import *
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_network

class Test(BaseTest):
    """
            TC0107276.001 	DCDLineCheckDialUpMuxLinux
        """
    def __init__(self):
        super().__init__()
        self.dialup_conn_name = None

    def setup(test):
        test.dut.detect()

    def run(test):
        test.log.step("1. Register on Network")
        test.expect(dstl_register_to_network(test.dut))
        test.log.step("2. Establish dial-up connection ")
        test.expect(test.dut.dstl_start_public_ipv4_data_connection_over_dialup_multiple(test, "at2",
                                                                                         test.dialup_conn_name),critical=True)
        test.sleep(10)
        test.log.info("Enable DCD line indication for Internet service profiles.")
        test.dut.at1.send_and_verify('at&c2')
        test.log.step("3. Check DCD0 line status on DSB (it should be ON)")
        test.expect(test.dut.at1.connection.getCD())
        test.log.step("4. Disconnect dial-up connection")
        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test)
        test.sleep(10)
        test.log.step("5. Check DCD0 line status (it should be OFF)")
        test.expect(not test.dut.at1.connection.getCD())


    def cleanup(test):
        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test)
        test.dut.at1.send_and_verify('AT&F', 'OK')

def check_dcd(test, atc_parameter):
    if atc_parameter == 0:
        test.expect(test.dut.at1.connection.getCD())
    else:
        test.expect(not test.dut.at1.connection.getCD())

if (__name__ == "__main__"):
    unicorn.main()
