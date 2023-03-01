#responsible: dariusz.drozdek@globallogic.com
#location: Wroclaw
#TC0104910.001

import re
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.packet_domain.start_public_IPv4_data_connection import dstl_start_public_ipv4_data_connection_over_dialup, \
    dstl_stop_public_ipv4_data_connection_over_dialup, get_ip_address_windows


class Test(BaseTest):
    """TC0104910.001    DialupWithDifferentMtuSizeAndPing

    Test intention is to check functionality of different MTU size during Dial-up connection with ping execution.

    1. Set AT^SCFG="GPRS/MTU/Mode","1" command on module
    2. Set AT^SCFG="GPRS/MTU/Size","1430"
    3. Check AT^SCFG= "GPRS/MTU/Size" stored value
    4. Enter SIM PIN
    5. Establish Dial-up connection
    6. Check command ipconfig /all in command line, find IP address and name of Dial-up connection (PPP)
    7. Check "netsh interface ipv4 show subinterface" and match MTU size from step 2
    8. Ping host with command "ping -l MTU_size -S PPP_IP 8.8.8.8 -n 30" (or use other available host)
    9. Restart module
    10. Repeat step 2-8 using <mtusize>=1280
    NOTE: For standard MTU of 1500 bytes, the maximum data size is 1472 bytes (MTU minus 20 bytes IP header and
    8 bytes for the ICMP header).
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CGDCONT=1,\"IP\",\"{}\"".format(test.dut.sim.apn_v4), ".*OK.*"))

    def run(test):
        dialup_name = "DUN_PEGASUS"
        host_ip = "180.76.76.76"  # This is Baidu IP address or use Google IP address "8.8.8.8"

        test.log.step("1. Set AT^SCFG=\"GPRS/MTU/Mode\",\"1\" command on module")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"GPRS/MTU/Mode\",\"1\"", ".*OK.*"))
        test.sleep(2)
        test.expect(dstl_restart(test.dut))
        test.sleep(2)

        for mtu in ["1430", "1280"]:
            test.log.step("2. Set AT^SCFG=\"GPRS/MTU/Size\",\"{}\"".format(mtu))
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"GPRS/MTU/Size\",\"{}\"".format(mtu), ".*OK.*"))

            test.log.step("3. Check AT^SCFG= \"GPRS/MTU/Size\" stored value")
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"GPRS/MTU/Size\"", ".*\"GPRS/MTU/Size\",{}\n.*OK.*"
                                                     .format(mtu)))

            test.log.step("4. Enter SIM PIN")
            test.expect(dstl_enter_pin(test.dut))
            test.sleep(5)

            test.log.step("5. Establish Dial-up connection")
            test.expect(dstl_start_public_ipv4_data_connection_over_dialup(test.dut, test, dialup_name), critical=True)

            test.log.step("6. Check command ipconfig /all in command line, find IP address and name of Dial-up "
                          "connection (PPP)")
            ip_address = get_ip_address_windows()
            test.log.info("IP address for PPP interface : " + ip_address)
            test.expect(ip_address)

            test.log.step("7. Check \"netsh interface ipv4 show subinterface\" and match MTU size from step 2")
            netsh = test.os.execute("netsh interface ipv4 show subinterface")
            test.expect(netsh)
            x = re.search(r"(\d*)\s*\d*\s*\d*\s*\d*\s*({})".format(dialup_name), netsh)
            if x:
                if mtu == x.group(1):
                    test.log.info("MTU size is correct")
                    test.expect(True)
                else:
                    test.log.info("MTU size is incorrect, see IPIS100314535")
                    test.expect(False)
            else:
                test.log.error("MTU not found")
                test.expect(False)

            test.log.step("8. Ping host with command \"ping -l MTU_size -S PPP_IP {} -n 30\" "
                          "(or use other available host)".format(host_ip))
            mtu_data_size = str(int(mtu) - 28)
            ping = test.os.execute("ping -l {} -S {} {} -n 30".format(mtu_data_size, ip_address, host_ip))
            test.expect(ping)
            ping_summary = re.search(r".*Lost = (\d+) .*", ping)
            if int(ping_summary.group(1)) < 4:
                test.log.info("Packets losses are less than 10%")
                test.expect(True)
            else:
                test.log.error("Packets losses are greater than 10%")
                test.expect(False)
            test.log.step("9. Restart module")
            dstl_stop_public_ipv4_data_connection_over_dialup(test.dut, test, dialup_name)
            test.sleep(5)
            test.expect(test.dut.at1.send_and_verify("ATE1", ".*OK.*"))
            test.expect(dstl_restart(test.dut))
            if mtu != "1280":
                test.log.step("10. Repeat step 2-8 using <mtusize>=1280")
            test.log.info("NOTE: For standard MTU of 1500 bytes, the maximum data size is 1472 bytes (MTU minus 20 "
                          "bytes IP header and 8 bytes for the ICMP header).")


    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"GPRS/MTU/Size\",\"1430\"", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))


if "__main__" == __name__:
    unicorn.main()
