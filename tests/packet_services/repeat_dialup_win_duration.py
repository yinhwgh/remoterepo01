#responsible: yanen.wang@thalesgroup.com
#location: Beijing
#TC0107107.001

import unicorn

from core.basetest import BaseTest
from dstl.packet_domain.start_public_IPv4_data_connection import *
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_network

class DialUpConnectionWindows(BaseTest):
    """
        Intention:	Check ppp dial up connection reliability
        step:
        1. Configurate pdp context like this: at+cgdcont=1,"ip","internet"
        2. Register to network
        3. Set up ppp dial up connection .
        4. Ping baidu ip address or another address at least 4 package.
        5. Disconnect diap up connection
        6. Repeat step 1-5 500times.
        7. Step 1-6 need to executed on win 7,8 and 10 OS.
    """
    numOfLoops = 500
    def __init__(self):
        super().__init__()
        self.dialup_conn_name = None

    def get_ping_result(test,ip_address):
        try:
            result_ping = subprocess.check_output('ping %s' % ip_address)
            ping_str = str(result_ping, 'utf-8')  # convert from byte to string
            test.log.info(ping_str)
        except subprocess.CalledProcessError as error:
            test.log.error(error)

    def setup(test):
        dstl_detect(test.dut)

    def run(test):
        test.log.step("1.Configurate pdp context")
        test.dut.at1.send_and_verify('at+cgdcont=1,"IPV4V6","internet"', "OK")
        test.log.step("2.register on Network")
        test.expect(dstl_register_to_network(test.dut))
        test.sleep(5)
        test.log.info('Repeat {} dial up - Begin'.format(test.numOfLoops))
        loop = 1
        while loop < test.numOfLoops + 1:
            test.log.info("******************************************")
            test.log.info('Loop: {} of dial up- Begin'.format(loop))
            test.log.step("3. Set up ppp dial up connection ")
            test.expect(test.dut.dstl_start_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name), critical=True)
            test.log.step("4. check if dial up successfully via ping server ip address")
            test.get_ping_result(test.ftp_server_ipv4)
            test.log.step("5. Disconnect diap up connection ***")
            test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name)
            test.sleep(20)
            test.dut.at1.send_and_verify('AT', 'OK')
            loop = loop + 1
        test.log.info('Repeat {} dial up - End'.format(test.numOfLoops))
        test.dut.at1.send_and_verify('AT', 'OK')
        test.dut.at1.send_and_verify(r'AT&F', 'OK')

    def cleanup(test):
        pass

if (__name__ == "__main__"):
    unicorn.main()
