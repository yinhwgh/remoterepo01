#responsible: fang.liu@thalesgroup.com
#location: Berlin
#TC0104835.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.packet_domain.start_public_IPv4_data_connection import *
from dstl.packet_domain.start_public_ipv4_data_connection_over_mbim import *
from dstl.auxiliary import init

class Test(BaseTest):

    def setup(test):

        test.dut.dstl_detect()

        """
        Module attached to network, connection on PC established on IPv6 PDP context.
        """
        test.log.step("1. Set PDP context to IPV6 first.")

        apn_ipv6 = test.dut.sim.gprs_apn_ipv6

        if not apn_ipv6:
            apn_ipv6 = "ber7.ericsson"

        test.dut.at1.send_and_verify("at+cgdcont=1,\"IPV6\",\"{}\"".format(apn_ipv6), ".*OK.*")
        test.expect(test.dut.dstl_register_to_network())

        test.log.step("2. Try to attach to network, and activate IPV6 PDP context.")
        test.dut.at1.send_and_verify("at+cgatt=1", ".*OK.*")
        test.dut.at1.send_and_verify("at+cgact=0,1", ".*OK.")

    def run(test):
        """
        Precondition: establish PPP connection First, if it's not possible try WWAN connection.
        """
        test.log.step("3. Data connection PPP/MBIM/WWAN must be established.")
        """
        res = test.dut.dstl_start_public_ipv4_data_connection_over_dialup(test, dialup_connection_name="Dial-up Connection", number="*99#")
        mbim = test.dut.start_connection(apn='ber7.ericsson')

        if mbim:
            test.log.info("MBIM connection is established.")
        else:
            test.log.info("It's failed to establish MBIM connection.")
        """
        #if "NOT ESTABLISH" in res[0] and not mbim:
        test.log.info("Try to establish WWAN connection.")
        test.dut.at1.send_and_verify("at^swwan=0,1", ".*OK.*")
        test.dut.dstl_start_public_ipv4_data_connection_over_wwan(test, wwan_adapter_1=True, wwan_adapter_2=False)
        #else:
            #test.expect(False, critical=True, msg="None of the data connection can be established, the test in not possible to execute!")
        """
         Execute the following commands in Windows command line:
         1. ping -S <IP address of module> 2a00:1450:4001:820::200e -i 1  "Time out error will occur, TTL expired in transit"
         2. ping -S <IP address of module> x:x:x:x:x:x:x:x      "x:x:x:x:x:x:x:x is not an active address, this should invoke Destination Unreachable error - Destination host unreachable or Ping timeout error, depending on the provided address and network configuration"
         3. ping -S <IP address of module> 2a00:1450:4001:821::200e  "This should be successful, no error invoked."
        """
        test.log.step("4. Ping the remote address in three different ways.")
        test.dut.at1.send_and_verify("at+cgpaddr=1", ".*OK.*")
        res = re.search(r'1,((([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])))', test.dut.at1.last_response)
        ipv6_dut = res.group(1)

        test.log.info("Ping a IPv6 address which not reachable, destination")
        test.os.execute_and_verify("ping -S {}:2a00:1450:4001:820::200e -i 1".format(ipv6_dut), ".*failed.*" | ".*timed out.*")

        test.log.info("Destination host unreachable or Ping timeout error, depending on the provided address and network configuration")
        test.os.execute_and_verify("ping -S {}:x:x:x:x:x:x:x:x".format(ipv6_dut), ".*unreachable.*" | ".*timed out.*")

        test.log.info("Ping Google ipv6 address, it should be successful.")
        test.os.execute_and_verify("ping -S {}:2a00:1450:4001:821::200e", ".*0% loss.*")


    def cleanup(test):
        """
        < Test postconditions >
        """
        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, dialup_connection_name="Dial-up Connection")


if "__main__" == __name__:
    unicorn.main()
