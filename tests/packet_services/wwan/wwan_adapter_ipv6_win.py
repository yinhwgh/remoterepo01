#responsible: yanen.wang@thalesgroup.com
#location: Beijing
#TC0102474.001
import re
import ipaddress
import subprocess
import sys
import unicorn
import urllib.request
from dstl.auxiliary import init
from dstl.security.lock_unlock_sim import dstl_unlock_sim
from dstl.network_service.register_to_network import *
from core.basetest import BaseTest
from dstl.packet_domain.start_public_IPv4_data_connection import *
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.ip_server.http_server import HttpServer

class Test(BaseTest):
    """ Debuged via VIPER
        TC0102474.001	WWANAdapterIPv6Windows7
    """
    def setup(test):
        dstl_detect(test.dut)
        apn_v6 = test.dut.sim.apn_v6
        define_pdp_context_ipv6 = f"AT+CGDCONT=1,\"IPV6\",\"{apn_v6}\""
        test.expect(test.dut.at1.send_and_verify(define_pdp_context_ipv6, "OK"))
        if test.dut.project == "VIPER":
            test.log.info(" *Service Set for USB *")
            test.dut.at1.send_and_verify('AT^SSRVSET="actSrvSet",11', "OK")
            test.dut.at1.send_and_verify('AT^SCFG="MEopMode/Prov/AutoSelect","off"', "OK")
        else:
            test.log.info(" * ***** * ")
        dstl_restart(test.dut)
    def run(test):
        test.log.info("Scenario--Runnig TC for IPv6")
        # Run test in 2G
        dstl_register_to_gsm(test.dut)
        test.test_wwan()

        # Run test in 3G
        dstl_register_to_umts(test.dut)
        test.test_wwan()

        # Run test in 4G
        dstl_register_to_lte(test.dut)
        test.test_wwan()

    def test_wwan(test):
        # AT commands
        activate_wwan = "AT^SWWAN=1,1"
        deactivate_wwan = "AT^SWWAN=0,1"
        show_pdp_address = "AT+CGPADDR"
        test.http_server = HttpServer("IPv6")
        server_ipv6_address = test.http_server.dstl_get_server_ip_address()
        test.sleep(5)
        test.dut.at1.send_and_verify("AT+CGPIAF=1,0,0", "OK")  # Select Printing IP address format
        test.expect(test.dut.at1.send_and_verify(activate_wwan))
        test.sleep(5)
        test.dut.at1.send_and_verify(show_pdp_address)
        try:
            # Get IP address from last_response
            ip_candidates = test.dut.at1.last_response.split('\n')[1].split(',')[1]
            ip_v6_address_dut = ip_candidates.replace('\"', '', 2).replace('\r', '')
            test.log.info(f'IPv6 address: {ip_v6_address_dut}')
            test.expect(test.is_ipv_6(ip_v6_address_dut))
            test.expect(test.first_four_ipv6_segments_found_in_ipconfig(ip_v6_address_dut))
        except:
            test.log.error("No IPv6 address found in last_response")
            test.expect(False)
        test.get_ping_result(server_ipv6_address)
        test.dut.at1.send_and_verify(deactivate_wwan)

    def is_ipv_6(test, address):
        try:
            ip_object = ipaddress.ip_address(f'{address}')
            return isinstance(ip_object, ipaddress.IPv6Address)
        except Exception as e:
            test.log.info(e)
            return False

    def get_ipconfig_output(test):
        test.log.info("Calling ipconfig ...")
        process = subprocess.Popen('ipconfig', stdout=subprocess.PIPE)
        output = process.stdout.read().decode('ascii')
        test.log.info(output)
        return output

    def first_four_ipv6_segments_found_in_ipconfig(test, ip_address):
        ip_address = ip_address.split(":")
        ip_address = ':'.join(ip_address[0:4]).lower()
        match = re.search(f'.*{ip_address}:.*', test.get_ipconfig_output())
        if match:
            test.log.info("IPv6 address from WWAN was founf in Windows console")
            return True
        else:
            test.log.error("IPv6 address from WWAN was NOT found in Windows console")
            return False
    def get_ping_result(test, ip_address):
        try:
            result_ping = subprocess.check_output('ping %s' % ip_address)
            ping_str = str(result_ping, 'utf-8')  # convert from byte to string
            test.log.info(ping_str)
        except subprocess.CalledProcessError as error:
            test.log.error(error)
            return False
    def cleanup(test):
        test.dut.at1.send_and_verify('AT^SSRVSET="actSrvSet",1', "OK")
        test.dut.at1.send_and_verify('AT^SCFG="MEopMode/Prov/AutoSelect","on"', "OK")
        test.dut.at1.send_and_verify(f"AT+CGDCONT=1,\"IPV4V6\",\"\"")
        test.dut.at1.send_and_verify('AT&F', 'OK')
        dstl_restart(test.dut)
        pass

if (__name__ == "__main__"):
    unicorn.main()
