#responsible: yanen.wang@thalesgroup.com
#location: Beijing
#TC0102478.001
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
        TC0102473.001	WWANAdapterIPv4Windows7
        TC0102478.001   WWANAdapterIPv4Windows10
    """
    def setup(test):
        dstl_detect(test.dut)
        apn_v4 = test.dut.sim.apn_v4
        define_pdp_context_ipv4 = f"AT+CGDCONT=1,\"IP\",\"{apn_v4}\""
        test.expect(test.dut.at1.send_and_verify(define_pdp_context_ipv4, "OK"))
        if test.dut.project == "VIPER":
            test.log.info(" *Service Set for USB *")
            test.dut.at1.send_and_verify('AT^SSRVSET="actSrvSet",11', "OK")
            test.dut.at1.send_and_verify('AT^SCFG="MEopMode/Prov/AutoSelect","off"', "OK")
        else:
            test.log.info(" * ***** * ")

        dstl_restart(test.dut)

    def run(test):
        test.log.info("Runnig TC for IPv4")
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
        test.http_server = HttpServer("IPv4")
        server_ipv4_address = test.http_server.dstl_get_server_ip_address()
        test.sleep(5)
        test.dut.at1.send_and_verify(deactivate_wwan)
        test.expect(test.dut.at1.send_and_verify(activate_wwan))
        test.sleep(5)
        test.dut.at1.send_and_verify(show_pdp_address)
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
        test.get_ping_result(server_ipv4_address)
        test.dut.at1.send_and_verify(deactivate_wwan)
        test.sleep(5)

    def is_ipv_4(test, address):
        try:
            ip_object = ipaddress.ip_address(address)
            return isinstance(ip_object, ipaddress.IPv4Address)
        except Exception as e:
            test.log.error("No valid IPv4 address!")
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
        test.dut.at1.send_and_verify('AT&F', 'OK')
        dstl_restart(test.dut)
        pass

if (__name__ == "__main__"):
    unicorn.main()
