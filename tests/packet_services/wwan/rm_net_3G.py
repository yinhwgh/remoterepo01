#responsible: yanen.wang@thalesgroup.com
#location: Beijing
#TC0092392.001

import ipaddress
import unicorn
import urllib.request

from os.path import dirname, realpath
from dstl.network_service.register_to_network import *
from core.basetest import BaseTest
from dstl.packet_domain.start_public_IPv4_data_connection import *
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.ip_server.http_server import HttpServer

def Schedule(a,b,c):
    per = 100.0 * a * b / c
    if per > 100:
       per = 100
    dstl.log.info ('%.2f%%' % per)
def download_file(url, dir):
    root = dirname(dirname(dirname(dirname(realpath(__file__)))))
    name = 'DLfile'
    dir = os.path.join(root, name)
    urllib.request.urlretrieve(url, dir, Schedule)
    urllib.request.urlcleanup()

class Test(BaseTest):
    """ Debuged via VIPER
        TC0092392.001	RmNet3G
    """
    def get_ping_result(test, ip_address):
        try:
            result_ping = subprocess.check_output('ping %s' % ip_address)
            ping_str = str(result_ping, 'utf-8')  # convert from byte to string
            test.log.info(ping_str)
        except subprocess.CalledProcessError as error:
            test.log.error(error)
            return False

    def setup(test):
        dstl_detect(test.dut)
        if test.dut.project == "VIPER":
           test.log.info(" *Service Set for USB *")
           test.dut.at1.send_and_verify('AT^SSRVSET="actSrvSet",11', "OK")
           dstl_restart(test.dut)
        else:
           test.log.info(" * ***** * ")

    def run(test):
        # AT commands
        apn_v4 = test.dut.sim.apn_v4
        apn_v6 = test.dut.sim.apn_v6
        define_pdp_context_ipv4 = f"AT+CGDCONT=1,\"IP\",\"{apn_v4}\""
        define_pdp_context_ipv6 = f"AT+CGDCONT=1,\"IPV6\",\"{apn_v6}\""
        activate_wwan = "AT^SWWAN=1,1"
        show_pdp_address = "AT+CGPADDR"
        test.http_server = HttpServer("IPv4")
        server_ipv4_address = test.http_server.dstl_get_server_ip_address()
        #IPV4
        test.log.info("Scenario 2  IPv4")
        test.expect(test.dut.at1.send_and_verify(define_pdp_context_ipv4, ".*OK.*"))
        dstl_restart(test.dut)
        dstl_register_to_umts(test.dut)
        test.expect(test.dut.at1.send_and_verify(activate_wwan, 'OK'))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify(show_pdp_address))
        try:
            # Get IP address from last_response
            ip_candidates = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", test.dut.at1.last_response, re.MULTILINE)
            ip_v4_address_dut = ip_candidates[0]
            test.log.info(f"IPv4 address: {ip_v4_address_dut}")
            test.expect(test.is_ipv_4(ip_v4_address_dut))
            test.expect(test.ipv4_address_found_in_ipconfig(ip_v4_address_dut))
        except:
            test.log.error("No IPv4 address found in last_response")
            test.expect(False)
        test.sleep(5)
        test.get_ping_result(server_ipv4_address)
        #download_file(test.http_server_url, dir)
        test.dut.at1.send_and_verify("AT^SWWAN=0,1", "OK")
        #IPV6
        test.sleep(10)
        test.log.info("Scenario 2  IPv6")
        test.http_server = HttpServer("IPv6")
        server_ipv6_address = test.http_server.dstl_get_server_ip_address()
        test.expect(test.dut.at1.send_and_verify(define_pdp_context_ipv6, ".*OK.*"))
        dstl_restart(test.dut)
        dstl_register_to_umts(test.dut)
        test.expect(test.dut.at1.send_and_verify(activate_wwan, 'OK'))
        test.sleep(5)
        test.dut.at1.send_and_verify("AT+CGPIAF=1,0,0", "OK")  # Select Printing IP address format
        test.expect(test.dut.at1.send_and_verify(show_pdp_address))
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

    def is_ipv_4(test, address):
        try:
            ip_object = ipaddress.ip_address(address)
            return isinstance(ip_object, ipaddress.IPv4Address)
        except Exception as e:
            test.log.error("No valid IPv4 address!")
            return False

    def is_ipv_6(test, address):
        try:
            ip_object = ipaddress.ip_address(f'{address}')
            return isinstance(ip_object, ipaddress.IPv6Address)
        except Exception as e:
            test.log.error("No valid IPv6 address")
            return False

    def get_ipconfig_output(test):
        test.log.info("Calling ipconfig ...")
        process = subprocess.Popen('ipconfig', stdout=subprocess.PIPE)
        output = process.stdout.read().decode('ascii')
        test.log.info(output)
        return output

    def ipv4_address_found_in_ipconfig(test, ip_address):
        assigned_ip4v_addresses = re.findall('\s+IPv4 Address.*: ([\d\.]+)', test.get_ipconfig_output())
        if ip_address in assigned_ip4v_addresses:
            test.log.info("IPv4 address from WWAN was found in Windows console")
            return True
        else:
            test.log.error("IPv4 address from WWAN was NOT found in Windows console")
            return False

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

    def cleanup(test):
        test.dut.at1.send_and_verify("AT^SWWAN=0,1", "OK")
        test.dut.at1.send_and_verify(f"AT+CGDCONT=1,\"IPV4V6\",\"\"")
        test.dut.at1.send_and_verify('AT^SSRVSET="actSrvSet",1', "OK")
        test.dut.at1.send_and_verify('AT&F', 'OK')
        pass

if (__name__ == "__main__"):
    unicorn.main()
