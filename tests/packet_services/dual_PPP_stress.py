#responsible: yanen.wang@thalesgroup.com
#location: Beijing
#TC0092932.001

import unicorn
import urllib.request

from core.basetest import BaseTest
from dstl.packet_domain.start_public_IPv4_data_connection import *
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_network,dstl_enter_pin

def Schedule(a,b,c):
    per = 100.0 * a * b / c
    if per > 100:
       per =100
    dstl.log.info ('%.2f%%' % per)
def download_file(url,dir):
    urllib.request.urlretrieve(url,dir,Schedule)
    urllib.request.urlcleanup()

def get_ping_result(ip_address):
    try:
        result_ping = subprocess.check_output('ping %s' % ip_address)
        ping_str = str(result_ping, 'utf-8')  # convert from byte to string
        dstl.log.info(ping_str)
    except subprocess.CalledProcessError as error:
        dstl.log.error(error)

class Test(BaseTest):
    """
        TC0092932.001-TpdualPPPstress
        Intention:	To test if module can work well during dual PPP stress test.
        Step:
        1.Enter Pin code and register to network;
        2.Define two PDP with different APNs on both ASC0 modem and USB modem ports;
        3.Establish DUN on both ASC0 modem and USB modem ports via IPv4;
        4.Check activated PDP via at+cgdcont?;
        5.Define two PDP with different APNs on both ASC0 modem and USB modem ports;
        6.Disconnect DUN and establish DUN on both ASC0 mux modem and USB mux modem ports in parallel;
        7.Check activated PDP via at+cgdcont?;
        8.Try to establish a third PPP connection on USB modem port;
        9.Check activated PDP via at+cgdcont?;
        10.Repeat step 2 to 7 for 1000 loops;
        11.Do step 2 and 8 but via IPv6 by setting at+cgdcont=1,”IPv6”,"APN"

    """
    numOfLoops = 5
    def setup(test):
        dstl_detect(test.dut)
    def run(test):
        test.log.step("1.Enter Pin code and register to network")
        dstl_enter_pin(test.dut)
        test.expect(dstl_register_to_network(test.dut))
        test.sleep(5)
        test.log.info("* Repeat step 2 to 7 for 1000 loops *")
        loop = 1
        while loop < test.numOfLoops:
            test.log.step('Loop: {}'.format(loop))
            test.log.step("2.Define two PDP with different APNs on both ASC0 modem and USB modem ports")
            test.log.step("3.Establish DUN on both ASC0 modem and USB modem ports via IPv4")
            test.expect(test.dut.dstl_start_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name, "*99***1#"))
            # test.expect(test.dut.dstl_start_public_ipv4_data_connection_over_dialup(test,test.dialup_conn_name1,"*99***2#"))
            test.sleep(10)
            test.log.info("** Check if dial up successfully **")
            ping_result = get_ping_result(test.server_ip_address)
            test.log.info(ping_result)
            test.log.step("4.Check activated PDP via at+cgdcont?")
            test.expect(test.dut.at3.send_and_verify('at+cgdcont?','.*CGDCONT: 1 .*CGDCONT: 2'))
            test.log.step("5.Define two PDP with different APNs on both ASC0 modem and USB modem ports")

            test.log.step("6.Disconnect DUN and establish DUN on both ASC0 mux modem and USB mux modem ports in parallel")
            test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name)
            test.sleep(10)
            test.dut.at1.send_and_verify('AT','OK')
            test.expect(test.dut.dstl_start_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name, "*99***1#"))

            test.log.step("7.Check activated PDP via at+cgdcont?")
            test.expect(test.dut.at3.send_and_verify('at+cgdcont?', '.*CGDCONT: 1 .*CGDCONT: 2'))
            loop = loop + 1


        test.log.step("8.Try to establish a third PPP connection on USB modem port")

        test.log.step("9.Check activated PDP via at+cgdcont?")
        test.expect(test.dut.at3.send_and_verify('at+cgdcont?', '.*CGDCONT: 1 .*CGDCONT: 2'))
        test.log.step("4.Check activated PDP via at+cgdcont?")
        test.log.step("10.Do step 2 and 8 but via IPv6")

    def cleanup(test):
        test.dut.at1.send_and_verify(r'AT&F', '.*OK.*')
        pass

if (__name__ == "__main__"):
    unicorn.main()
