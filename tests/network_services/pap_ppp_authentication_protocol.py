# responsible: dariusz.drozdek@globallogic.com
# location: Wroclaw
# TC0081871.002

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.packet_domain.start_public_IPv4_data_connection import dstl_start_public_ipv4_data_connection_over_dialup, \
    dstl_stop_public_ipv4_data_connection_over_dialup


class Test(BaseTest):
    """TC0081871.002    PAP_PPP Authentication Protocol

    The module should be able to set up GPRS session when PAP.

    1.Set type of authentication:
        at^sgauth=1,1,"user","passwd"
    2. Define PDP context:
        at+cgdcont=1,"IP","your provider APN"
    3. Set up GPRS DialUp connection

    Please note, that all settings should be put in Device Manager for modem, to be sure that all settings are loaded.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", "OK"))

    def run(test):
        #dialup_name = "DUN_PEGASUS"
        test.log.step("1.Set type of authentication: at^sgauth=1,1,\"user\",\"passwd\"")
        test.expect(test.dut.at1.send_and_verify("AT^SGAUTH=1,1,\"user\",\"passwd\"", ".*OK.*"))

        test.log.step("2. Define PDP context: at+cgdcont=1,\"IP\",\"your provider APN\"")
        test.expect(
            test.dut.at1.send_and_verify("AT+CGDCONT=1,\"IP\",\"{}\"".format(test.dut.sim.apn_v4), ".*OK.*"))

        test.log.step("3. Set up GPRS DialUp connection \n"
                      "Please note, that all settings should be put in Device Manager for modem, to be sure that "
                      "all settings are loaded.")
        test.expect(dstl_start_public_ipv4_data_connection_over_dialup(test.dut, test, test.dialup_conn_name))
        test.sleep(10)  # 10 timeout for working dialup
        dstl_stop_public_ipv4_data_connection_over_dialup(test.dut, test, test.dialup_conn_name)
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("ATE1", ".*OK.*"))

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT^SGAUTH=1", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))


if "__main__" == __name__:
    unicorn.main()
