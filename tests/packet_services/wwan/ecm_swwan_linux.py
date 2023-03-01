#responsible: yanen.wang@thalesgroup.com
#location: Beijing
#TC0106139.001

import unicorn
import ipaddress
import subprocess
import sys

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.restart_module import dstl_restart

class Test(BaseTest):
    """
      TC0106139.001 Ecm_Swwan_Linux
    """

    def setup(test):
        dstl_detect(test.dut)
        test.dut.at1.send_and_verify('AT^SSRVSET="actSrvSet",1', "OK")
        dstl_restart(test.dut)

    def run(test):
        apn = test.dut.sim.apn_v4
        define_pdp_context = f"AT+CGDCONT=1,\"IPV4V6\",\"{apn}\""
        activate_wwan = "AT^SWWAN=1,1"
        deactivate_wwan = "AT^SWWAN=0,1"

        test.expect(test.dut.at1.send_and_verify(define_pdp_context, "OK"))
        test.log.step("Register on Network")
        dstl_register_to_network(test.dut)
        test.log.step("ECM WWAN in LINUX")
        test.expect(test.dut.at1.send_and_verify(activate_wwan, "OK"))
        test.sleep(10)
        test.get_ping_result(test.ftp_server_ipv4)
        test.expect(test.dut.at1.send_and_verify(deactivate_wwan, "OK"))

    def get_ipconfig_output(test):
        test.log.info("Calling ifconfig ...")
        process = subprocess.Popen('ifconfig -a', stdout=subprocess.PIPE)
        output = process.stdout.read().decode('ascii')
        test.log.info(output)
        return output
    def get_ping_result(test,ip_address):
        try:
            result_ping = subprocess.check_output('ping %s' % ip_address)
            ping_str = str(result_ping, 'utf-8')  # convert from byte to string
            test.log.info(ping_str)
        except subprocess.CalledProcessError as error:
            test.log.error(error)

    def cleanup(test):
        test.dut.at1.send_and_verify('AT&F', 'OK')
        pass

if (__name__ == "__main__"):
    unicorn.main()
