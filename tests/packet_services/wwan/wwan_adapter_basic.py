# author: johann.suhr@thalesgroup.com
# location: Berlin
# TC0103619.001
import re
import ipaddress
import subprocess
import sys
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.network_service.register_to_network import *
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_enter_pin

class Test(BaseTest):
    ''' TC0103619.001 - WwanAdapterBasic
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.at1.send_and_verify('AT^SCFG="MEopMode/Prov/AutoSelect","off"', "OK")
        test.dut.at1.send_and_verify('AT^SSRVSET="actSrvSet",11', "OK")
        dstl_restart(test.dut)

    def run(test):
        if "win32" not in sys.platform:
            test.log.error("Platform not supported")
            return

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
        apn_v4 = test.dut.sim.apn_v4
        apn_v6 = test.dut.sim.apn_v6
        define_pdp_context_ipv4 = f"AT+CGDCONT=1,\"IP\",\"{apn_v4}\""
        define_pdp_context_ipv6 = f"AT+CGDCONT=1,\"IPV6\",\"{apn_v6}\""
        activate_wwan = "AT^SWWAN=1,1"
        deactivate_wwan = "AT^SWWAN=0,1"
        show_pdp_address = "AT+CGPADDR"
        test.log.info("Runnig TC for IPv4")
        test.expect(test.dut.at1.send_and_verify(define_pdp_context_ipv4, ".*OK.*"))
        dstl_restart(test.dut)
        dstl_enter_pin(test.dut)
        test.sleep(60)
        test.expect(test.dut.at1.send_and_verify(activate_wwan))
        test.expect(test.dut.at1.send_and_verify(show_pdp_address))
        try:
            # Get IP address from last_response
            ip_candidates = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", test.dut.at1.last_response,
                                       re.MULTILINE)
            ip_v4_address_dut = ip_candidates[0]
            test.log.info(f"IPv4 address: {ip_v4_address_dut}")
            test.expect(test.is_ipv_4(ip_v4_address_dut))
            test.expect(test.ipv4_address_found_in_ipconfig(ip_v4_address_dut))
        except:
            test.log.error("No IPv4 address found in last_response")
            test.expect(False)
        # Step 4: Deactivate RmNet connection: at^swwan=0,2
        test.expect(test.dut.at1.send_and_verify(deactivate_wwan))
        # Step 6
        test.log.info("Runnig TC for IPv6")
        test.expect(test.dut.at1.send_and_verify(define_pdp_context_ipv6, ".*OK.*"))
        dstl_restart(test.dut)
        dstl_enter_pin(test.dut)
        test.sleep(60)
        # Repeat steps 2 - 5 for IPv6
        test.dut.at1.send_and_verify("AT+CGPIAF=1,0,0", "OK")
        # Step 2
        test.expect(test.dut.at1.send_and_verify(activate_wwan))
        # Step 3
        test.expect(test.dut.at1.send_and_verify(show_pdp_address))
        try:
            # Get IP address from last_response
            #ip_candidates = re.findall('(?<![:.\w])(?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}(?![:.\w])',
            #                           test.dut.at1.last_response, re.MULTILINE)
            ip_candidates = test.dut.at1.last_response.split('\n')[1].split(',')[1]
            ip_v6_address_dut = ip_candidates.replace('\"', '', 2).replace('\r','')
            test.log.info(f'IPv6 address: {ip_v6_address_dut}')
            test.expect(test.is_ipv_6(ip_v6_address_dut))
            test.expect(test.first_four_ipv6_segments_found_in_ipconfig(ip_v6_address_dut))

        except:
            test.log.error("No IPv6 address found in last_response")
            test.expect(False)
        # Step 4: Deactivate RmNet connection: at^swwan=0,1
        test.expect(test.dut.at1.send_and_verify(deactivate_wwan))
        # Cleaning up
        test.dut.at1.send_and_verify(f"AT+CGDCONT=1,\"IPV4V6\",\"\"")
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
            test.log.info(e)
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
        test.dut.at1.send_and_verify('AT^SSRVSET="actSrvSet",1', "OK")
        test.dut.at1.send_and_verify('AT^SCFG="MEopMode/Prov/AutoSelect","on"', "OK")
        test.dut.at1.send_and_verify(f"AT+CGDCONT=1,\"IPV4V6\",\"\"")
        test.dut.at1.send_and_verify("AT&F", "OK")
        dstl_restart(test.dut)
        pass

if "__main__" == __name__:
    unicorn.main()
