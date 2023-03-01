#responsible: fang.liu@globallogic.com
#location: Berlin
#TC0103933.001

import unicorn
import subprocess
import re
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.packet_domain.start_public_IPv4_data_connection import *
from dstl.network_service.register_to_network import dstl_register_to_network



class DailUpWindows(BaseTest):

    def setup(test):

        test.dut.dstl_detect()
        test.dut.dstl_register_to_network()

    def run(test):
        """
        1.Establish dial-up connection
        2.Check connection properties - DNS address should be assigned
        3.Execute ping to domain (eg. ping google.com or ping www.dau.dau on CMW-500). Name should be resolved to IP address.
        4.Repeat steps 1-3 for dial-up connection with IPv6 address (if supported)
        """
        domain_addr = "www.google.com"

        test.log.step("1. Establish PPP dial_up connection via USB module port.")
        test.log.info("***********************************************************************************************")
        test.dut.dstl_start_public_ipv4_data_connection_over_dialup(test, dialup_connection_name="Dial-up Connection", number="*99***#")

        test.check_properties()

        test.ping_domain(domain_addr)


        test.log.step("4. Disconnect the dial_up connection.")
        test.log.info("***********************************************************************************************")
        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, dialup_connection_name="Dial-up Connection")


    def check_properties(test):

        test.log.step("2. Check connection properties - DNS address should be assigned")
        test.log.info("***********************************************************************************************")

        res = subprocess.check_output('ipconfig /all')

        # convert from byte to string
        res_str = str(res, 'utf-8')

        pattern_dns = r'DNS Servers . . . . . . . . . . . : [0-9]+\.[0-9]+\.[0-9]+\.[0-9]+'
        pattern_ppp = r'Dial-up Connection:'
        res_1 = re.search(pattern_dns, res_str)
        res_2 = re.search(pattern_ppp, res_str)

        test.log.info("The DNS servers assigned are as follows:")
        print(res_2)
        print(res_1)


    def ping_domain(test, address_url):

        test.log.step("3. Ping the domain, exp. ping google.com or ping www.dau.dau.")
        test.log.info("***********************************************************************************************")

        res = subprocess.check_output('ping %s' % address_url)
        res_str = str(res, 'utf-8')

        pattern_ip = r'Pinging(.*)(\[[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\]) with 32 bytes of data:'
        res_3 = re.search(pattern_ip, res_str)

        if res_3:
            print(res_3.group())
            test.expect(True)
        else:
            test.log.error("Domain name can't be resolved to IP address.")


    def cleanup(test):

        pass

if "__main__" == __name__:
    unicorn.main()
